from django.urls import path
from . import views

urlpatterns = [
   path('upload/', views.score_resume, name='score_resume'),
   path('job-based-ats/', views.job_based_ats, name='job_based_ats'),
]
