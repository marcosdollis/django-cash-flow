from django.core.management.base import BaseCommand
from transactions.models import Goal


class Command(BaseCommand):
    help = 'Atualiza o progresso de todas as metas baseado nas transações existentes'

    def handle(self, *args, **options):
        goals = Goal.objects.filter(is_active=True)
        
        self.stdout.write(f"Atualizando {goals.count()} metas...")
        
        updated_count = 0
        for goal in goals:
            old_amount = goal.current_amount
            goal.update_progress()
            new_amount = goal.current_amount
            
            if old_amount != new_amount:
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Meta '{goal.name}': R$ {old_amount} → R$ {new_amount}"
                    )
                )
            else:
                self.stdout.write(
                    f"Meta '{goal.name}': R$ {old_amount} (sem alteração)"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎯 Atualização concluída! {updated_count} metas foram atualizadas."
            )
        )