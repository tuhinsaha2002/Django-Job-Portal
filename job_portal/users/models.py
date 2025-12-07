from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from pydantic import ValidationError
from calendar import monthrange
from django.utils.timezone import now, timedelta

class CustomUser(AbstractUser):
    APPLICANT = 'APPLICANT'
    COMPANY = 'COMPANY'

    ROLE_CHOICES = [
        (APPLICANT, 'Applicant'),
        (COMPANY, 'Company'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=APPLICANT)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        import random
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiration = now() + timedelta(minutes=10)
        self.save()
        return self.otp

    def verify_otp(self, otp):
        return self.otp == otp and now() <= self.otp_expiration

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Applicant(models.Model):
    LOCATION_CHOICES = [
        ('Mumbai', 'Mumbai'),
        ('Vasai', 'Vasai'),
        ('Pune', 'Pune'),
        ('Delhi', 'Delhi'),
        # Add more locations as needed
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    linkedin_profile = models.URLField(null=True, blank=True)
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, null=True, blank=True)  # Use choices here
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    ats_score = models.FloatField(null=True, blank=True)  # Add ATS score field

    def clean(self):
        if len(self.resume.name) > 200:
            raise ValidationError("Filename must be at most 200 characters.")
    
    def profile_view_count(self):
        return self.profile_views.count()

    def is_profile_complete(self):
        required_fields = [
            self.dob,
            self.address,
            self.phone_no,
            self.bio,
            self.linkedin_profile,
            self.location,
            self.profile_picture,
            self.resume,
        ]
        return all(required_fields)

    def __str__(self):
        return self.user.username

    
    
class Subscription(models.Model):
    FREE = 'Free'
    PLAN_499 = '499'
    PLAN_1200 = '1200'

    PLAN_CHOICES = [
        (FREE, 'Free'),
        (PLAN_499, '499 Rs/month'),
        (PLAN_1200, '1200 Rs/month'),
    ]

    applicant = models.OneToOneField('Applicant', on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=FREE)
    start_date = models.DateField(default=date.today)
    expiry_date = models.DateField(null=True, blank=True)
    remaining_applications = models.PositiveIntegerField(default=3)
    applications_used = models.PositiveIntegerField(default=0)  # Tracks used applications
    last_reset_date = models.DateField(default=date.today)  # Tracks the last reset date

    def is_active(self):
        today = date.today()

        if self.plan == self.FREE:
         # Free plan is active if within the current calendar month
            return self.last_reset_date.month == today.month and self.last_reset_date.year == today.year

        # Paid plans are active if expiry_date is valid
        return self.expiry_date and self.expiry_date >= today


    def reset_remaining_applications(self):
        today = date.today()

        if self.plan == self.FREE:
            # Reset Free plan applications on the first day of each month
            if self.last_reset_date.month != today.month:
                self.remaining_applications = self.get_application_limit()  # Default is 3 for Free plan
                self.applications_used = 0
                self.last_reset_date = today
                self.save()

        elif self.expiry_date and self.expiry_date < today:
            # If a paid subscription expired, revert to Free plan
            if self.plan != self.FREE:  # Don't revert if already on Free plan
                self.plan = self.FREE
                self.expiry_date = None
                self.remaining_applications = self.get_application_limit()  # Default Free plan applications
                self.applications_used = 0
                self.last_reset_date = today
                self.save()

        elif self.last_reset_date.month != today.month:
            # Reset applications for paid plans if a new month starts
            self.remaining_applications = self.get_application_limit()
            self.applications_used = 0
            self.last_reset_date = today
            self.save()


    def needs_reset(self):
        """
        Determines if the subscription needs a reset.
        - Reset if the subscription expired.
        - Reset if the last reset occurred in a different month.
        """
        today = date.today()
        return (
            (self.expiry_date and self.expiry_date < today) or
            (self.last_reset_date.month != today.month)
        )

    def get_application_limit(self):
        """
        Returns the application limit for the current plan.
        """
        plan_limits = {
            self.FREE: 3,
            self.PLAN_499: 6,
            self.PLAN_1200: 12,
        }
        return plan_limits.get(self.plan, 3)
    
    def get_expiry_date(self):
        if self.plan == 'Free':
            today = date.today()
            _, last_day = monthrange(today.year, today.month)
            return date(today.year, today.month, last_day)
        return self.expiry_date

    def __str__(self):
        return f"{self.applicant.user.username} - {self.plan}"
    
    
from companies.models import Company
class ProfileView(models.Model):
    viewed_applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='profile_views')
    viewed_by_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="companies_views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.viewed_by_company.company_name} viewed {self.viewed_applicant.user.username}"


