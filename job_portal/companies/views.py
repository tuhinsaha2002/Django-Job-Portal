from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CompanySignUpForm, CompanyProfileForm
from .models import Company
from django.contrib.auth.decorators import login_required
from jobs.models import Job, Application
from users.models import CustomUser, Applicant, Skill
from django.core.mail import send_mail
from django.conf import settings
from .forms import JobApplicationForm
from users.models import Applicant
from jobs.models import Application ,Job
from users.models import ProfileView

def company_signup(request):
    if request.method == 'POST':
        form = CompanySignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('company_profile')
    else:
        form = CompanySignUpForm()
    return render(request, 'companies/company_signup.html', {'form': form})

def company_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.role == CustomUser.COMPANY:
                login(request, user)
                try:
                    company = Company.objects.get(owner=request.user)
                    if not company.company_name or not company.description:
                        return redirect('company_profile')
                    return redirect('company_dashboard')
                except Company.DoesNotExist:
                    return redirect('company_profile')
            else:
                messages.error(request, "You don't have a company account. Please log in as an applicant.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'companies/company_login.html')

@login_required
def company_profile(request):
    # Fetch the Company instance if it exists
    company = Company.objects.filter(owner=request.user).first()

    # If no Company instance exists, prefill the email field with the user's email
    initial_data = {'email': request.user.email} if not company else {}

    if request.method == 'POST':
        # Handle form submission
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.owner = request.user  # Ensure the owner is set correctly
            profile.save()
            return redirect('company_dashboard')
    else:
        # Initialize the form with the existing company instance or initial email
        form = CompanyProfileForm(instance=company, initial=initial_data)

    return render(request, 'companies/company_profile.html', {'form': form})


@login_required
def company_dashboard(request):
    company = request.user.owned_companies.first()
    jobs = company.jobs.all()
    applications = Application.objects.filter(job__in=jobs) 

    if not company:
        messages.info(request, "You don't have a company profile. Please create one.")
        return redirect('company_profile')

    total_jobs = Job.objects.filter(company=company).count()
    total_applications = Application.objects.filter(job__company=company).count()

    context = {
        'company': company,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'applications': applications,
    }

    return render(request, 'companies/company_dashboard.html', context)

@login_required
def delete_company_profile(request):
    try:
        company = request.user.owned_companies.first()
        if company:
            company.delete()
            messages.success(request, "Your company profile has been deleted.")
            if not request.user.owned_companies.exists():
                return redirect('company_profile')
            else:
                return redirect('company_dashboard')
        else:
            messages.error(request, "You do not have a company profile to delete.")
            return redirect('company_dashboard')
    except Company.DoesNotExist:
        messages.error(request, "You do not have a company profile to delete.")
        return redirect('company_dashboard')

@login_required
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    applicant = application.applicant

    if request.method == "POST":
        status = request.POST.get("status")
        if status in ["Pending", "Accepted", "Rejected"]:
            application.status = status
            application.save()
            messages.success(request, f"Application status updated to {status}.")
            return redirect('application_detail', application_id=application.id)
        else:
            messages.error(request, "Invalid status selected.")

    context = {
        'applicant': applicant,
        'application': application,
    }
    return render(request, 'companies/application_detail.html', context)


# Applicant filter
@login_required
def job_applicants(request):
    search_query = request.GET.get('skills', '')
    applicants = Applicant.objects.all()

    if search_query:
        search_skills = [skill.strip().lower() for skill in search_query.split(',')]
        matching_skills = Skill.objects.filter(name__in=search_skills)
        applicants = applicants.filter(skills__in=matching_skills).distinct()

    return render(request, 'companies/job_applicants.html', {'applicants': applicants, 'search_query': search_query})

#Company side Interview scheduling
@login_required
def schedule_interview(request, applicant_id):
    company = request.user  # Assuming the user is logged in as a company owner
    applicant = get_object_or_404(Applicant, id=applicant_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, company=company)
        if form.is_valid():
            job = form.cleaned_data['job']
            interview_date = form.cleaned_data['interview_date']
            interview_venue = form.cleaned_data['interview_venue']

            # Create or update the application
            application, created = Application.objects.get_or_create(
                applicant=applicant,
                job=job,
                defaults={
                    'status': 'Shortlisted for Interview',
                    'interview_date': interview_date,
                    'interview_venue': interview_venue,
                }
            )
            if not created:
                application.status = 'Shortlisted for Interview'
                application.interview_date = interview_date
                application.interview_venue = interview_venue
                application.save()

            # Send email to applicant
            send_mail(
                'Interview Scheduled',
                f'You have been shortlisted for an interview.\n\nDetails:\nJob: {job.title}\nDate: {interview_date}\nVenue: {interview_venue}',
                settings.DEFAULT_FROM_EMAIL,
                [applicant.user.email]
            )

            return redirect('job_applicants')  # Redirect to a success page or applicant list
    else:
        form = JobApplicationForm(company=company)

    return render(request, 'companies/schedule_interview.html', {'form': form, 'applicant': applicant})


# To view applicants profile
@login_required
def company_view_applicant_profile(request, applicant_id):
    # Get the applicant profile
    applicant_profile = get_object_or_404(Applicant, id=applicant_id)
    
    # Get the company from the logged-in user
    company = get_object_or_404(Company, owner=request.user)
    
    # Check if the company has already viewed the profile
    profile_view, created = ProfileView.objects.get_or_create(
        viewed_applicant=applicant_profile,
        viewed_by_company=company
    )
    
    if not created:
        # If the view already exists, update the viewed_at timestamp or any other logic (e.g., increase view count)
        profile_view.viewed_at = timezone.now()
        profile_view.save()
    
    return render(request, 'companies/company_applicant_profile.html', {'applicant_profile': applicant_profile})