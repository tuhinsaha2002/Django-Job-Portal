from django.db import models
from companies.models import Company
from django.utils.timezone import now
from users.models import Applicant # Assuming Applicant is in users.models
from datetime import timedelta,timezone

def get_default_expiry_date():
    return now().date() + timedelta(days=30)

from django.utils import timezone
from datetime import timedelta

class Job(models.Model):
    FULL_TIME = 'FT'
    PART_TIME = 'PT'
    REMOTE = 'RM'
    JOB_TYPE_CHOICES = [
        (FULL_TIME, 'Full-time'),
        (PART_TIME, 'Part-time'),
        (REMOTE, 'Remote'),
    ]
    
    LOCATION_CHOICES = [
        ('Mumbai', 'Mumbai'),
        ('Vasai', 'Vasai'),
        # Add more locations as needed
    ]
    
    CATEGORY_CHOICES = [
    ('Software Developer', 'Software Developer'),
    ('Designer', 'Designer'),
    ('Marketing', 'Marketing'),
    ('Service', 'Service'),
    ('Teacher', 'Teacher'),
    ('Finance', 'Finance'),
    ('Data Analyst', 'Data Analyst'),
    ('Content Writer', 'Content Writer'),
    ('Sales', 'Sales'),
    ('Customer Support', 'Customer Support'),
    ('Engineering', 'Engineering'),
    ('Human Resources', 'Human Resources'),
]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills_required = models.TextField()
    min_salary = models.DecimalField(max_digits=6, decimal_places=2, help_text="Minimum salary in LPA")
    max_salary = models.DecimalField(max_digits=6, decimal_places=2, help_text="Maximum salary in LPA")
    location = models.CharField(max_length=255, choices=LOCATION_CHOICES)
    job_type = models.CharField(max_length=2, choices=JOB_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Software Developer')
    expiry_date = models.DateField(default=get_default_expiry_date)
    min_experience = models.PositiveIntegerField(default=0)  # Minimum years of experience required
    max_experience = models.PositiveIntegerField(default=0)  # Maximum years of experience allowed
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Field to mark if the job is active or not
    vacancies = models.PositiveIntegerField(default=1)

    def experience_range(self):
        """Returns the experience range as a string."""
        return f"{self.min_experience} - {self.max_experience} years"
    
    def check_expiry(self):
        """Check if the job is expired."""
        if self.expiry_date and self.expiry_date < timezone.now().date():
            self.is_active = False
            self.save()

    @property
    def is_expired(self):
        """Returns True if the job is expired."""
        return self.expiry_date and self.expiry_date < timezone.now().date()
    
    def salary_range(self):
        """Returns the salary range in LPA as a string."""
        return f"{self.min_salary} LPA to {self.max_salary} LPA"

    def __str__(self):
        return self.title


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    applied_on = models.DateTimeField(default=now)
    experience = models.IntegerField(default=0)
    feedback = models.TextField(null=True, blank=True)  # For rejection feedback
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Reviewed', 'Reviewed'),
            ('Shortlisted for Interview', 'Shortlisted for Interview'),
            ('Accepted', 'Accepted'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending',
    )
    interview_date = models.DateTimeField(blank=True, null=True, default=None)  # For interview scheduling
    interview_venue = models.TextField(blank=True, null=True, default="")  # Venue for interview

    class Meta:
        ordering = ['-applied_on']  # Default to most recent applications

    def __str__(self):
        return f"Application: {self.applicant.user.username} for {self.job.title} - Status: {self.status}"
    
    
class Wishlist(models.Model):
    user = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='wishlists')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')  # Ensure a user can't wishlist the same job twice
        ordering = ['-added_on']  # Most recent wishlisted jobs first

    def __str__(self):
        return f"{self.user.user.username} wishlisted {self.job.title}"

