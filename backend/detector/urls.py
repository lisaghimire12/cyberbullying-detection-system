from django.urls import path
from . import views

urlpatterns = [

    # Home Page
    path("", views.home),

    # YouTube Link Analyzer API
    path("api/analyze-link/", views.analyze_link),
    
    #To print harmful comments
    path("api/download-report/", views.download_report),


]
