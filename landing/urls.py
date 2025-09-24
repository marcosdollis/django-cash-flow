from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.landing_page, name='home'),
    path('start-trial/', views.start_trial, name='start_trial'),
    path('schedule-demo/', views.schedule_demo, name='schedule_demo'),
    path('get-started/', views.redirect_to_dashboard, name='get_started'),
]