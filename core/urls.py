from django.urls import path
from . import views, premium_exports

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('overview/', views.overview_view, name='overview'),
    path('insights/', views.insights_view, name='insights'),  # PREMIUM FEATURE
    
    # Exportações Premium
    path('export/pdf/', premium_exports.export_financial_report_pdf, name='export_pdf'),
    path('export/excel/', premium_exports.export_financial_report_excel, name='export_excel'),
    path('export/', views.export_financial_report, name='export_financial_report'),
]