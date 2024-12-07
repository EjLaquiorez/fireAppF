from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count, Avg
from datetime import datetime
from django.contrib import messages

from .models import Locations, Incident, FireStation
from .forms import IncidentForm

import requests
from django.conf import settings

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'
    model = Incident

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Incident.objects.all()

def PieCountbySeverity(request): 
    query = '''
    SELECT COALESCE(severity_level, 'Unknown') as severity_level, 
           COUNT(*) as count 
    FROM fire_incident 
    GROUP BY severity_level
    ORDER BY severity_level;
    ''' 
    
    with connection.cursor() as cursor: 
        cursor.execute(query)
        rows = cursor.fetchall()
    
    # Convert the rows directly into a dictionary
    data = {str(severity): count for severity, count in rows}
    
    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year
    result = {month: 0 for month in range(1, 13)}
    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1
        
    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
    
    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()}
    
    return JsonResponse(result_with_month_names)

def MultilineIncidentTop3Country(request):
    query = '''
    SELECT fl.country, strftime('%m', fi.date_time) AS month, COUNT(fi.id) AS incident_count 
    FROM fire_incident fi 
    JOIN fire_locations fl ON fi.location_id = fl.id 
    WHERE fl.country IN (
        SELECT fl_top.country 
        FROM fire_incident fi_top 
        JOIN fire_locations fl_top ON fi_top.location_id = fl_top.id 
        WHERE strftime('%Y', fi_top.date_time) = strftime('%Y', 'now') 
        GROUP BY fl_top.country 
        ORDER BY COUNT(fi_top.id) DESC 
        LIMIT 3
    ) 
    AND strftime('%Y', fi.date_time) = strftime('%Y', 'now') 
    GROUP BY fl.country, month 
    ORDER BY fl.country, month;
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    
    # Initialize a dictionary to store the result
    result = {}
    
    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))
    
    # Month names mapping
    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]
        
        # If the country is not in the result dictionary initialize it with all months set to zero
        if country not in result:
            result[country] = {month_names[m]: 0 for m in months}
            
        # Update the incident count for the corresponding month
        result[country][month_names[month]] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month_names[m]: 0 for m in months}

    # Sort months within each country
    for country in result:
        result[country] = dict(sorted(result[country].items(), 
            key=lambda x: list(month_names.values()).index(x[0])))
        
    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM fire_incident fi
    WHERE strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY fi.severity_level, month
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    
    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    
    # Month names mapping
    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }
    
    for row in rows:
        level = str(row[0])
        month = row[1]
        total_incidents = row[2]
        
        if level not in result:
            result[level] = {month_names[m]: 0 for m in months}
            
        result[level][month_names[month]] = total_incidents
    
    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items(), 
            key=lambda x: list(month_names.values()).index(x[0])))
    
    return JsonResponse(result)

def map_station(request):
    # Retrieve fire station data from the database
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    # Convert latitude and longitude to float for proper handling in JavaScript
    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    # Convert QuerySet to a list
    fireStations_list = list(fireStations)

    # Prepare context to pass to the template
    context = {
        'fireStations': fireStations_list,
    }

    # Render the template with the fire station data
    return render(request, 'map_station.html', context)

def chart_data(request):
    # Group incidents by severity_level and count them
    severity_counts = (Incident.objects
        .values('severity_level')
        .annotate(count=Count('id'))
        .order_by('severity_level'))
    
    # Convert to the format expected by the chart
    data = {item['severity_level']: item['count'] for item in severity_counts}
    
    # If no data exists, provide default empty data structure
    if not data:
        data = {
            'Minor Fire': 0,
            'Moderate Fire': 0,
            'Major Fire': 0
        }
    
    return JsonResponse(data)

class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_form.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        messages.success(self.request, 'Incident created successfully!')
        return super().form_valid(form)

class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_form.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        messages.success(self.request, 'Incident updated successfully!')
        return super().form_valid(form)

class IncidentDeleteView(DeleteView):
    model = Incident
    success_url = reverse_lazy('incident-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Incident deleted successfully!')
        return super().delete(request, *args, **kwargs)

def map_incident(request):
    try:
        incidents = Incident.objects.filter(
            location__latitude__isnull=False,
            location__longitude__isnull=False
        ).select_related('location').prefetch_related('weatherconditions_set').values(
            'severity_level',
            'date_time',
            'location__name',
            'location__latitude',
            'location__longitude',
            'status',
            'incident_type',
            'description',
            'weatherconditions__temperature',
            'weatherconditions__humidity',
            'weatherconditions__wind_speed',
        )

        # Get fire stations
        fire_stations = FireStation.objects.values('name', 'latitude', 'longitude')

        # Get unique locations for the filter dropdown
        locations = Incident.objects.values_list('location__name', flat=True).distinct()

        # Format the data for the template
        incident_list = []
        for incident in incidents:
            try:
                latitude = float(incident['location__latitude'])
                longitude = float(incident['location__longitude'])
            except (ValueError, TypeError):
                continue
            
            incident_list.append({
                'latitude': latitude,
                'longitude': longitude,
                'severity_level': incident['severity_level'],
                'date': incident['date_time'].strftime('%Y-%m-%d %H:%M'),
                'location': incident['location__name'],
                'status': 'Active' if incident.get('status') == 'active' else 'Resolved',
                'incident_type': incident.get('incident_type', 'Fire Incident'),
                'description': incident.get('description', ''),
                'weather': {
                    'temperature': incident.get('weatherconditions__temperature'),
                    'humidity': incident.get('weatherconditions__humidity'),
                    'wind_speed': incident.get('weatherconditions__wind_speed'),
                    'wind_direction': incident.get('weatherconditions__wind_direction')
                }
            })

        # Format fire stations data
        station_list = [{
            'name': station['name'],
            'latitude': float(station['latitude']),
            'longitude': float(station['longitude'])
        } for station in fire_stations]

        context = {
            'fireIncidents': incident_list,
            'fireStations': station_list,
            'locations': locations,
        }
        return render(request, 'map_incident.html', context)
    except Exception as e:
        messages.error(request, f"Error loading map data: {str(e)}")
        return render(request, 'map_incident.html', {'error': True})

class IncidentListView(ListView):
    model = Incident
    template_name = 'incident_list.html'
    context_object_name = 'incidents'
    ordering = ['-date_time']

def incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    return render(request, 'incident_detail.html', {'incident': incident})

def get_weather(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not lat or not lon:
        return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)
    
    # OpenWeatherMap API endpoint
    api_key = settings.OPENWEATHER_API_KEY  # You'll need to add this to settings.py
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        weather_data = {
            'temperature': round(data['main']['temp'], 1),
            'humidity': data['main']['humidity'],
            'wind_speed': round(data['wind']['speed'], 1),
            'conditions': data['weather'][0]['description']
        }
        
        return JsonResponse(weather_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def map_incident_view(request):
    # Get all unique locations from Incident model
    locations = Incident.objects.values_list('location__name', flat=True).distinct()
    
    # Get all incidents with their locations
    incidents = Incident.objects.select_related('location').all()
    
    context = {
        'locations': locations,
        'fireIncidents': list(incidents)
    }
    return render(request, 'map_incident.html', context)

def bar_chart(request):
    # Example query - modify according to your model structure
    monthly_data = Incident.objects.values('month').annotate(count=Count('id'))
    data = {item['month']: item['count'] for item in monthly_data}
    return JsonResponse(data)

def doughnut_chart(request):
    # Example query
    category_data = Incident.objects.values('category').annotate(count=Count('id'))
    data = {item['category']: item['count'] for item in category_data}
    return JsonResponse(data)

def radar_chart(request):
    # Example query
    metric_data = Incident.objects.values('metric').annotate(value=Avg('value'))
    data = {item['metric']: item['value'] for item in metric_data}
    return JsonResponse(data)
