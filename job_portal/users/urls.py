from django.urls import path
from users import views

urlpatterns = [
    path('applicant_signup/', views.applicant_signup, name='applicant_signup'),
    path('login/', views.applicant_login, name='applicant_login'),
    path('logout/', views.logout_view, name='logout'),
    path('applicant_profile/', views.applicant_profile, name='applicant_profile'),
    path('applicant_dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    path('delete_applicant_profile/', views.delete_applicant_profile, name='delete_applicant_profile'),
    path('withdraw_application/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('applied_jobs/', views.applied_jobs, name='applied_jobs'),
    path('job_info/<int:job_id>/', views.job_info, name='job_info'),
    path('profile/', views.profile, name='profile'),  # For applicants viewing their profile
    path('profile/views/', views.company_views, name='company_views'),
    path('delete-company-view/<int:view_id>/', views.delete_company_view, name='delete_company_view'),
    path('my-subscription/', views.my_subscription, name='my_subscription'),
    path('request-otp/', views.request_otp, name='request_otp'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),
]


   
