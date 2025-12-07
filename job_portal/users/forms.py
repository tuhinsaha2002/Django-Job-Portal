from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Applicant

class ApplicantSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.APPLICANT  # Automatically set the role to 'APPLICANT'
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        # Ensure email uniqueness
        email = cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        
        return cleaned_data



class ApplicantProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Applicant
        fields = ['dob', 'address', 'phone_no', 'bio', 'linkedin_profile', 'location', 'profile_picture', 'resume']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize first_name, last_name, email based on user details
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

        # Ensure the location field uses the choices from the model
        self.fields['location'] = forms.ChoiceField(
            choices=Applicant.LOCATION_CHOICES,  # Use the location choices defined in the model
            required=True,
            widget=forms.Select(attrs={'class': 'form-control'})
        )

    def save(self, commit=True):
        applicant = super().save(commit=False)
        user = applicant.user

        # Update user details
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            applicant.save()

        return applicant

class OTPRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)

class OTPVerifyForm(forms.Form):
    otp = forms.CharField(label="OTP", max_length=6)

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)