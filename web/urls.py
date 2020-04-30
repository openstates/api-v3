from django.urls import path
from api import views

urlpatterns = [
    path("legislators/", views.legislators)
]
