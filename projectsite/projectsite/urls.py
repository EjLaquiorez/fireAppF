from django.urls import path
from django.contrib import admin
from fire.views import (
    HomePageView, 
    ChartView, 
    PieCountbySeverity,
    LineCountbyMonth,
    MultilineIncidentTop3Country,
    multipleBarbySeverity,
    IncidentCreateView, IncidentUpdateView, IncidentDeleteView
)

from fire import views
    


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='pie-chart'),
    path('lineChart/', LineCountbyMonth, name='line-chart'), 
    path('multilineChart/', MultilineIncidentTop3Country, name='multiline-chart'),
    path('multiBarChart/', multipleBarbySeverity, name='multibar-chart'),
    path('incident/add/', IncidentCreateView.as_view(), name='incident-create'),
    path('incident/<int:pk>/edit/', IncidentUpdateView.as_view(), name='incident-update'),
    path('incident/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident-delete'),
    path('stations/', views.map_station, name='map-station'),
    
]