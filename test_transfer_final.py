import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from transactions.models import Transaction, Account
from accounts.models import Company
from decimal import Decimal
from datetime import date

def test_transfer_fix():
    print("=== TESTANDO NOVA TRANSFERÊNCIA CORRIGIDA ===")

    # Buscar dados para teste
    company = Company.objects.get(name="dinelle")
    conta_stone = Account.objects.get(company=company, name__icontains="Stone")
    conta_sicredi = Account.objects.get(company=company, name__icontains="Sicredi")
    user = company.owner

    print(f"Saldos antes:")
    print(f"  Stone: R$ {conta_stone.current_balance}")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance}")

    # Contar transferências antes
    transfers_before = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    
    print(f"\nTransferências antes: {transfers_before}")

    # Criar uma nova transferência
    valor_teste = Decimal('50.00')

    print(f"\nCriando transferência de R$ {valor_teste}")
    print(f"De: {conta_stone.name} para {conta_sicredi.name}")

    try:
        # Criar transação de transferência
        transfer = Transaction.objects.create(
            company=company,
            account=conta_stone,
            transfer_to_account=conta_sicredi,
            transaction_type='transfer',
            amount=valor_teste,
            description='Teste transferência corrigida',
            transaction_date=date.today(),
            status='completed',
            created_by=user
        )

        print(f"Transferência criada - ID: {transfer.id}")

        # Recarregar saldos
        conta_stone.refresh_from_db()
        conta_sicredi.refresh_from_db()

        print(f"\nSaldos depois:")
        print(f"  Stone: R$ {conta_stone.current_balance}")
        print(f"  Sicredi: R$ {conta_sicredi.current_balance}")

        # Verificar quantas transações de transferência foram criadas
        transfers_after = Transaction.objects.filter(
            company=company,
            transaction_type='transfer'
        ).count()

        print(f"\nTransferências depois: {transfers_after}")
        print(f"Novas transferências criadas: {transfers_after - transfers_before}")

        # Listar todas as transferências
        print(f"\n=== TODAS AS TRANSFERENCIAS ===")
        all_transfers = Transaction.objects.filter(
            company=company,
            transaction_type='transfer'
        ).order_by('created_at')

        for i, t in enumerate(all_transfers, 1):
            direction = f"{t.account.name} -> {t.transfer_to_account.name if t.transfer_to_account else 'N/A'}"
            print(f"{i}. ID {t.id}: {direction} - R$ {t.amount} - {t.description} ({t.status})")

        # Teste: alterar status de pending para completed
        print(f"\n=== TESTE ALTERAÇÃO DE STATUS ===")
        
        # Criar uma transferência com status pending
        transfer_pending = Transaction.objects.create(
            company=company,
            account=conta_stone,
            transfer_to_account=conta_sicredi,
            transaction_type='transfer',
            amount=Decimal('25.00'),
            description='Teste status pending->completed',
            transaction_date=date.today(),
            status='pending',
            created_by=user
        )
        
        print(f"Transferência pending criada - ID: {transfer_pending.id}")
        
        transfers_before_status_change = Transaction.objects.filter(
            company=company,
            transaction_type='transfer'
        ).count()
        
        # Alterar status para completed
        transfer_pending.status = 'completed'
        transfer_pending.save()
        
        transfers_after_status_change = Transaction.objects.filter(
            company=company,
            transaction_type='transfer'
        ).count()
        
        print(f"Transferências antes da mudança de status: {transfers_before_status_change}")
        print(f"Transferências depois da mudança de status: {transfers_after_status_change}")
        
        if transfers_after_status_change == transfers_before_status_change:
            print("✅ Mudança de status NÃO criou duplicatas")
        else:
            print("❌ Mudança de status criou duplicatas!")

        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")

    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transfer_fix()