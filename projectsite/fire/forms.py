from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Incident, Locations, Firefighters

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

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if date_time > timezone.now():
            raise ValidationError("Future dates are not allowed.")
        return date_time

    def clean_temperature(self):
        temperature = self.cleaned_data.get('temperature')
        if temperature < 0:
            raise ValidationError("Temperature cannot be negative.")
        return temperature

    def clean_humidity(self):
        humidity = self.cleaned_data.get('humidity')
        if humidity < 0:
            raise ValidationError("Humidity cannot be negative.")
        return humidity

    def clean_wind_speed(self):
        wind_speed = self.cleaned_data.get('wind_speed')
        if wind_speed < 0:
            raise ValidationError("Wind speed cannot be negative.")
        return wind_speed

class LocationForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = ['name', 'address', 'city', 'country', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter location name'
                }
            ),
            'address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter address'
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter city'
                }
            ),
            'country': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter country'
                }
            ),
            'latitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': 'any'
                }
            ),
            'longitude': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': 'any'
                }
            ),
        }

class FirefighterForm(forms.ModelForm):
    class Meta:
        model = Firefighters
        fields = ['name', 'rank', 'experience_level', 'station']