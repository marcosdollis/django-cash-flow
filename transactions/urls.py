from django.urls import path
from . import views
from .test_views import test_transaction_detail

app_name = 'transactions'

urlpatterns = [
    path('', views.transaction_list_view, name='list'),
    path('add/', views.transaction_create_view, name='create'),
    path('<uuid:uuid>/', views.transaction_detail_view, name='detail'),
    path('<uuid:uuid>/test/', test_transaction_detail, name='test_detail'),
    path('<uuid:uuid>/edit/', views.transaction_update_view, name='update'),
    path('<uuid:uuid>/status/', views.transaction_update_status_view, name='update_status'),
    path('<uuid:uuid>/delete/', views.transaction_delete_view, name='delete'),
    path('bulk/status/', views.transaction_bulk_update_status_view, name='bulk_update_status'),
    
    # Categorias
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/add/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update_view, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
    
    # Contas
    path('accounts/', views.account_list_view, name='account_list'),
    path('accounts/add/', views.account_create_view, name='account_create'),
    path('accounts/<int:pk>/edit/', views.account_update_view, name='account_update'),
    path('accounts/<int:pk>/delete/', views.account_delete_view, name='account_delete'),
    
    # Metas
    path('goals/', views.goal_list_view, name='goal_list'),
    path('goals/add/', views.goal_create_view, name='goal_create'),
    path('goals/<int:pk>/edit/', views.goal_update_view, name='goal_update'),
    path('goals/<int:pk>/delete/', views.goal_delete_view, name='goal_delete'),
]