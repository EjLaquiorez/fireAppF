from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Locations(BaseModel):
    name = models.CharField(max_length=150)
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)  # can be in separate table
    country = models.CharField(max_length=150)  # can be in separate table


class Incident(BaseModel):
    SEVERITY_CHOICES = (
        ('Minor Fire', 'Minor Fire'),
        ('Moderate Fire', 'Moderate Fire'),
        ('Major Fire', 'Major Fire'),
    )
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Resolve', 'Resolve'),
    )
    INCIDENT_TYPE_CHOICES = (
        ('Structure Fire', 'Structure Fire'),
        ('Vehicle Fire', 'Vehicle Fire'),
        ('Wildfire', 'Wildfire'),
        ('Chemical Fire', 'Chemical Fire'),
        ('Electrical Fire', 'Electrical Fire'),
    )
    location = models.ForeignKey(Locations, on_delete=models.CASCADE, related_name='incidents')
    date_time = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Date and time when the incident occurred"
    )
    severity_level = models.CharField(
        max_length=45, 
        choices=SEVERITY_CHOICES,
        help_text="Level of fire severity"
    )
    status = models.CharField(
        max_length=45, 
        choices=STATUS_CHOICES, 
        default='Active'
    )
    description = models.TextField(  # Changed from CharField to TextField
        max_length=1000,  # Increased max length
        help_text="Detailed description of the incident"
    )
    incident_type = models.CharField(
        max_length=100,  # Changed from 45 to 100
        choices=INCIDENT_TYPE_CHOICES,
        null=True,      # Added
        blank=True,     # Added
        help_text="Type of fire incident"
    )


class FireStation(BaseModel):
    name = models.CharField(max_length=150)
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)  # can be in separate table
    country = models.CharField(max_length=150)  # can be in separate table


class Firefighters(BaseModel):
    XP_CHOICES = (
        ('Probationary Firefighter', 'Probationary Firefighter'),
        ('Firefighter I', 'Firefighter I'),
        ('Firefighter II', 'Firefighter II'),
        ('Firefighter III', 'Firefighter III'),
        ('Driver', 'Driver'),
        ('Captain', 'Captain'),
        ('Battalion Chief', 'Battalion Chief'),)
    name = models.CharField(max_length=150)
    rank = models.CharField(max_length=150)
    experience_level = models.CharField(
        max_length=45,  # Reduced from 150 since we have choices
        choices=XP_CHOICES,
        help_text="Firefighter's experience level"
    )
    station = models.ForeignKey(  # Changed to ForeignKey
        FireStation,
        on_delete=models.SET_NULL,
        null=True,
        related_name='firefighters'
    )


class FireTruck(BaseModel):
    truck_number = models.CharField(max_length=150)
    model = models.CharField(max_length=150)
    capacity = models.CharField(max_length=150)  # water
    station = models.ForeignKey(FireStation, on_delete=models.CASCADE)


class WeatherConditions(BaseModel):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=10, decimal_places=2)
    humidity = models.DecimalField(max_digits=10, decimal_places=2)
    wind_speed = models.DecimalField(max_digits=10, decimal_places=2)
    weather_description = models.CharField(max_length=150)
    wind_direction = models.CharField(max_length=50, null=True, blank=True)  # Add this
