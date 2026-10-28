from django.urls import path
from . import views

urlpatterns = [
    path("", views.scheme_list, name="scheme_list"),
    path("<slug:slug>/", views.scheme_detail, name="scheme_detail"),
]