from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['candidate_name', 'uploaded_resume']

class JobDescriptionForm(forms.Form):
    uploaded_resume = forms.FileField(label="Upload Resume")
    job_description = forms.CharField(widget=forms.Textarea, label="Job Description")
