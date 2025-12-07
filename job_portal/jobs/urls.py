from django.urls import path
from . import views

urlpatterns = [
    path('job_list/', views.job_list, name='job_list'),
    path('post/', views.post_job, name='post_job'),
    path('edit_job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('job_detail/<int:job_id>/', views.job_detail, name='job_detail'),
    path('apply_for_job/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('browse_all_jobs/', views.browse_all_jobs, name='browse_all_jobs'),
    path('jobs_search/', views.job_search, name='job_search'),
    path('job_details_view/<int:job_id>/details/', views.job_details_view, name='job_details_view'),
    path('application/<int:application_id>/update_status/', views.update_application_status, name='update_application_status'),
    path('application/<int:application_id>/interview/', views.open_interview_modal, name='open_interview_modal'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_wishlist/<int:job_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:job_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('repost_job/<int:job_id>/', views.repost_job, name='repost_job'),
    path('change_plan/<str:new_plan>/', views.change_plan, name='change_plan'),
    path('subscription/', views.subscription, name='subscription'),
    path('application/feedback/<int:application_id>/', views.feedback_page, name='feedback_page'),
    path('pay/<str:plan>/', views.pay_subscription, name='pay_subscription'),
    path('payment-success/',views.payment_success,name="payment_success"),
]
