"""
Context processors para templates
"""
from django.conf import settings


def vapid_public_key(request):
    """Disponibiliza a chave pública VAPID nos templates"""
    return {
        'VAPID_PUBLIC_KEY': getattr(settings, 'VAPID_PUBLIC_KEY', '')
    }
