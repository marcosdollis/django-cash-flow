from django.contrib import admin
from .models import PushSubscription, PushNotificationLog, ScheduledNotification, WebAuthnCredential


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active', 'created_at', 'device_name']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'device_name']
    readonly_fields = ['endpoint', 'p256dh', 'auth', 'user_agent', 'created_at', 'updated_at', 'last_used']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'device_name', 'is_active')
        }),
        ('Dados da Subscrição', {
            'fields': ('endpoint', 'p256dh', 'auth'),
            'classes': ('collapse',)
        }),
        ('Informações Técnicas', {
            'fields': ('user_agent', 'created_at', 'updated_at', 'last_used'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Subscrições são criadas via API, não manualmente
        return False


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_user_email', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at', 'sent_at']
    search_fields = ['title', 'body', 'subscription__user__email']
    readonly_fields = ['subscription', 'title', 'body', 'icon', 'url', 
                      'status', 'error_message', 'created_at', 'sent_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notificação', {
            'fields': ('subscription', 'title', 'body', 'icon', 'url')
        }),
        ('Status', {
            'fields': ('status', 'error_message', 'created_at', 'sent_at')
        }),
    )
    
    def get_user_email(self, obj):
        return obj.subscription.user.email
    get_user_email.short_description = 'Usuário'
    get_user_email.admin_order_field = 'subscription__user__email'
    
    def has_add_permission(self, request):
        # Logs são criados automaticamente
        return False
    
    def has_change_permission(self, request, obj=None):
        # Logs são read-only
        return False


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_time', 'is_active', 'last_sent', 'next_send']
    list_filter = ['is_active', 'scheduled_time']
    search_fields = ['title', 'body']
    readonly_fields = ['last_sent', 'next_send']
    
    fieldsets = (
        ('Configuração', {
            'fields': ('title', 'body', 'scheduled_time', 'is_active')
        }),
        ('Informações', {
            'fields': ('icon', 'url', 'last_sent', 'next_send'),
            'classes': ('collapse',)
        }),
    )
    
    def next_send(self, obj):
        from django.utils import timezone
        now = timezone.now()
        today = now.date()
        scheduled_time = obj.scheduled_time
        
        # Cria datetime para hoje com o horário agendado
        next_send = timezone.datetime.combine(today, scheduled_time)
        next_send = timezone.make_aware(next_send)
        
        # Se já passou hoje, agenda para amanhã
        if next_send <= now:
            next_send = next_send + timezone.timedelta(days=1)
        
        return next_send.strftime('%d/%m/%Y %H:%M')
    
    next_send.short_description = 'Próximo Envio'


@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'device_type', 'is_active', 'last_used', 'created_at']
    list_filter = ['is_active', 'device_type', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'device_name']
    readonly_fields = ['credential_id', 'public_key', 'sign_count', 'created_at', 'last_used']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'is_active')
        }),
        ('Dispositivo', {
            'fields': ('device_name', 'device_type', 'transports')
        }),
        ('Credencial', {
            'fields': ('credential_id', 'public_key', 'sign_count'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'last_used'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Credenciais são criadas via API/WebAuthn
        return False

