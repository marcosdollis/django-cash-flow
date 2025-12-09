from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction, Account, Goal


@receiver(post_save, sender=Transaction)
def update_account_balance_on_transaction_save(sender, instance, created, **kwargs):
    """Atualiza o saldo da conta quando uma transação é salva"""
    if instance.status == 'completed':
        # Atualizar conta de origem (se existir)
        if hasattr(instance, 'account') and instance.account:
            instance.account.update_balance()
        
        # Para transferências, atualizar também a conta de destino
        if instance.transaction_type == 'transfer' and instance.transfer_to_account:
            instance.transfer_to_account.update_balance()
        
        # Atualizar progresso das metas relacionadas à categoria desta transação
        if instance.category:
            related_goals = Goal.objects.filter(
                company=instance.company,
                category=instance.category,
                is_active=True
            )
            for goal in related_goals:
                goal.update_progress()


@receiver(post_delete, sender=Transaction)
def update_account_balance_on_transaction_delete(sender, instance, **kwargs):
    """Atualiza o saldo da conta quando uma transação é excluída"""
    if instance.status == 'completed':
        # Atualizar conta de origem (se existir)
        if hasattr(instance, 'account') and instance.account:
            instance.account.update_balance()
        
        # Para transferências, atualizar também a conta de destino
        if instance.transaction_type == 'transfer' and instance.transfer_to_account:
            instance.transfer_to_account.update_balance()
        
        # Atualizar progresso das metas relacionadas à categoria desta transação
        if instance.category:
            related_goals = Goal.objects.filter(
                company=instance.company,
                category=instance.category,
                is_active=True
            )
            for goal in related_goals:
                goal.update_progress()