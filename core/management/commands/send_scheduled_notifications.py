from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import ScheduledNotification
from api.views import send_push_notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Envia notificações push agendadas para todos os usuários'

    def handle(self, *args, **options):
        notifications_sent = 0
        users_notified = 0
        
        # Buscar notificações que devem ser enviadas agora
        scheduled_notifications = ScheduledNotification.objects.filter(is_active=True)
        
        self.stdout.write(f"Encontradas {scheduled_notifications.count()} notificações agendadas ativas")
        
        for notification in scheduled_notifications:
            if notification.should_send_now():
                self.stdout.write(f"Enviando: {notification.title}")
                
                # Enviar para todos os usuários com subscrições ativas
                users_with_subscriptions = User.objects.filter(
                    push_subscriptions__is_active=True
                ).distinct()
                
                users_notified_for_this_notification = 0
                
                for user in users_with_subscriptions:
                    try:
                        results = send_push_notification(
                            user=user,
                            title=notification.title,
                            body=notification.body,
                            url=notification.url,
                            icon=notification.icon
                        )
                        
                        if results['sent'] > 0:
                            users_notified_for_this_notification += 1
                            notifications_sent += results['sent']
                            
                    except Exception as e:
                        self.stderr.write(f"Erro ao enviar para {user.email}: {e}")
                
                # Marcar como enviada
                notification.mark_sent()
                
                self.stdout.write(f"  Notificação enviada para {users_notified_for_this_notification} usuários")
                users_notified += users_notified_for_this_notification
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído! {notifications_sent} notificações enviadas para {users_notified} usuários"
            )
        )