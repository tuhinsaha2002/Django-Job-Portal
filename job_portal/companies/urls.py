from django.urls import path
from . import views

urlpatterns = [
    path('company_signup/', views.company_signup, name='company_signup'),
    path('company_login/', views.company_login, name='company_login'),
    path('company_profile/', views.company_profile, name='company_profile'),
    path('company_dashboard/', views.company_dashboard, name='company_dashboard'),
    path('delete_company_profile/', views.delete_company_profile, name='delete_company_profile'), 
    path('application_detail/<int:application_id>/', views.application_detail, name='application_detail'),
    path('job-applicants/', views.job_applicants, name='job_applicants'),
    path('applicant/<int:applicant_id>/schedule_interview/', views.schedule_interview, name='schedule_interview'),
    path('applicant/<int:applicant_id>/', views.company_view_applicant_profile, name='company_view_applicant_profile'),
]
    
