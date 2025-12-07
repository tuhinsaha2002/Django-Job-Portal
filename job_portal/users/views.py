from datetime import date, timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from resume.utils import calculate_ats_score
from .forms import ApplicantSignUpForm, ApplicantProfileForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Applicant
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import Application, Job
from .models import CustomUser, Subscription
from django.core.exceptions import ValidationError
import PyPDF2
from docx import Document
from django.utils.html import escape
import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Applicant, Skill
from .forms import ApplicantProfileForm
from .models import Applicant, ProfileView
from jobs.models import Wishlist

def is_ats_compliant(file):
    """
    Perform an ATS compliance scan on the provided file. Checks for the presence of
    required sections and validates that the resume contains the necessary information.
    """

    # Define a list of essential ATS keywords
    required_keywords = [
        "EDUCATION", "SKILLS", "CERTIFICATION", "PROJECTS",
    ]

    # Try to extract text from the PDF file
    if file.name.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() for page in pdf_reader.pages])
        except Exception as e:
            raise ValidationError(f"Could not read the PDF file: {escape(str(e))}")
    
    # Try to extract text from the DOCX file
    elif file.name.endswith('.docx'):
        try:
            doc = Document(file)
            text = " ".join([p.text for p in doc.paragraphs])
        except Exception as e:
            raise ValidationError(f"Could not read the DOCX file: {escape(str(e))}")
    
    # Raise an error if the file is not PDF or DOCX
    else:
        raise ValidationError("Only PDF and DOCX files are supported.")

    # Check if text is long enough (minimal content requirement)
    if len(text.strip()) < 100:
        raise ValidationError("The resume is too short. It must contain enough details.")

    # Convert the text to uppercase for case-insensitive comparison
    text_upper = text.upper()

    # Check if all required keywords are present in the text
    missing_keywords = [keyword for keyword in required_keywords if keyword not in text_upper]
    if missing_keywords:
        raise ValidationError(f"The resume is missing the following required sections: {', '.join(missing_keywords)}")

    # Validate if the resume contains a phone number (simple 10-digit check)
    if not re.search(r"\b\d{10}\b", text):
        raise ValidationError("Resume is missing a phone number. Please include a valid 10-digit phone number.")

    # Validate if the resume contains an email address (basic pattern check)
    if not re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b", text):
        raise ValidationError("Resume is missing an email address. Please include a valid email address.")

    return True

def home(request):
    return render(request, 'home.html') 

def applicant_signup(request):
    if request.method == 'POST':
        form = ApplicantSignUpForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 != password2:
                messages.error(request, "Passwords do not match. Please try again.")
                return render(request, 'users/applicant_signup.html', {'form': form})
            
            user = form.save(commit=False)
            user.set_password(password1)
            user.save()
            Applicant.objects.create(user=user)
            messages.success(request, 'You have successfully signed up! Please log in with your username and password.')
            return redirect('applicant_login')
        else:
            messages.error(request, 'There was an error with your signup. Please check the form and try again.')
    else:
        form = ApplicantSignUpForm()

    return render(request, 'users/applicant_signup.html', {'form': form})

