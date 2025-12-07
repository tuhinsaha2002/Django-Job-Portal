from django import forms
from .models import Job,Application

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 
            'description', 
            'skills_required', 
            'min_salary', 
            'max_salary',  # Added fields for salary range
            'location', 
            'job_type', 
            'min_experience', 
            'max_experience', 
            'expiry_date', 
            'vacancies',
            'category',
        ]

    # Customizing the expiry_date field to use a date picker
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Select the job expiry date."
    )

    # Customizing the min_salary and max_salary fields to use dropdown
    min_salary = forms.ChoiceField(
        choices=[(i / 2, f"{i / 2} LPA") for i in range(0, 101)],  # Dropdown for 0.0 to 50.0 LPA
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the minimum salary in LPA."
    )

    max_salary = forms.ChoiceField(
        choices=[(i / 2, f"{i / 2} LPA") for i in range(0, 101)],  # Dropdown for 0.0 to 50.0 LPA
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the maximum salary in LPA."
    )

    # Additional validation for salary range
    def clean(self):
        cleaned_data = super().clean()
        min_salary = float(cleaned_data.get('min_salary', 0))
        max_salary = float(cleaned_data.get('max_salary', 0))

        if min_salary > max_salary:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")

        return cleaned_data




class ApplicationForm(forms.ModelForm):
    experience = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Years of Experience"
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label="Cover Letter"
    )

    class Meta:
        model = Application
        fields = ['resume', 'experience', 'cover_letter']

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)

    def clean_experience(self):
        experience = self.cleaned_data['experience']
        if self.job:
            if experience < self.job.min_experience or experience > self.job.max_experience:
                raise forms.ValidationError(
                    f"Your experience must be between {self.job.min_experience} and {self.job.max_experience} years."
                )
        return experience


        
class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['interview_date', 'interview_venue']  # Only include interview-related fields
        
