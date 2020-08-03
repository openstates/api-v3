from django.urls import path
from api import endpoints

urlpatterns = [
    path("jurisdictions/", endpoints.JurisdictionEndpoint().as_django_view()),
    path("people/", endpoints.PeopleEndpoint().as_django_view())
]
