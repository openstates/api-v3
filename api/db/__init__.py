import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://")
"""
From https://docs.sqlalchemy.org/en/14/core/pooling.html
Default pool/overflow size is 5/10, timeout 30 seconds

max_overflow=15 - the number of connections to allow in connection pool “overflow”,
    that is connections that can be opened above and beyond the pool_size setting,
    which defaults to five. this is only used with QueuePool.

pool_size=10 - the number of connections to keep open inside the connection pool.
    This used with QueuePool as well as SingletonThreadPool.
    With QueuePool, a pool_size setting of 0 indicates no limit; to disable pooling,
    set poolclass to NullPool instead.

pool_timeout=30 - number of seconds to wait before giving up on getting a connection from the pool.
    This is only used with QueuePool. This can be a float but is subject to the limitations of
    Python time functions which may not be reliable in the tens of milliseconds.

pool_recycle=28800 - this setting causes the pool to recycle connections after the given number
    of seconds has passed. It defaults to -1, or no timeout. For example, setting to 3600 means
    connections will be recycled after one hour. Note that MySQL in particular will disconnect
    automatically if no activity is detected on a connection for eight hours
    (although this is configurable with the MySQLDB connection itself and the server configuration as well).
"""
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=7,
    pool_timeout=45,
    pool_recycle=7200,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
