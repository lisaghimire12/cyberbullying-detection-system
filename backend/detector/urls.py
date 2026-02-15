from django.urls import path
from . import views

urlpatterns = [

    # Home Page
    path("", views.home),

    # YouTube Link Analyzer API
    path("api/analyze-link/", views.analyze_link),

]
