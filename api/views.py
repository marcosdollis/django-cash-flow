from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.models import PushSubscription, PushNotificationLog
from pywebpush import webpush, WebPushException
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def subscribe_push(request):
    """
    Endpoint para registrar uma nova subscrição push
    """
    try:
        data = json.loads(request.body)
        subscription_info = data.get('subscription')
        
        if not subscription_info:
            return JsonResponse({'error': 'Subscription data required'}, status=400)
        
        # Extrair dados da subscription
        endpoint = subscription_info.get('endpoint')
        keys = subscription_info.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return JsonResponse({'error': 'Invalid subscription data'}, status=400)
        
        # Criar ou atualizar subscrição
        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh': p256dh,
                'auth': auth,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                'device_name': data.get('device_name', 'Navegador'),
                'is_active': True,
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Subscrição criada com sucesso' if created else 'Subscrição atualizada',
            'subscription_id': subscription.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao criar subscrição: {str(e)}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def unsubscribe_push(request):
    """
    Endpoint para desativar uma subscrição push
    """
    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return JsonResponse({'error': 'Endpoint required'}, status=400)
        
        # Desativar subscrição
        updated = PushSubscription.objects.filter(
            user=request.user,
            endpoint=endpoint
        ).update(is_active=False)
        
        if updated:
            return JsonResponse({'success': True, 'message': 'Subscrição removida'})
        else:
            return JsonResponse({'error': 'Subscrição não encontrada'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao remover subscrição: {str(e)}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


def send_push_notification(user, title, body, url='', icon='/static/icons/icon-192x192.png'):
    """
    Função helper para enviar notificação push para todas as subscrições ativas de um usuário
    
    Args:
        user: Objeto User
        title: Título da notificação
        body: Corpo da mensagem
        url: URL opcional para abrir ao clicar
        icon: Caminho do ícone
    
    Returns:
        dict com estatísticas de envio
    """
    subscriptions = PushSubscription.objects.filter(user=user, is_active=True)
    
    results = {
        'sent': 0,
        'failed': 0,
        'total': subscriptions.count()
    }
    
    # Dados da notificação
    notification_data = {
        'title': title,
        'body': body,
        'icon': icon,
        'badge': '/static/icons/icon-72x72.png',
        'url': url,
    }
    
    # VAPID keys - você precisará gerar essas chaves
    vapid_claims = {
        "sub": f"mailto:{getattr(settings, 'VAPID_ADMIN_EMAIL', 'admin@cashflow.com')}"
    }
    
    for subscription in subscriptions:
        try:
            # Log da tentativa
            log = PushNotificationLog.objects.create(
                subscription=subscription,
                title=title,
                body=body,
                icon=icon,
                url=url,
                status='pending'
            )
            
            # Preparar dados para webpush
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            }
            
            # Enviar notificação
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(notification_data),
                vapid_private_key=getattr(settings, 'VAPID_PRIVATE_KEY', None),
                vapid_claims=vapid_claims
            )
            
            # Atualizar log como enviado
            log.status = 'sent'
            log.save()
            
            subscription.mark_used()
            results['sent'] += 1
            
        except WebPushException as e:
            logger.error(f"Erro ao enviar push para {subscription.id}: {str(e)}")
            
            # Se a subscrição expirou (410 Gone), desativar
            if e.response and e.response.status_code == 410:
                subscription.is_active = False
                subscription.save()
                log.status = 'expired'
            else:
                log.status = 'failed'
            
            log.error_message = str(e)
            log.save()
            results['failed'] += 1
            
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar push: {str(e)}")
            log.status = 'failed'
            log.error_message = str(e)
            log.save()
            results['failed'] += 1
    
    return results


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def test_push(request):
    """
    Endpoint para testar envio de notificação push
    """
    try:
        results = send_push_notification(
            user=request.user,
            title='Teste de Notificação',
            body='Sua notificação push está funcionando! 🎉',
            url='/dashboard/',
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Notificação enviada',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação teste: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
