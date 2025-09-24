from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'api'

# Para APIs REST futuras
router = DefaultRouter()

urlpatterns = [
    path('v1/', include(router.urls)),
]