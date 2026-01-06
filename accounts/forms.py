from django import forms
from django.contrib.auth.forms import UserCreationForm
from custom_validators.validators import *
from django.core.exceptions import ValidationError
from .models import User, SystemManager, Settings
from django.contrib.auth.forms import AuthenticationForm
from django.utils.html import mark_safe

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = [
            'ticket_visibility',
            'ticket_self_assignment',
            'asset_visibility',
            'can_modify_assigned_assets',
            'can_modify_all_assets',
            'notify_status_changed',
            'notify_new_message',
            'notify_ticket_assigned',
            'notify_ticket_resolved',
            'smtp_enabled',
            'smtp_email',
            'smtp_password',
            'smtp_host',
            'smtp_port',
            'smtp_use_tls',
            'smtp_from_email',
        ]
        widgets = {
            'smtp_password': forms.PasswordInput(render_value=True),
            'smtp_port': forms.TextInput(attrs={'class': 'form-control shadow-none'})
        }

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control shadow-none',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control shadow-none',
            'placeholder': 'Password'
        })

class TechnicianCreationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control shadow-none'})
    )
    class Meta:
        model = User
        # Remove if username/password is not needed for tech
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'department')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'department': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the help text to match the validation requirements
        help_text = mark_safe(self.fields['password1'].help_text.replace(
            'at least 8 characters.</li>', 
            'at least 15 characters.</li><li>Your password must contain at least one symbol.</li>'
        ))
        self.fields['password1'].help_text = help_text

    def clean_password1(self):
        passwd1 = self.cleaned_data['password1']
        passwd2 = self.data['password2']

        if (passwd2 == '') and (passwd1 != ''):
            self.add_error('password1', '❗Please fill out this field')

        if passwd1 and passwd2:
            # Check that passwords match
            if passwd1 != passwd2:
                self.add_error('password2', '❗The passwords do not match')

            # Check password requirements
            err_list = []
            if not min_max_length_schema.validate(passwd1):
                err_list.append("❗Password must be 15-40 characters\n")
            if not upper_and_lower_schema.validate(passwd1):
                err_list.append("❗Password must have an uppercase and a lowercase letter\n")
            if not digit_no_spaces_schema.validate(passwd1):
                err_list.append("❗Password must contain a digit and no spaces\n")
            if not symbol_schema.validate(passwd1):
                err_list.append("❗Password must contain a symbol\n")
            
            [ self.add_error('password1', err) for err in err_list ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@etsu.edu'):
            raise ValidationError('Please use an ETSU email address.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.UserType.TECHNICIAN
        if commit:
            user.save()
        return user

class SystemManagerCreationForm(UserCreationForm):
    departments = forms.CharField(
        max_length=200,
        help_text='Comma-separated list of departments',
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    job_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control shadow-none'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@etsu.edu'):
            raise ValidationError('Please use an ETSU email address.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.UserType.SYSTEM_MANAGER
        if commit:
            user.save()
            SystemManager.objects.create(
                user=user,
                job_title=self.cleaned_data['job_title'],
                departments=self.cleaned_data['departments']
            )
        return user
