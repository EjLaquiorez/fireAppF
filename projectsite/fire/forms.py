from django import forms
from .models import Incident

class IncidentForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Incident
        fields = ['date_time', 'location', 'incident_type', 'severity_level', 'status', 'description', 'latitude', 'longitude']
        widgets = {
            'date_time': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'location': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'incident_type': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'severity_level': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter incident description'
                }
            ),
        }