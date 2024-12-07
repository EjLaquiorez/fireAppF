from django.urls import path
from django.contrib import admin
from fire.views import (
    HomePageView, 
    ChartView, 
    PieCountbySeverity,
    LineCountbyMonth,
    MultilineIncidentTop3Country,
    multipleBarbySeverity,
    IncidentCreateView, IncidentUpdateView, IncidentDeleteView, IncidentListView,
    incident_detail,
    get_weather,
    bar_chart,
    doughnut_chart,
    radar_chart,
    incident_list_table,
    MapIncidentView
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
    path('incidents/', IncidentListView.as_view(), name='incident-list'),
    path('incidents/table/', views.incident_list_table, name='incident-list-table'),
    path('incidents/<int:pk>/', incident_detail, name='incident-detail'),
    path('incidents/<int:pk>/edit/', IncidentUpdateView.as_view(), name='incident-update'),
    path('incidents/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident-delete'),
    path('api/weather/', get_weather, name='get-weather'),
    path('barChart/', bar_chart, name='bar_chart'),
    path('doughnutChart/', doughnut_chart, name='doughnut_chart'),
    path('radarChart/', radar_chart, name='radar_chart'),
    path('map/incident/', MapIncidentView.as_view(), name='map-incident'),
]