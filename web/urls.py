from django.urls import path
from api import endpoints

urlpatterns = [
    path("legislators/", endpoints.LegislatorEndpoint().as_django_view())
]
