from django.core.management.base import BaseCommand
from transactions.models import Account


class Command(BaseCommand):
    help = 'Atualiza o saldo atual de todas as contas baseado no saldo inicial e transações'

    def handle(self, *args, **options):
        accounts = Account.objects.filter(is_active=True)
        updated_count = 0
        
        for account in accounts:
            old_balance = account.current_balance
            account.update_balance()
            new_balance = account.current_balance
            
            if old_balance != new_balance:
                updated_count += 1
                self.stdout.write(
                    f'Conta "{account.name}": {old_balance} → {new_balance}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Sucesso! {updated_count} contas atualizadas.')
        )