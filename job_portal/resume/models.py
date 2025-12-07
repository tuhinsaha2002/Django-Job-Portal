from django.db import models

class Resume(models.Model):
    candidate_name = models.CharField(max_length=100, default="Anonymous")
    uploaded_resume = models.FileField(upload_to='resumes/')
    ats_score = models.FloatField(null=True, blank=True)

class ATSAnalysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    score = models.FloatField()
    analysis_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