def applicant_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.role == CustomUser.APPLICANT:
                    login(request, user)
                    applicant = user.applicant
                    if not applicant.dob or not applicant.address or not applicant.resume:
                        return redirect('applicant_profile')
                    return redirect('applicant_dashboard')
                else:
                    messages.error(request, "You don't have an applicant account. Please log in as a company.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/applicant_login.html', {'form': form})


def extract_skills_from_resume(resume_file, predefined_skills):
    reader = PyPDF2.PdfReader(resume_file)
    text = " ".join(page.extract_text() for page in reader.pages).lower()
    return {skill for skill in predefined_skills if skill.name.lower() in text}


@login_required
def applicant_profile(request):
    applicant = request.user.applicant
    predefined_skills = Skill.objects.all()

    if request.method == 'POST':
        form = ApplicantProfileForm(request.POST, request.FILES, instance=applicant)

        if request.FILES.get('resume'):
            try:
                # Calculate ATS score for the uploaded resume
                is_ats_compliant(request.FILES['resume'])
                ats_score = calculate_ats_score(request.FILES['resume'])
                applicant.ats_score = ats_score

                # Extract skills based on the resume
                extracted_skills = extract_skills_from_resume(request.FILES['resume'], predefined_skills)
                applicant.skills.set(extracted_skills)  # Update skills via Many-to-Many field
            except ValidationError as ve:
                form.add_error('resume',ve)

        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.save()

            form.save()
            applicant.save()
            messages.success(request, "Your profile has been successfully updated.")
            return redirect('applicant_dashboard')
    else:
        form = ApplicantProfileForm(instance=applicant)
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
        form.fields['email'].initial = request.user.email

    return render(request, 'users/applicant_profile.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

from django.contrib import messages

@login_required
def applicant_dashboard(request):
    applicant = request.user.applicant
    saved_jobs_count = Wishlist.objects.filter(user=applicant).count() 
    applied_jobs_count = Application.objects.filter(applicant=applicant).count() 
    ats_score = applicant.ats_score or 0

    # Ensure the applicant has a subscription
    subscription, created = Subscription.objects.get_or_create(
        applicant=applicant,
        defaults={
            'plan': 'Free',
            'expiry_date': None,
            'remaining_applications': 3,
            'applications_used': 0,
            'last_reset_date': date.today(),
        }
    )

    # Reset remaining applications if needed
    if created or subscription.needs_reset():
        subscription.reset_remaining_applications()

    # Ensure the user cannot downgrade to Free if the current subscription is active
    if subscription.is_active() and subscription.plan != 'Free':
        subscription.plan = subscription.plan  # Maintain current plan
    elif not subscription.is_active():
        messages.info(
            request,
            "You are on a Free Plan"
        )

    # Recommended jobs based on location
    recommended_jobs = Job.objects.filter(location=applicant.location)

    # Pass the context to the template
    context = {
        'applicant': applicant,
        'subscription': subscription,
        'recommended_jobs': recommended_jobs,
        'applications_remaining': subscription.remaining_applications,
        'expiration_date': subscription.expiry_date,
        'last_reset_date': subscription.last_reset_date,  # Include last reset date
        'saved_jobs_count': saved_jobs_count,
        'applied_jobs_count': applied_jobs_count,
        'ats_score': ats_score,
    }

    return render(request, 'users/applicant_dashboard.html', context)


@login_required
def profile(request):
    applicant_profile = get_object_or_404(Applicant, user=request.user)
    return render(request, 'users/profile.html', {'applicant_profile': applicant_profile})

@login_required
def company_views(request):
    # Check if the logged-in user is an applicant
    if not request.user.role == 'APPLICANT':
        return redirect('dashboard')  # Redirect to dashboard if not an applicant

    # Get all the companies that viewed this applicant's profile
    profile_views = ProfileView.objects.filter(viewed_applicant__user=request.user).select_related('viewed_by_company')

    context = {
        'profile_views': profile_views,
    }
    return render(request, 'users/company_view.html', context)

@login_required
def delete_company_view(request, view_id):
    # Ensure the user is an applicant and the view exists
    if not request.user.role == 'APPLICANT':
        return redirect('dashboard')  # Redirect if not an applicant

    profile_view = get_object_or_404(ProfileView, id=view_id, viewed_applicant__user=request.user)

    # Delete the view
    profile_view.delete()

    # Redirect back to the company views page
    return redirect('company_views')



@login_required
def delete_applicant_profile(request):
    if request.method == "POST":
        applicant = request.user.applicant
        user = request.user
        applicant.delete()
        user.delete()
        return redirect('home')
    return redirect('applicant_dashboard')

@login_required
def withdraw_application(request, application_id):
    try:
        application = Application.objects.get(id=application_id, applicant=request.user.applicant)
        application.delete()
        messages.success(request, "Your application has been withdrawn.")
    except Application.DoesNotExist:
        messages.error(request, "You don't have permission to withdraw this application.")
    return redirect('applied_jobs')

@login_required
def edit_profile(request):
    # Get the applicant instance related to the logged-in user
    applicant = request.user.applicant
    predefined_skills = Skill.objects.all()

    if request.method == 'POST':
        # Create a form instance with the POST data and the current applicant instance
        form = ApplicantProfileForm(request.POST, request.FILES, instance=applicant)

        # Perform ATS score calculation and skill extraction if a resume is uploaded
        if request.FILES.get('resume'):
            try:
                # Calculate ATS score for the uploaded resume
                is_ats_compliant(request.FILES['resume'])
                ats_score = calculate_ats_score(request.FILES['resume'])
                applicant.ats_score = ats_score

                # Extract skills based on the resume
                extracted_skills = extract_skills_from_resume(request.FILES['resume'], predefined_skills)
                applicant.skills.set(extracted_skills)  # Update skills via Many-to-Many field
            except ValidationError as ve:
                form.add_error('resume', ve)

        if form.is_valid():
            # Update the user's first and last names
            user = request.user
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.save()

            # Save the form and applicant instance
            form.save()
            applicant.save()

            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('applicant_dashboard')  # Redirect to the dashboard after saving
        else:
            messages.error(request, 'There were some errors with your form. Please check again.')
    else:
        # Create a form instance for the GET request
        form = ApplicantProfileForm(instance=applicant)

    return render(request, 'users/edit_profile.html', {'form': form})




@login_required
def applied_jobs(request):
    if request.user.is_authenticated:
        applicant_profile = getattr(request.user, 'applicant', None)
        
        if applicant_profile:
            applications = Application.objects.filter(applicant=applicant_profile)
            jobs = [application.job for application in applications]
            
            return render(request, 'users/applied_jobs.html', {'jobs': jobs, 'applications': applications})
        else:
            return render(request, 'users/applied_jobs.html', {'error': 'No applicant profile found.'})
    else:
        return redirect('login')
    
@login_required
def job_info(request, job_id):
    # If the user is not authenticated, redirect them to the login page
    if not request.user.is_authenticated:
        return redirect('applicant_login')
    
    # Fetch the job object
    job = get_object_or_404(Job, id=job_id)
    
    # Check if the logged-in user has already applied for the job
    application = Application.objects.filter(job=job, applicant__user=request.user).first()

    context = {
        'job': job,
        'has_applied': application is not None,
        'application_status': application.status if application else None,
    }
    
    return render(request, 'users/job_info.html', context)


@login_required
def my_subscription(request):
    try:
        applicant = request.user.applicant
        subscription = get_object_or_404(Subscription, applicant=applicant)

        context = {
            'subscription': subscription,
            'change_plan_url': 'subscription',  # URL name for subscription view
            'expiry_date': subscription.get_expiry_date(),  # Dynamically calculated expiry date
        }
        return render(request, 'users/my_subscription.html', context)
    except AttributeError:
        messages.error(request, "No subscription found for this user.")
        return redirect('home')  # Redirect to an appropriate page


from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib import messages
from .forms import OTPRequestForm, OTPVerifyForm, PasswordResetForm
from .models import Applicant, Company

User = get_user_model()

def request_otp(request):
    if request.method == "POST":
        form = OTPRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = user.generate_otp()
                send_mail(
                    'Your OTP Code',
                    f'Your OTP is {otp}. It is valid for 10 minutes.',
                    'your_email@gmail.com',
                    [email],
                )
                # Determine account type (Applicant or Company)
                if Applicant.objects.filter(user=user).exists():
                    account_type = "Applicant"
                else:
                    account_type = "Company"

                # Save the account type in the session to use it in the verify_otp view
                request.session['account_type'] = account_type

                messages.success(request, f"OTP sent to your email. (Account Type: {account_type})")
                return redirect('verify_otp', user_id=user.id)
            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
    else:
        form = OTPRequestForm()
    return render(request, 'users/request_otp.html', {'form': form})


def verify_otp(request, user_id):
    user = User.objects.get(id=user_id)
    account_type = request.session.get('account_type', 'Unknown')  # Get account type from session
    
    if request.method == "POST":
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if user.verify_otp(otp):
                messages.success(request, f"OTP verified. ({account_type}) Reset your password now.")
                return redirect('reset_password', user_id=user.id)
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPVerifyForm()
    
    return render(request, 'users/verify_otp.html', {'form': form, 'account_type': account_type})


def reset_password(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successful.")
                # Redirect based on the account type
                if Applicant.objects.filter(user=user).exists():
                    return redirect('applicant_login')
                else:
                    return redirect('company_login')
            else:
                messages.error(request, "Passwords do not match.")
    else:
        form = PasswordResetForm()
    return render(request, 'users/reset_password.html', {'form': form})






# def applicant_login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
            
#             if user is not None:
#                 try:
#                     applicant = user.applicant
#                     login(request, user)  # Log in the user
#                     # Check if the applicant profile is complete
#                     if not applicant.dob or not applicant.address:
#                         return redirect('applicant_profile')  # Redirect to complete profile if it's not complete
#                     return redirect('applicant_dashboard')  # Redirect to the dashboard if profile is complete
#                 except Applicant.DoesNotExist:
#                     messages.error(request, "You are not registered as an applicant.")
#             else:
#                 messages.error(request, "Invalid username or password.")
#         else:
#             messages.error(request, "Invalid username or password.")
#     else:
#         form = AuthenticationForm()
    
#     return render(request, 'users/applicant_login.html', {'form': form})
