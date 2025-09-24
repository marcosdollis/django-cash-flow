import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from transactions.models import Transaction, Account
from accounts.models import Company
from decimal import Decimal
from datetime import date

def test_corrected_transfers():
    print("=== TESTE TRANSFERENCIAS CORRIGIDAS ===")

    # Limpar transferências existentes primeiro
    company = Company.objects.get(name="dinelle")
    Transaction.objects.filter(company=company, transaction_type='transfer').delete()
    
    # Atualizar saldos após limpeza
    accounts = Account.objects.filter(company=company)
    for account in accounts:
        account.update_balance()
    
    conta_stone = Account.objects.get(company=company, name__icontains="Stone")
    conta_sicredi = Account.objects.get(company=company, name__icontains="Sicredi")
    user = company.owner

    print(f"Saldos iniciais (pós limpeza):")
    print(f"  Stone: R$ {conta_stone.current_balance}")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance}")

    # TESTE 1: Criar transferência PENDING
    print(f"\n=== TESTE 1: TRANSFERENCIA PENDING ===")
    
    transfer_pending = Transaction.objects.create(
        company=company,
        account=conta_stone,
        transfer_to_account=conta_sicredi,
        transaction_type='transfer',
        amount=Decimal('200.00'),
        description='Teste pending corrigido',
        transaction_date=date.today(),
        status='pending',
        created_by=user
    )

    # Verificar quantas transações foram criadas
    total_transfers = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    
    print(f"Total de transferências criadas: {total_transfers}")
    
    # Listar transferências criadas
    transfers = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).order_by('created_at')
    
    for i, t in enumerate(transfers, 1):
        direction = f"{t.account.name} -> {t.transfer_to_account.name if t.transfer_to_account else 'N/A'}"
        print(f"{i}. ID {t.id}: {direction} - R$ {t.amount} - {t.description} - {t.status}")

    # Verificar saldos (pending não deve afetar saldos)
    conta_stone.refresh_from_db()
    conta_sicredi.refresh_from_db()
    
    print(f"\nSaldos após transferência PENDING:")
    print(f"  Stone: R$ {conta_stone.current_balance}")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance}")
    print("(Saldos não devem mudar com status pending)")

    # TESTE 2: Aprovar transferência
    print(f"\n=== TESTE 2: APROVANDO TRANSFERENCIA ===")
    
    transfers_before_approval = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    
    print(f"Transferências antes aprovação: {transfers_before_approval}")
    
    # Aprovar a transferência
    transfer_pending.status = 'completed'
    transfer_pending.save()
    
    transfers_after_approval = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    
    print(f"Transferências após aprovação: {transfers_after_approval}")
    print(f"Novas criadas na aprovação: {transfers_after_approval - transfers_before_approval}")
    
    # Verificar status das transferências
    print(f"\nStatus das transferências após aprovação:")
    all_transfers = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).order_by('created_at')
    
    for i, t in enumerate(all_transfers, 1):
        direction = f"{t.account.name} -> {t.transfer_to_account.name if t.transfer_to_account else 'N/A'}"
        print(f"{i}. ID {t.id}: {direction} - R$ {t.amount} - {t.status}")
    
    # Verificar saldos finais
    conta_stone.refresh_from_db()
    conta_sicredi.refresh_from_db()
    
    print(f"\nSaldos finais:")
    print(f"  Stone: R$ {conta_stone.current_balance}")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance}")

    # TESTE 3: Criar transferência já COMPLETED
    print(f"\n=== TESTE 3: TRANSFERENCIA DIRETAMENTE COMPLETED ===")
    
    transfer_completed = Transaction.objects.create(
        company=company,
        account=conta_stone,
        transfer_to_account=conta_sicredi,
        transaction_type='transfer',
        amount=Decimal('50.00'),
        description='Teste direto completed',
        transaction_date=date.today(),
        status='completed',
        created_by=user
    )
    
    # Verificar resultado
    final_transfers = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    
    print(f"Total de transferências final: {final_transfers}")
    
    conta_stone.refresh_from_db()
    conta_sicredi.refresh_from_db()
    
    print(f"\nSaldos após segunda transferência:")
    print(f"  Stone: R$ {conta_stone.current_balance}")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance}")

    print(f"\n=== RESUMO DOS TESTES ===")
    print("1. Transferência PENDING deve criar 2 registros (origem + espelho)")
    print("2. Aprovação NÃO deve criar registros adicionais")
    print("3. Espelho deve ter mesmo status que a original")
    print("4. Transferência COMPLETED direta deve funcionar")
    print("TESTE CONCLUÍDO!")

if __name__ == "__main__":
    test_corrected_transfers()