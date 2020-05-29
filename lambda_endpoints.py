import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

django.setup()

from api import endpoints
legislators = endpoints.LegislatorEndpoint().as_lambda_handler()
