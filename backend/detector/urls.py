from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/predict/", views.predict),
    path("api/analyze-link/", views.analyze_link),
]
