from django.urls import path
from api import endpoints

urlpatterns = [
    path("people/", endpoints.PeopleEndpoint().as_django_view())
]
