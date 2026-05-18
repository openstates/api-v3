import os
import datetime
import typing
from dataclasses import dataclass
from redis import Redis


@dataclass
class Tier:
    name: str
    per_minute: int
    per_hour: int
    per_day: int


@dataclass
class DailyUsage:
    date: datetime.date
    calls: int


class RateLimitExceeded(Exception):
    pass


def _get_redis_connection() -> Redis:
    host = os.environ.get("RRL_REDIS_HOST", "localhost")
    port = int(os.environ.get("RRL_REDIS_PORT", 6379))
    db = int(os.environ.get("RRL_REDIS_DB", 0))
    return Redis(host=host, port=port, db=db)


class V3RateLimiter:
    """
    <prefix>:<key>:<hour><minute>         expires in 2 minutes
    <prefix>:<key>:<hour>                 expires in 2 hours
    <prefix>:<key>:<day>                  never expires
    """

    def __init__(
        self,
        tiers: typing.List[Tier],
        *,
        prefix: str = "",
        use_redis_time: bool = True,
        track_daily_usage: bool = True,
    ):
        self.redis = _get_redis_connection()
        self.tiers = {tier.name: tier for tier in tiers}
        self.prefix = prefix
        self.use_redis_time = use_redis_time
        self.track_daily_usage = track_daily_usage

    def check_limit_and_increment_counters(self, key: str, tier_name: str) -> bool:
        try:
            tier = self.tiers[tier_name]
        except KeyError:
            raise ValueError(f"unknown tier: {tier_name}")
        if self.use_redis_time:
            timestamp = self.redis.time()[0]
            now = datetime.datetime.fromtimestamp(timestamp)
        else:
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        # check AND increment usage counters
        pipe = self.redis.pipeline()
        day = now.strftime("%Y%m%d")
        day_key = f"{self.prefix}:{key}:d{day}"
        day_requests_key = f"{self.prefix}:{key}:dr{day}"
        if tier.per_minute:
            minute_key = f"{self.prefix}:{key}:m{now.minute}"
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
        if tier.per_hour:
            hour_key = f"{self.prefix}:{key}:h{now.hour}"
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
        if tier.per_day or self.track_daily_usage:
            # Keep separate day and day-requests keys
            # day key: used for aggregate usage tracking, so we want to limit this to
            # track allowed requests the user has used
            # day-requests key: tracking how many TOTAL (incl blocked) requests made
            pipe.incr(day_key)
            pipe.incr(day_requests_key)
            # keep data around for usage tracking
            if not self.track_daily_usage:
                pipe.expire(day_key, 86400)
                pipe.expire(day_requests_key, 86400)
        result = pipe.execute()

        # parse redis pipeline results
        # the result is pairs of results of incr and expire calls, so if all 3 limits are set
        # it looks like [per_minute_calls, True, per_hour_calls, True, per_day_allowed_calls, per_day_raw_calls]
        # we increment value_pos as we consume values so we know which location we're looking at
        value_pos = 0
        minute_calls = hour_calls = day_calls = 0
        minute_exceeded = hour_exceeded = day_exceeded = False
        if tier.per_minute:
            minute_calls = result[value_pos]
            if result[value_pos] > tier.per_minute:
                minute_exceeded = True
            value_pos += 2
        if tier.per_hour:
            hour_calls = result[value_pos]
            if result[value_pos] > tier.per_hour:
                hour_exceeded = True
            value_pos += 2
        if tier.per_day:
            # report back the # of raw requests, not just allowed requests
            day_calls = result[value_pos + 1]
            if result[value_pos] > tier.per_day:
                day_exceeded = True
                # daily usage numbers are used to report overall usage
                # so actually want to decrement back to the prior value
                # otherwise the usage count for the day will include all *blocked* requests
                self.redis.decr(day_key)

        # Raise appropriate exception if limit exceeded
        if minute_exceeded:
            raise RateLimitExceeded(
                f"exceeded limit of {tier.per_minute}/min: {minute_calls}"
            )
        if hour_exceeded:
            raise RateLimitExceeded(
                f"exceeded limit of {tier.per_hour}/hour: {hour_calls}"
            )
        if day_exceeded:
            raise RateLimitExceeded(
                f"exceeded limit of {tier.per_day}/day: {day_calls}"
            )

        return True

    def get_usage_since(
        self,
        key: str,
        start: datetime.date,
        end: typing.Optional[datetime.date] = None,
    ) -> typing.List[DailyUsage]:
        if not self.track_daily_usage:
            raise RuntimeError("track_daily_usage is not enabled")
        if not end:
            end = datetime.date.today()
        days = []
        day = start
        while day <= end:
            days.append(day)
            day += datetime.timedelta(days=1)
        day_keys = [f"{self.prefix}:{key}:d{day.strftime('%Y%m%d')}" for day in days]
        return [
            DailyUsage(d, int(calls.decode()) if calls else 0)
            for d, calls in zip(days, self.redis.mget(day_keys))
        ]
