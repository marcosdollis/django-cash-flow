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


# ==================== WEB AUTHN (BIOMETRIA) ====================

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes
)
from webauthn.helpers import bytes_to_base64url
from core.models import WebAuthnCredential
import secrets


@login_required
@require_http_methods(["GET"])
@csrf_exempt
def webauthn_registration_options(request):
    """
    Gera opções para registro de credencial WebAuthn
    """
    try:
        # Verificar se usuário já tem credencial
        if hasattr(request.user, 'webauthn_credential'):
            return JsonResponse({
                'error': 'Usuário já possui credencial biométrica registrada'
            }, status=400)
        
        # Gerar opções de registro
        options = generate_registration_options(
            rp_id=request.get_host().split(':')[0],  # Remove porta se houver
            rp_name="CashFlow Manager",
            user_id=str(request.user.id),
            user_name=request.user.email,
            user_display_name=request.user.get_full_name() or request.user.email,
            challenge=secrets.token_bytes(32),
        )
        
        # Armazenar challenge na sessão para verificação posterior
        request.session['webauthn_registration_challenge'] = bytes_to_base64url(options.challenge)
        
        return JsonResponse(options_to_json(options))
        
    except Exception as e:
        logger.error(f"Erro ao gerar opções de registro WebAuthn: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def webauthn_registration_verify(request):
    """
    Verifica e registra a credencial WebAuthn
    """
    try:
        data = json.loads(request.body)
        
        # Recuperar challenge da sessão
        challenge_b64 = request.session.get('webauthn_registration_challenge')
        if not challenge_b64:
            return JsonResponse({'error': 'Challenge não encontrado'}, status=400)
        
        # Verificar resposta de registro
        verification = verify_registration_response(
            credential=data,
            expected_challenge=base64url_to_bytes(challenge_b64),
            expected_origin=f"https://{request.get_host().split(':')[0]}",
            expected_rp_id=request.get_host().split(':')[0],
        )
        
        # Salvar credencial
        credential = WebAuthnCredential.objects.create(
            user=request.user,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
            device_name=data.get('device_name', 'Dispositivo Biométrico'),
            device_type='platform',  # Assume platform authenticator
            transports=data.get('transports', []),
        )
        
        # Limpar challenge da sessão
        del request.session['webauthn_registration_challenge']
        
        return JsonResponse({
            'success': True,
            'message': 'Credencial biométrica registrada com sucesso',
            'credential_id': credential.credential_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar registro WebAuthn: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
@csrf_exempt
def webauthn_authentication_options(request):
    """
    Gera opções para autenticação WebAuthn
    """
    try:
        # Verificar se usuário tem credencial
        if not hasattr(request.user, 'webauthn_credential'):
            return JsonResponse({
                'error': 'Nenhuma credencial biométrica registrada'
            }, status=400)
        
        credential = request.user.webauthn_credential
        
        # Gerar opções de autenticação
        options = generate_authentication_options(
            rp_id=request.get_host().split(':')[0],
            challenge=secrets.token_bytes(32),
            allow_credentials=[{
                "type": "public-key",
                "id": credential.credential_id,
            }],
        )
        
        # Armazenar challenge na sessão
        request.session['webauthn_authentication_challenge'] = bytes_to_base64url(options.challenge)
        
        return JsonResponse(options_to_json(options))
        
    except Exception as e:
        logger.error(f"Erro ao gerar opções de autenticação WebAuthn: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def webauthn_authentication_verify(request):
    """
    Verifica a autenticação WebAuthn
    """
    try:
        data = json.loads(request.body)
        
        # Recuperar challenge da sessão
        challenge_b64 = request.session.get('webauthn_authentication_challenge')
        if not challenge_b64:
            return JsonResponse({'error': 'Challenge não encontrado'}, status=400)
        
        credential = request.user.webauthn_credential
        
        # Verificar resposta de autenticação
        verification = verify_authentication_response(
            credential=data,
            expected_challenge=base64url_to_bytes(challenge_b64),
            expected_origin=f"https://{request.get_host().split(':')[0]}",
            expected_rp_id=request.get_host().split(':')[0],
            credential_public_key=credential.public_key,
            credential_current_sign_count=credential.sign_count,
        )
        
        # Atualizar contador de uso
        credential.sign_count = verification.new_sign_count
        credential.mark_used()
        
        # Limpar challenge da sessão
        del request.session['webauthn_authentication_challenge']
        
        # Fazer login do usuário (se necessário)
        from django.contrib.auth import login
        login(request, request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Autenticação biométrica realizada com sucesso',
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'name': request.user.get_full_name(),
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar autenticação WebAuthn: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
@csrf_exempt
def webauthn_remove_credential(request):
    """
    Remove a credencial WebAuthn do usuário
    """
    try:
        if hasattr(request.user, 'webauthn_credential'):
            request.user.webauthn_credential.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Credencial biométrica removida com sucesso'
            })
        else:
            return JsonResponse({
                'error': 'Nenhuma credencial biométrica encontrada'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Erro ao remover credencial WebAuthn: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
