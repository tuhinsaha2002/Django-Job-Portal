# jobs/tests.py

from django.test import TestCase
from django.utils.timezone import now, timedelta
from .models import Job

class JobExpiryTest(TestCase):
    def test_job_expiry(self):
        # Create a job with an expiry date in the past
        job = Job.objects.create(
            title="Expired Job",
            description="A test job",
            expiry_date=now().date() - timedelta(days=1),
        )
        # Manually call the method to check expiry
        job.check_expiry()

        # Check if the job is expired (inactive)
        job.refresh_from_db()
        self.assertFalse(job.is_active)

    def test_active_job(self):
        # Create a job with an expiry date in the future
        job = Job.objects.create(
            title="Active Job",
            description="A test job",
            expiry_date=now().date() + timedelta(days=10),
        )
        # Check if the job is still active
        self.assertTrue(job.is_active)
