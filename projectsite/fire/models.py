from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Location(models.Model):
    name = models.CharField(max_length=150)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name


class Locations(BaseModel):
    name = models.CharField(max_length=150)
    latitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16, 
        null=True, 
        blank=True,
        help_text="Latitude coordinate of the location"
    )
    longitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16, 
        null=True, 
        blank=True,
        help_text="Longitude coordinate of the location"
    )
    address = models.CharField(
        max_length=500,  # Increased to accommodate full addresses
        blank=True,
        help_text="Full address from geocoding"
    )
    city = models.CharField(
        max_length=150,
        blank=True,
        help_text="City name"
    )
    country = models.CharField(
        max_length=150,
        blank=True,
        help_text="Country name"
    )

    def __str__(self):
        return self.name

    def get_coordinates(self):
        if self.latitude and self.longitude:
            return (self.latitude, self.longitude)
        return None

    def update_from_coordinates(self, latitude, longitude, address_data):
        self.latitude = latitude
        self.longitude = longitude
        self.address = address_data.get('display_name', '')
        self.city = address_data.get('address', {}).get('city', '')
        self.country = address_data.get('address', {}).get('country', '')
        self.save()


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


class FireStation(models.Model):
    name = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16, 
        null=True, 
        blank=True,
        help_text="Latitude coordinate of the location"
    )
    longitude = models.DecimalField(
        max_digits=22, 
        decimal_places=16, 
        null=True, 
        blank=True,
        help_text="Longitude coordinate of the location"
    )
    address = models.CharField(
        max_length=500,  # Increased to accommodate full addresses
        blank=True,
        help_text="Full address from geocoding"
    )
    city = models.CharField(
        max_length=150,
        blank=True,
        help_text="City name"
    )
    country = models.CharField(
        max_length=150,
        blank=True,
        help_text="Country name"
    )

    def __str__(self):
        return self.name

    def get_coordinates(self):
        if self.latitude and self.longitude:
            return (self.latitude, self.longitude)
        return None

    def update_from_coordinates(self, latitude, longitude, address_data):
        self.latitude = latitude
        self.longitude = longitude
        self.address = address_data.get('display_name', '')
        self.city = address_data.get('address', {}).get('city', '')
        self.country = address_data.get('address', {}).get('country', '')
        self.save()


class Firefighters(models.Model):
    RANK_CHOICES = (
        ('Director', 'Director'),
        ('Chief Superintendent', 'Chief Superintendent'),
        ('Senior Superintendent', 'Senior Superintendent'),
        ('Superintendent', 'Superintendent'),
        ('Chief Inspector', 'Chief Inspector'),
        ('Senior Inspector', 'Senior Inspector'),
        ('Inspector', 'Inspector'),
    )
    name = models.CharField(max_length=150)
    rank = models.CharField(
        max_length=45,  # Reduced from 150 since we have choices
        choices=RANK_CHOICES,
        help_text="Firefighter's rank"
    )
    experience_level = models.CharField(
        max_length=45,  # Reduced from 150 since we have choices
        choices=(
            ('Probationary Firefighter', 'Probationary Firefighter'),
            ('Firefighter I', 'Firefighter I'),
            ('Firefighter II', 'Firefighter II'),
            ('Firefighter III', 'Firefighter III'),
            ('Driver', 'Driver'),
            ('Captain', 'Captain'),
            ('Battalion Chief', 'Battalion Chief'),
        ),
        help_text="Firefighter's experience level"
    )
    station = models.CharField(
        max_length=150,
        choices=[
            ('Station 1', 'Station 1'),
            ('Station 2', 'Station 2'),
            ('Station 3', 'Station 3'),
            ('Station 4', 'Station 4'),
            ('Station 5', 'Station 5'),
        ],
        help_text="Fire station where the firefighter is assigned",
        default='Station 1'  # Provide a default value here
    )


class FireTruck(models.Model):
    truck_number = models.CharField(max_length=150)
    model = models.CharField(max_length=150)
    capacity = models.CharField(max_length=150)  # water
    station = models.ForeignKey(FireStation, on_delete=models.CASCADE)


class WeatherConditions(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=10, decimal_places=2)
    humidity = models.DecimalField(max_digits=10, decimal_places=2)
    wind_speed = models.DecimalField(max_digits=10, decimal_places=2)
    weather_description = models.CharField(max_length=150)
    wind_direction = models.CharField(max_length=50, null=True, blank=True)  # Add this
