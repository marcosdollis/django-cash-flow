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


class ScheduledNotification(models.Model):
    """Modelo para notificações push agendadas"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
    ]
    
    title = models.CharField('Título', max_length=100)
    body = models.TextField('Mensagem')
    icon = models.CharField('Ícone', max_length=100, default='/static/icons/icon-192x192.png')
    url = models.CharField('URL', max_length=200, blank=True)
    
    # Agendamento
    frequency = models.CharField('Frequência', max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    scheduled_time = models.TimeField('Horário')
    is_active = models.BooleanField('Ativo', default=True)
    
    # Controle de envio
    last_sent = models.DateTimeField('Último Envio', null=True, blank=True)
    next_send = models.DateTimeField('Próximo Envio', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Notificação Agendada'
        verbose_name_plural = 'Notificações Agendadas'
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_time.strftime('%H:%M')}"
    
    def should_send_now(self):
        """Verifica se deve enviar a notificação agora"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        
        # Para notificações diárias, verifica se é a hora certa e não foi enviada hoje
        if self.frequency == 'daily':
            if now.time() >= self.scheduled_time:
                if self.last_sent:
                    # Verifica se já foi enviada hoje
                    return self.last_sent.date() < now.date()
                else:
                    # Nunca foi enviada, pode enviar
                    return True
        
        return False
    
    def mark_sent(self):
        """Marca como enviada e calcula próximo envio"""
        now = timezone.now()
        self.last_sent = now
        
        if self.frequency == 'daily':
            # Próximo envio amanhã na mesma hora
            tomorrow = now + timezone.timedelta(days=1)
            self.next_send = timezone.datetime.combine(tomorrow.date(), self.scheduled_time)
        
        self.save(update_fields=['last_sent', 'next_send'])


class WebAuthnCredential(models.Model):
    """
    Modelo para armazenar credenciais WebAuthn (autenticação biométrica)
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webauthn_credential'
    )
    
    # Dados da credencial
    credential_id = models.CharField(max_length=255, unique=True)
    public_key = models.TextField()  # Chave pública em formato PEM
    sign_count = models.PositiveIntegerField(default=0)
    
    # Metadados
    device_name = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # 'platform' ou 'cross-platform'
    transports = models.JSONField(default=list, blank=True)  # ['usb', 'nfc', 'ble', 'internal']
    
    # Controle
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Credencial WebAuthn'
        verbose_name_plural = 'Credenciais WebAuthn'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.device_name or 'Dispositivo'}"
    
    def mark_used(self):
        """Atualiza o contador de uso"""
        from django.utils import timezone
        self.sign_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['sign_count', 'last_used'])
