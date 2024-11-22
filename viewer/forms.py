from django import forms



class searchForm(forms.Form):
    search = forms.CharField(label='Search', max_length=100)


from django import forms
from django.core.exceptions import ValidationError
from datetime import date

class viewerRegistrationForm(forms.Form):
    usernames = forms.CharField(
        label="username",
        min_length=8,  # Username must be at least 8 characters long
        widget=forms.TextInput(
            attrs={
                  "class": "form-control",
                "placeholder": "Enter your username",
            }
        ),
    )
    password = forms.CharField(
        label="password",
        min_length=8,  # Password must be at least 8 characters long
        widget=forms.PasswordInput(
            attrs={
                  "class": "form-control",
                "placeholder": "Enter your password",
            }
        ),
    )
    DOB = forms.DateField(
        label="date of birth", 
        widget=forms.TextInput(attrs={  "class": "form-control","type": "date"})
    )
    address = forms.CharField(
        label="Address",
        widget=forms.TextInput(
            attrs={
                  "class": "form-control",
                "placeholder": "Enter your address",
            }
        ),
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_DOB(self):
        dob = self.cleaned_data.get('DOB')
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 10:
            raise ValidationError("You must be at least 10 years old to register.")
        return dob

    def clean_usernames(self):
        username = self.cleaned_data.get('usernames')
        if len(username) < 8:
            raise ValidationError("Username must be at least 8 characters long.")
        return username


# forms.py

from django import forms

class LoginForm(forms.Form):
    usernames = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your username"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter your password"}),
    )


class PasswordResetForm(forms.Form):
    usernames = forms.CharField(max_length=100, label='Username')
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label='New Password',
        min_length=8,
        max_length=100,
        help_text='Enter a new password.'
    )