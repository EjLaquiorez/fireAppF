from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

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
    JOIN fire_locations fl ON fi.location_id = fl.id WHERE fl.country 
    IN (SELECT fl_top.country FROM fire_incident fi_top 
        JOIN fire_locations fl_top ON fi_top.location_id = fl_top.id 
        WHERE strftime('%Y', fi_top.date_time) = strftime('%Y', 'now') 
        GROUP BY fl_top.country 
        ORDER BY COUNT(fi_top.id) DESC LIMIT 3 ) 
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now') 
        GROUP BY fl.country, month 
        ORDER BY fl.country, month;'''
    
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
    fields = ['severity_level', 'date_time', 'location']
    template_name = 'incident_form.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        messages.success(self.request, 'Incident was successfully created.')
        return super().form_valid(form)

class IncidentUpdateView(UpdateView):
    model = Incident
    fields = ['severity_level', 'date_time', 'location']
    template_name = 'incident_form.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        messages.success(self.request, 'Incident was successfully updated.')
        return super().form_valid(form)

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_confirm_delete.html'
    success_url = reverse_lazy('incident-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Incident was successfully deleted.')
        return super().delete(request, *args, **kwargs)

def delete_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        incident.delete()
        messages.success(request, 'Incident was successfully deleted.')
        return redirect('incident-list')
    return render(request, 'delete_incident.html', {'incident': incident})
