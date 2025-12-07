from datetime import date, timedelta, timezone
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from users.models import Applicant
from .models import Job,Wishlist
from .forms import JobForm, ApplicationForm
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404
from .models import Job, Application
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render
from django.http import JsonResponse
from razorpay import Client
from django.conf import settings



@login_required
def job_list(request):
    company = request.user.owned_companies.first()

    if not company:
        messages.info(request, "You need to create a company profile before accessing job listings.")
        return redirect('company_profile')

    # Check expiry for each job
    jobs = Job.objects.filter(company=company).order_by('-created_at')

    # Optionally mark jobs as expired (if not already done)
    for job in jobs:
        job.check_expiry()

    # Filter expired jobs (optional)
    active_jobs = jobs.filter(is_active=True)

    paginator = Paginator(active_jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'jobs': page_obj,
        'company': company,
        'paginator': paginator,
    }

    return render(request, 'jobs/job_list.html', context)


@login_required
def post_job(request):
    company = request.user.owned_companies.first()
    if not company:
        messages.info(request, "You need to create a company profile before posting jobs.")
        return redirect('company_profile')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.save()
            messages.success(request, "Job posted successfully.")
            return redirect('job_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def edit_job(request, job_id):
    # Retrieve the job based on its ID
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        # If the form is submitted, process the form with the existing data
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()  # Save the updated job data
            return redirect('job_detail', job_id=job.id)  # Redirect to the job detail page or another appropriate page
    else:
        # If the form is not submitted, render the form with existing job data
        form = JobForm(instance=job)
    
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.owned_companies.first())
    
    if request.user != job.company.owner:
        messages.error(request, "You are not authorized to delete this job.")
        return redirect('job_list')

    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('job_list')

@login_required
def repost_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.owned_companies.first())

    if job.is_expired:
        # Create a new job with the same data, resetting the expiry date
        new_job = Job.objects.create(
            company=job.company,
            title=job.title,
            description=job.description,
            location=job.location,
            salary=job.salary,
            created_at=timezone.now(),  # Reset the creation date
            expiry_date=timezone.now() + timezone.timedelta(days=30)  # Set a new expiry date (30 days for example)
        )
        messages.success(request, 'Job reposted successfully!')
        return redirect('job_list')  # Redirect to the job list page
    else:
        messages.error(request, 'This job cannot be reposted because it is not expired.')
        return redirect('job_list')


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def job_details_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    selected_status = request.GET.get('status', 'ALL')

    # Handle status update
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        if application_id and new_status:
            application = get_object_or_404(Application, id=application_id, job=job)
            if new_status in [choice[0] for choice in Application._meta.get_field('status').choices]:
                application.status = new_status
                application.save()
                # Redirect to the same page with the current filter to refresh
                return redirect(f"{request.path}?status={selected_status}")

    # Filter applications based on selected status
    if selected_status == 'ALL':
        applications = job.applications.all()
    else:
        applications = job.applications.filter(status=selected_status)

    context = {
        'job': job,
        'applications': applications,
        'selected_status': selected_status,
    }
    return render(request, 'jobs/company_job_details.html', context)

