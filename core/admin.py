from django.contrib import admin
from .models import PushSubscription, PushNotificationLog


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

