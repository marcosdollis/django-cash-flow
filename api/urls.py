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
    
    # WebAuthn (Biometria)
    path('webauthn/register/options/', views.webauthn_registration_options, name='webauthn_register_options'),
    path('webauthn/register/verify/', views.webauthn_registration_verify, name='webauthn_register_verify'),
    path('webauthn/authenticate/options/', views.webauthn_authentication_options, name='webauthn_auth_options'),
    path('webauthn/authenticate/verify/', views.webauthn_authentication_verify, name='webauthn_auth_verify'),
    path('webauthn/remove/', views.webauthn_remove_credential, name='webauthn_remove'),
]