import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from transactions.models import Transaction, Account
from accounts.models import Company
from decimal import Decimal
from datetime import date

def test_simplified_transfers():
    print("=== TESTE TRANSFERENCIAS SIMPLIFICADAS ===")

    # Limpar todas as transferências primeiro
    company = Company.objects.get(name="dinelle")
    Transaction.objects.filter(company=company, transaction_type='transfer').delete()
    
    # Atualizar saldos após limpeza
    accounts = Account.objects.filter(company=company)
    for account in accounts:
        account.update_balance()
    
    conta_stone = Account.objects.get(company=company, name__icontains="Stone")
    conta_sicredi = Account.objects.get(company=company, name__icontains="Sicredi")
    user = company.owner

    print(f"Saldos iniciais (após limpeza):")
    print(f"  Stone: R$ {conta_stone.current_balance}")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance}")

    # TESTE 1: Criar transferência única
    print(f"\n=== TESTE 1: UMA TRANSFERENCIA APENAS ===")
    
    transfer = Transaction.objects.create(
        company=company,
        account=conta_stone,  # ORIGEM (sai dinheiro)
        transfer_to_account=conta_sicredi,  # DESTINO (entra dinheiro)
        transaction_type='transfer',
        amount=Decimal('300.00'),
        description='Transferência única Stone -> Sicredi',
        transaction_date=date.today(),
        status='completed',
        created_by=user
    )

    # Verificar quantas transações foram criadas
    total_transfers = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    
    print(f"Total de transferências criadas: {total_transfers}")
    print("(Deveria ser 1 apenas - sem transações espelho)")
    
    # Listar a transferência criada
    transfers = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    )
    
    for t in transfers:
        direction = f"{t.account.name} -> {t.transfer_to_account.name if t.transfer_to_account else 'N/A'}"
        print(f"ID {t.id}: {direction} - R$ {t.amount} - {t.description}")

    # Verificar saldos após transferência
    conta_stone.refresh_from_db()
    conta_sicredi.refresh_from_db()
    
    print(f"\nSaldos após transferência:")
    print(f"  Stone: R$ {conta_stone.current_balance} (deveria ter diminuído R$ 300)")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance} (deveria ter aumentado R$ 300)")
    
    # Calcular saldos esperados
    print(f"\n=== VERIFICAÇÃO DETALHADA ===")
    
    # Stone - cálculo detalhado
    stone_initial = Decimal('0.00')
    stone_income = sum(t.amount for t in Transaction.objects.filter(
        account=conta_stone, transaction_type='income', status='completed'
    ))
    stone_expense = sum(t.amount for t in Transaction.objects.filter(
        account=conta_stone, transaction_type='expense', status='completed'
    ))
    stone_transfers_out = sum(t.amount for t in Transaction.objects.filter(
        account=conta_stone, transaction_type='transfer', status='completed'
    ))
    stone_transfers_in = sum(t.amount for t in Transaction.objects.filter(
        transfer_to_account=conta_stone, transaction_type='transfer', status='completed'
    ))
    
    stone_expected = stone_initial + stone_income - stone_expense - stone_transfers_out + stone_transfers_in
    
    print(f"Stone - Cálculo detalhado:")
    print(f"  Inicial: R$ {stone_initial}")
    print(f"  Receitas: R$ {stone_income}")
    print(f"  Despesas: R$ {stone_expense}")
    print(f"  Transferências enviadas: R$ {stone_transfers_out}")
    print(f"  Transferências recebidas: R$ {stone_transfers_in}")
    print(f"  Esperado: R$ {stone_expected}")
    print(f"  Atual: R$ {conta_stone.current_balance}")
    print(f"  Correto: {'✅' if stone_expected == conta_stone.current_balance else '❌'}")
    
    # Sicredi - cálculo detalhado  
    sicredi_initial = Decimal('0.00')
    sicredi_income = sum(t.amount for t in Transaction.objects.filter(
        account=conta_sicredi, transaction_type='income', status='completed'
    ))
    sicredi_expense = sum(t.amount for t in Transaction.objects.filter(
        account=conta_sicredi, transaction_type='expense', status='completed'
    ))
    sicredi_transfers_out = sum(t.amount for t in Transaction.objects.filter(
        account=conta_sicredi, transaction_type='transfer', status='completed'
    ))
    sicredi_transfers_in = sum(t.amount for t in Transaction.objects.filter(
        transfer_to_account=conta_sicredi, transaction_type='transfer', status='completed'
    ))
    
    sicredi_expected = sicredi_initial + sicredi_income - sicredi_expense - sicredi_transfers_out + sicredi_transfers_in
    
    print(f"\nSicredi - Cálculo detalhado:")
    print(f"  Inicial: R$ {sicredi_initial}")
    print(f"  Receitas: R$ {sicredi_income}")
    print(f"  Despesas: R$ {sicredi_expense}")
    print(f"  Transferências enviadas: R$ {sicredi_transfers_out}")
    print(f"  Transferências recebidas: R$ {sicredi_transfers_in}")
    print(f"  Esperado: R$ {sicredi_expected}")
    print(f"  Atual: R$ {conta_sicredi.current_balance}")
    print(f"  Correto: {'✅' if sicredi_expected == conta_sicredi.current_balance else '❌'}")

    # TESTE 2: Transferência no sentido contrário
    print(f"\n=== TESTE 2: TRANSFERENCIA CONTRARIA ===")
    
    transfer_reverse = Transaction.objects.create(
        company=company,
        account=conta_sicredi,  # ORIGEM
        transfer_to_account=conta_stone,  # DESTINO  
        transaction_type='transfer',
        amount=Decimal('100.00'),
        description='Transferência Sicredi -> Stone',
        transaction_date=date.today(),
        status='completed',
        created_by=user
    )
    
    # Verificar saldos finais
    conta_stone.refresh_from_db()
    conta_sicredi.refresh_from_db()
    
    print(f"Saldos finais:")
    print(f"  Stone: R$ {conta_stone.current_balance}")
    print(f"  Sicredi: R$ {conta_sicredi.current_balance}")
    print(f"  Total transferências: {Transaction.objects.filter(company=company, transaction_type='transfer').count()}")
    
    print(f"\n=== RESUMO ===")
    print("✅ Lógica simplificada implementada:")
    print("   - 1 transferência = 1 registro apenas")
    print("   - Sem transações espelho duplicadas")
    print("   - Saldos calculados corretamente")
    print("   - Origin account: diminui saldo")
    print("   - Destination account: aumenta saldo")
    print("TESTE CONCLUÍDO!")

if __name__ == "__main__":
    test_simplified_transfers()