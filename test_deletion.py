import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from transactions.models import Transaction, Account
from accounts.models import Company
from decimal import Decimal
from datetime import date

def test_transaction_deletion():
    print("=== TESTE DE EXCLUSÃO DE TRANSAÇÕES ===")

    # Buscar dados para teste
    company = Company.objects.get(name="dinelle")
    conta_stone = Account.objects.get(company=company, name__icontains="Stone")
    conta_sicredi = Account.objects.get(company=company, name__icontains="Sicredi")
    user = company.owner

    print(f"=== TESTE 1: EXCLUSÃO DE RECEITA ===")
    print(f"Saldo inicial Stone: R$ {conta_stone.current_balance}")

    # Criar uma receita de teste
    receita = Transaction.objects.create(
        company=company,
        account=conta_stone,
        transaction_type='income',
        amount=Decimal('100.00'),
        description='Receita de teste para exclusão',
        transaction_date=date.today(),
        status='completed',
        created_by=user
    )

    # Recarregar saldo após criação
    conta_stone.refresh_from_db()
    saldo_apos_receita = conta_stone.current_balance
    print(f"Saldo após criar receita: R$ {saldo_apos_receita}")

    # Deletar a receita
    receita_id = receita.id
    receita.delete()
    
    # Recarregar saldo após exclusão
    conta_stone.refresh_from_db()
    saldo_apos_exclusao = conta_stone.current_balance
    print(f"Saldo após excluir receita: R$ {saldo_apos_exclusao}")
    
    if saldo_apos_exclusao == saldo_apos_receita - Decimal('100.00'):
        print("✅ Exclusão de receita atualizou o saldo corretamente")
    else:
        print("❌ Exclusão de receita NÃO atualizou o saldo")

    print(f"\n=== TESTE 2: EXCLUSÃO DE DESPESA ===")
    saldo_inicial_teste2 = conta_stone.current_balance
    print(f"Saldo inicial: R$ {saldo_inicial_teste2}")

    # Criar uma despesa de teste
    despesa = Transaction.objects.create(
        company=company,
        account=conta_stone,
        transaction_type='expense',
        amount=Decimal('50.00'),
        description='Despesa de teste para exclusão',
        transaction_date=date.today(),
        status='completed',
        created_by=user
    )

    # Recarregar saldo após criação
    conta_stone.refresh_from_db()
    saldo_apos_despesa = conta_stone.current_balance
    print(f"Saldo após criar despesa: R$ {saldo_apos_despesa}")

    # Deletar a despesa
    despesa.delete()
    
    # Recarregar saldo após exclusão
    conta_stone.refresh_from_db()
    saldo_apos_exclusao_despesa = conta_stone.current_balance
    print(f"Saldo após excluir despesa: R$ {saldo_apos_exclusao_despesa}")
    
    if saldo_apos_exclusao_despesa == saldo_apos_despesa + Decimal('50.00'):
        print("✅ Exclusão de despesa atualizou o saldo corretamente")
    else:
        print("❌ Exclusão de despesa NÃO atualizou o saldo")

    print(f"\n=== TESTE 3: EXCLUSÃO DE TRANSFERÊNCIA ===")
    saldo_stone_inicial = conta_stone.current_balance
    saldo_sicredi_inicial = conta_sicredi.current_balance
    
    print(f"Saldos iniciais:")
    print(f"  Stone: R$ {saldo_stone_inicial}")
    print(f"  Sicredi: R$ {saldo_sicredi_inicial}")

    # Criar uma transferência de teste
    transferencia = Transaction.objects.create(
        company=company,
        account=conta_stone,
        transfer_to_account=conta_sicredi,
        transaction_type='transfer',
        amount=Decimal('75.00'),
        description='Transferência de teste para exclusão',
        transaction_date=date.today(),
        status='completed',
        created_by=user
    )

    # Recarregar saldos após criação
    conta_stone.refresh_from_db()
    conta_sicredi.refresh_from_db()
    saldo_stone_apos_transfer = conta_stone.current_balance
    saldo_sicredi_apos_transfer = conta_sicredi.current_balance
    
    print(f"Saldos após transferência:")
    print(f"  Stone: R$ {saldo_stone_apos_transfer}")
    print(f"  Sicredi: R$ {saldo_sicredi_apos_transfer}")

    # Contar quantas transferências existem antes da exclusão
    transfers_antes = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    print(f"Transferências antes da exclusão: {transfers_antes}")

    # Deletar a transferência (deve deletar também a transação espelho)
    transferencia.delete()
    
    # Contar quantas transferências existem após a exclusão
    transfers_depois = Transaction.objects.filter(
        company=company,
        transaction_type='transfer'
    ).count()
    print(f"Transferências após a exclusão: {transfers_depois}")
    
    # Recarregar saldos após exclusão
    conta_stone.refresh_from_db()
    conta_sicredi.refresh_from_db()
    saldo_stone_final = conta_stone.current_balance
    saldo_sicredi_final = conta_sicredi.current_balance
    
    print(f"Saldos finais:")
    print(f"  Stone: R$ {saldo_stone_final}")
    print(f"  Sicredi: R$ {saldo_sicredi_final}")
    
    # Verificar se os saldos voltaram ao estado inicial
    stone_correto = saldo_stone_final == saldo_stone_inicial
    sicredi_correto = saldo_sicredi_final == saldo_sicredi_inicial
    espelho_deletado = transfers_depois == transfers_antes - 2  # Deve ter deletado 2 (original + espelho)
    
    if stone_correto and sicredi_correto and espelho_deletado:
        print("✅ Exclusão de transferência funcionou corretamente")
        print("  - Saldos voltaram ao estado inicial")
        print("  - Transação espelho foi deletada automaticamente")
    else:
        print("❌ Exclusão de transferência teve problemas:")
        if not stone_correto:
            print(f"  - Saldo Stone incorreto: esperado {saldo_stone_inicial}, atual {saldo_stone_final}")
        if not sicredi_correto:
            print(f"  - Saldo Sicredi incorreto: esperado {saldo_sicredi_inicial}, atual {saldo_sicredi_final}")
        if not espelho_deletado:
            print(f"  - Transação espelho não foi deletada: {transfers_antes} -> {transfers_depois}")

    print(f"\n=== RESUMO DOS TESTES ===")
    print("1. Exclusão de receitas: Saldo reduz automaticamente")
    print("2. Exclusão de despesas: Saldo aumenta automaticamente")
    print("3. Exclusão de transferências: Ambas as contas e transação espelho são atualizadas")
    print("✅ Todos os testes de exclusão concluídos!")

if __name__ == "__main__":
    test_transaction_deletion()