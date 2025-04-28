from django import forms
from django.core.validators import FileExtensionValidator
from .models import Ticket, TicketAttachment, TicketMessage
from .choices import TicketItemChoices
from .models import Ticket, TicketType, TicketSubType
from assets.models import AssetType

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class TicketSubmissionForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'form-control shadow-none',
            'style': 'resize: none;',
            'placeholder': 'Please describe your issue or request in detail'
        })
    )

    type = forms.ChoiceField(
        choices = [('', 'Select a type...')] + [(t.value, t.label) for t in TicketType],
        widget=forms.Select(attrs={'class': 'form-control shadow-none color-666'})
    )

    subtype = forms.ChoiceField(
        choices = [('', 'Select a subtype...')] + [(t.value, t.label) for t in TicketSubType],
        widget=forms.Select(attrs={'class': 'form-control shadow-none color-666'})
    )

    item = forms.ChoiceField(
        choices=[('', 'Select an item...')] + TicketItemChoices.ALL_ITEM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control shadow-none color-666'})
    )

    attachments = MultipleFileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg'])],
        help_text='Allowed file types: PDF, DOC, DOCX, TXT, PNG, JPG. Max size: 5MB per file.'
    )
    inventory_number = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control shadow-none color-666',
            'placeholder': 'Optional: Enter asset inventory number if relevant'
        }),
        help_text='If your request relates to a specific asset, enter its inventory number'
    )
    
    asset_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Select asset type...')] + [(t.value, t.label) for t in AssetType],
        widget=forms.Select(attrs={
            'class': 'form-control shadow-none color-666',
            'disabled': 'disabled'  # Initially disabled, will be enabled by JavaScript when inventory_number is filled
        })
    )

    class Meta:
        model = Ticket
        fields = ['requestor_email', 'requestor_phone', 'requestor_name', 
                 'title', 'description', 'type', 'subtype', 'item',
                 'inventory_number', 'asset_type']  # Add both fields
        labels = {
            'title': 'Subject',
        }
        widgets = {
            'requestor_email': forms.EmailInput(attrs={
                'class': 'form-control shadow-none',
                'placeholder': 'your.email@etsu.edu'
            }),
            'requestor_phone': forms.TextInput(attrs={
                'class': 'form-control shadow-none',
                'placeholder': '(Optional) Phone number'
            }),
            'requestor_name': forms.TextInput(attrs={
                'class': 'form-control shadow-none',
                'placeholder': 'Your full name'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control shadow-none',
                'placeholder': 'Brief subject line for your ticket'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        inventory_number = cleaned_data.get('inventory_number')
        asset_type = cleaned_data.get('asset_type')
        
        # If inventory number is provided, asset type is required
        if inventory_number and not asset_type:
            self.add_error('asset_type', 'Asset type is required when an inventory number is provided')
            
        return cleaned_data

    def clean_requestor_email(self):
        email = self.cleaned_data.get('requestor_email')
        if not email.endswith('@etsu.edu'):
            raise forms.ValidationError('Please use your ETSU email address (@etsu.edu)')
        return email

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        for file in files:
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError(f'File {file.name} is too large. Maximum size is 5MB.')
        return files

class TicketAccessForm(forms.Form):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@etsu.edu', 'class': 'form-control shadow-none'})
    )
    ticket_number = forms.CharField(
        label='Ticket Number',
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-XXXX', 'class': 'form-control shadow-none'})
    )
    access_code = forms.CharField(
        label='Access Code',
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Access code from email', 'class': 'form-control shadow-none'})
    )

class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Type your message here...', 'style': 'resize: none;', 'class': 'form-control shadow-none'})
        }
