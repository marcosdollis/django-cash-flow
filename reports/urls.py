from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list_view, name='list'),
    path('generate/', views.report_generate_view, name='generate'),
    path('<uuid:uuid>/', views.report_detail_view, name='detail'),
    path('<uuid:uuid>/download/', views.report_download_view, name='download'),
    
    # Dashboards
    path('dashboards/', views.dashboard_list_view, name='dashboard_list'),
    path('dashboards/create/', views.dashboard_create_view, name='dashboard_create'),
    path('dashboards/<int:pk>/', views.dashboard_detail_view, name='dashboard_detail'),
    
    # Previsões
    path('forecasts/', views.forecast_list_view, name='forecast_list'),
    path('forecasts/create/', views.forecast_create_view, name='forecast_create'),
    
    # Alertas
    path('alerts/', views.alert_list_view, name='alert_list'),
    path('alerts/<int:pk>/acknowledge/', views.alert_acknowledge_view, name='alert_acknowledge'),
    path('alerts/<int:pk>/resolve/', views.alert_resolve_view, name='alert_resolve'),
]