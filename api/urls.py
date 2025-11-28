from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Para APIs REST futuras
router = DefaultRouter()

urlpatterns = [
    path('v1/', include(router.urls)),
    
    # Push Notifications
    path('push/subscribe/', views.subscribe_push, name='push_subscribe'),
    path('push/unsubscribe/', views.unsubscribe_push, name='push_unsubscribe'),
    path('push/test/', views.test_push, name='push_test'),
]