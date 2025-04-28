from django import forms
from .models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['inventory_number', 'name', 'type', 'location', 'details', 
                 'purchase_date', 'is_active', 'bitlocker_key']

        widgets = {
            'inventory_number': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'name': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'type': forms.Select(attrs={'class': 'form-control shadow-none'}),
            'location': forms.TextInput(attrs={'class': 'form-control shadow-none'}),
            'details': forms.Textarea(attrs={'class': 'form-control shadow-none', 'rows': 8, 'style': 'resize: none;'}),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control shadow-none', 
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input shadow-none'}),
            'bitlocker_key': forms.TextInput(attrs={
                'class': 'form-control shadow-none',
                'placeholder': 'e.g.: 123456-123456-123456-123456-123456-123456-123456-123456'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Get the user if it was passed
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show bitlocker field to staff users (technicians/managers)
        if not user or not user.is_authenticated:
            self.fields.pop('bitlocker_key', None)
