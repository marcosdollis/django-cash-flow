from django.db import models
from django.conf import settings
from django.utils import timezone


class PushSubscription(models.Model):
    """Armazena as subscrições de push notifications dos usuários"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        verbose_name='Usuário'
    )
    
    # Dados da subscription do navegador
    endpoint = models.URLField('Endpoint', max_length=500, unique=True)
    p256dh = models.CharField('Chave P256DH', max_length=255)
    auth = models.CharField('Auth Secret', max_length=255)
    
    # Metadados
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    device_name = models.CharField('Nome do Dispositivo', max_length=100, blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    # Timestamps
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    last_used = models.DateTimeField('Último Uso', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Subscrição Push'
        verbose_name_plural = 'Subscrições Push'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['endpoint']),
        ]
    
    def __str__(self):
        device = self.device_name or 'Dispositivo'
        return f"{self.user.email} - {device}"
    
    def mark_used(self):
        """Marca a subscrição como usada recentemente"""
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])


class PushNotificationLog(models.Model):
    """Log de notificações push enviadas"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sent', 'Enviada'),
        ('failed', 'Falhou'),
        ('expired', 'Expirada'),
    ]
    
    subscription = models.ForeignKey(
        PushSubscription,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Subscrição'
    )
    
    # Conteúdo da notificação
    title = models.CharField('Título', max_length=200)
    body = models.TextField('Mensagem')
    icon = models.CharField('Ícone', max_length=200, default='/static/icons/icon-192x192.png')
    url = models.URLField('URL', max_length=500, blank=True)
    
    # Status e resultado
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField('Mensagem de Erro', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    sent_at = models.DateTimeField('Enviado em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subscription.user.email} ({self.status})"
