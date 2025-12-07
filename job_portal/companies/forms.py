from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from .models import Company
from jobs.models import Job

class CompanySignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.COMPANY  # Automatically set the role to 'COMPANY'
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        
        # Password matching validation
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        # Ensure email uniqueness
        email = cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        
        return cleaned_data


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'description', 'location', 'website', 'email', 'phone_number', 'logo']
        
class JobApplicationForm(forms.Form):
    job = forms.ModelChoiceField(
        queryset=Job.objects.none(),
        label="Select Job",
        empty_label="Choose a job"
    )
    interview_date = forms.DateTimeField(label="Interview Date", widget=forms.TextInput(attrs={'type': 'datetime-local'}))
    interview_venue = forms.CharField(label="Interview Venue", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            # Filter jobs by the company that owns them
            self.fields['job'].queryset = Job.objects.filter(company__owner=company)