@login_required
def update_application_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(Application, id=application_id)
        new_status = request.POST.get('status')

        if new_status in [choice[0] for choice in Application._meta.get_field('status').choices]:
            application.status = new_status
            
            application.save() 
            
            if new_status == 'Rejected':
                application.save()  # Save the application status
                return redirect('feedback_page', application_id=application.id)  # Redirect to feedback page


            if new_status == 'Accepted':
                send_mail(
                    'Job Application Accepted',
                    'Your job application has been accepted.',
                    settings.DEFAULT_FROM_EMAIL,
                    [application.applicant.user.email]
                )
            elif new_status == 'Shortlisted for Interview':
                return redirect('open_interview_modal', application_id=application.id)
            
            elif new_status == 'Reviewed':
                send_mail(
                    'Job Application Reviewed',
                    'Your job application has been reviewed.',
                    settings.DEFAULT_FROM_EMAIL,
                    [application.applicant.user.email]
                )

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def open_interview_modal(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        venue = request.POST.get('venue')
        interview_time = request.POST.get('interview_time')

        # Optionally save interview details to the application or a new model
        application.interview_venue = venue
        application.interview_date = interview_time
        application.save()

        # Send email with interview details
        send_mail(
            'Interview Scheduled',
            f'Your interview is scheduled at {venue} on {interview_time}.',
            settings.DEFAULT_FROM_EMAIL,
            [application.applicant.user.email]
        )

        return redirect('job_details_view', job_id=application.job.id)

    return render(request, 'jobs/interview_modal.html', {'application': application})

@login_required
def feedback_page(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.method == 'POST':
        feedback = request.POST.get('feedback')

        # Save the feedback to the application
        application.feedback = feedback
        application.save()

        # Render the feedback email template
        email_subject = 'Job Application Rejected'
        email_html_body = render_to_string(
            'jobs/feedback.html',  # Your feedback template
            {
                'applicant_name': application.applicant.user.username,
                'job_title': application.job.title,
                'feedback': feedback,
            }
        )
        email_text_body = strip_tags(email_html_body)  # Remove HTML tags for plain text

        # Send rejection email with feedback
        send_mail(
            email_subject,
            email_text_body,  # Use plain text body
            settings.DEFAULT_FROM_EMAIL,
            [application.applicant.user.email],
            fail_silently=False,
        )

        # Redirect to the job details view after sending the email
        return redirect('job_details_view', job_id=application.job.id)

    return render(request, 'jobs/feedback_form.html', {'application': application})


@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applicant = request.user.applicant
    subscription = applicant.subscription

    # Check if subscription is valid
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Please renew or upgrade your plan.")
        return redirect('subscription')

    # Ensure enough applications remaining
    if subscription.remaining_applications <= 0:
        messages.error(request, "You've reached your application limit for this month.")
        return redirect('subscription')

    # Prevent duplicate applications
    existing_application = Application.objects.filter(job=job, applicant=applicant).exclude(status='Rejected').first()
    if existing_application:
        messages.info(request, "You have already applied for this job.")
        return redirect('applied_jobs')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            experience = form.cleaned_data.get('experience')

            # Validate experience against job requirements
            if experience < job.min_experience or experience > job.max_experience:
                messages.error(request, f"This job requires {job.min_experience} - {job.max_experience} years of experience.")
                return redirect('apply_for_job', job_id=job.id)

            application = form.save(commit=False)
            application.job = job
            application.applicant = applicant

            # Automatically use the resume from the applicant's profile
            application.resume = applicant.resume
            application.save()

            # Deduct an application
            subscription.remaining_applications -= 1
            subscription.save()

            messages.success(request, "Your application has been submitted.")
            return redirect('applied_jobs')
    else:
        form = ApplicationForm()

    return render(request, 'jobs/apply_for_job.html', {'form': form, 'job': job, 'current_resume': applicant.resume})





@login_required
def change_plan(request, new_plan):
    applicant = request.user.applicant
    subscription = applicant.subscription

    # Check if the subscription is active and paid
    if subscription.is_active() and subscription.plan in ['499', '1200']:
        # Check if the current plan has expired before allowing changes
        if subscription.expiry_date > date.today():
            messages.error(request, "You cannot change your plan until the current plan expires.")
            return redirect('applicant_dashboard')

    # Handle switching plans
    if new_plan == 'Free':
        subscription.plan = 'Free'
        subscription.expiry_date = None
        subscription.remaining_applications = 3
    elif new_plan == '499':
        subscription.plan = '499'
        subscription.expiry_date = date.today() + timedelta(days=30)
        subscription.remaining_applications += 6
    elif new_plan == '1200':
        subscription.plan = '1200'
        subscription.expiry_date = date.today() + timedelta(days=30)
        subscription.remaining_applications += 12
    else:
        messages.error(request, "Invalid plan selected.")
        return redirect('applicant_dashboard')

    subscription.save()
    if new_plan == 'Free':
        pass  # No success message for free plan change
    else:
        messages.success(request, f"Plan changed to {new_plan} successfully.")
    return redirect('applicant_dashboard')

@login_required
def subscription(request):
    applicant = request.user.applicant
    subscription = applicant.subscription

    if request.method == "POST":
        new_plan = request.POST.get('subscription_plan')

        if new_plan != subscription.plan:
            return redirect('change_plan', new_plan=new_plan)
        
        if new_plan == "Free":
            # Update to free plan without payment
            subscription.plan = "Free"
            subscription.save()
            messages.success(request, "You have successfully switched to the Free Plan!")
            return redirect('subscription')
        else:
            # Redirect to payment gateway for paid plans
            return redirect('pay_subscription', plan=new_plan)

    context = {
        'subscription': subscription,
        'razorpay_key': settings.RAZORPAY_API_KEY
    }
    return render(request, 'jobs/subscription.html', context)

@login_required
def browse_all_jobs(request):
    # Get the filter values from GET request
    job_type = request.GET.get('job_type')
    experience = request.GET.get('experience')
    location = request.GET.get('location')
    salary_range = request.GET.get('salary_range')
    category = request.GET.get('category')  # New filter for category

    # Start with all jobs
    jobs = Job.objects.all()

    # Filter by job type
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    # Filter by experience level
    if experience:
        if experience == '0-2':  # 0-2 years of experience
            jobs = jobs.filter(min_experience__lte=2)
        elif experience == '3-5':  # 3-5 years of experience
            jobs = jobs.filter(Q(min_experience__lte=5) & Q(max_experience__gte=3))
        elif experience == '6+':  # 6+ years of experience
            jobs = jobs.filter(min_experience__gte=6)
    
    # Filter by location
    if location:
        jobs = jobs.filter(location=location)

    # Filter by salary range
    if salary_range:
        if salary_range == '0-3':
            jobs = jobs.filter(max_salary__gte=0, min_salary__lte=3)
        elif salary_range == '3-5':
            jobs = jobs.filter(max_salary__gte=3, min_salary__lte=5)
        elif salary_range == '5-10':
            jobs = jobs.filter(max_salary__gte=5, min_salary__lte=10)
        elif salary_range == '10+':
            jobs = jobs.filter(max_salary__gte=10)

    # Filter by category
    if category:
        jobs = jobs.filter(category=category)  # Filter by category

    # Get unique locations for the location filter dropdown
    unique_locations = Job.LOCATION_CHOICES  # Assuming this is predefined
    # Get unique categories for the category filter dropdown
    unique_categories = Job.CATEGORY_CHOICES  # Assuming this is predefined

    # Fetch the current user's Applicant instance
    applicant = Applicant.objects.get(user=request.user)

    # Get the user's wishlist to check if the job is already wishlisted
    user_wishlisted_jobs = Wishlist.objects.filter(user=applicant).values_list('job_id', flat=True)

    return render(
        request,
        'jobs/browse_all_jobs.html',
        {
            'jobs': jobs,
            'unique_locations': unique_locations,
            'unique_categories': unique_categories,  # Add unique categories to context
            'user_wishlisted_jobs': user_wishlisted_jobs,
            'selected_job_type': job_type,
            'selected_experience': experience,
            'selected_location': location,
            'selected_salary_range': salary_range,
            'selected_category': category,  # Track selected category
        }
    )



def job_search(request):
    query = request.GET.get('q', '')  # Get the search query from the URL parameters
    if query:
        # Normalize the query: convert to lowercase and remove extra spaces
        query_normalized = ''.join(query.lower().split())
        # Use Q objects to create a case-insensitive filter and ignore spaces
        jobs = Job.objects.filter(
            Q(title__icontains=query_normalized) |
            Q(title__icontains=query.replace(' ', ''))
        )
    else:
        jobs = Job.objects.all()  # If no query, show all jobs
    return render(request, 'jobs/job_search_results.html', {
        'jobs': jobs,
        'query': query,
    })

@login_required
def add_to_wishlist(request, job_id):
    applicant = Applicant.objects.get(user=request.user)
    job = Job.objects.get(id=job_id)

    # Check if the job is already in the wishlist
    if Wishlist.objects.filter(user=applicant, job=job).exists():
        messages.info(request, "This job is already in your wishlist!")
    else:
        Wishlist.objects.create(user=applicant, job=job)
        messages.success(request, f"Job '{job.title}' has been added to your wishlist!")

    return redirect('applicant_dashboard')

@login_required
def remove_from_wishlist(request, job_id):
    applicant = Applicant.objects.get(user=request.user)
    job = Job.objects.get(id=job_id)

    wishlist_entry = Wishlist.objects.filter(user=applicant, job=job)
    if wishlist_entry.exists():
        wishlist_entry.delete()
        messages.success(request, f"Job '{job.title}' has been removed from your wishlist!")
    else:
        messages.info(request, "This job is not in your wishlist.")

    return redirect('applicant_dashboard')


@login_required
def wishlist(request):
    applicant = Applicant.objects.get(user=request.user)
    wishlist_jobs = Job.objects.filter(wishlisted_by__user=applicant)  # Get jobs in the applicant's wishlist
    
    return render(request, 'jobs/wishlist.html', {
        'wishlist_jobs': wishlist_jobs,
    })
    

def pay_subscription(request, plan):
    razorpay_client = Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

    if plan == "499":
        amount = 49900  # ₹499 in paise
    elif plan == "1200":
        amount = 120000  # ₹1200 in paise
    else:
        messages.error(request, "Invalid plan selected!")
        return redirect('subscription')

    # Create an order in Razorpay
    order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": f"order_rcptid_{plan}",
        "payment_capture": 1
    })

    context = {
        "razorpay_key": settings.RAZORPAY_API_KEY,
        "payment": order,
        "plan": plan,
    }
    return render(request, "users/pay.html", context)



@login_required
def payment_success(request):
    payment_id = request.GET.get('payment_id', 'N/A')
    plan = request.GET.get('plan', 'N/A')

    # Ensure the payment was successful (add necessary validation for payment)
    if payment_id != 'N/A' and plan != 'N/A':
        # Call the change_plan function to update the subscription
        return change_plan(request, plan)

    messages.error(request, "Payment or plan details are missing.")
    return redirect('applicant_dashboard')
