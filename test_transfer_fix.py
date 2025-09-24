import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Company
from transactions.models import Account, Transaction
from decimal import Decimal

User = get_user_model()

def test_transfer_correction():
    print("=== TESTE DE CORREÇÃO DE TRANSFERÊNCIAS ===")
    
    # Buscar dados de teste
    try:
        company = Company.objects.get(name="dinelle")
        conta_stone = Account.objects.get(company=company, name__icontains="Stone")
        conta_sicredi = Account.objects.get(company=company, name__icontains="Sicredi")
        user = company.owner
        
        print(f"Empresa: {company.name}")
        print(f"Conta origem: {conta_stone.name} (Saldo: R$ {conta_stone.current_balance})")
        print(f"Conta destino: {conta_sicredi.name} (Saldo: R$ {conta_sicredi.current_balance})")
        
        # Saldos antes da transferência
        saldo_stone_antes = conta_stone.current_balance
        saldo_sicredi_antes = conta_sicredi.current_balance
        
        # Criar uma nova transferência de teste
        valor_transferencia = Decimal('100.00')
        
        print(f"\nCriando transferência de R$ {valor_transferencia}")
        print(f"De: {conta_stone.name} para: {conta_sicredi.name}")
        
        transfer = Transaction.objects.create(
            company=company,
            account=conta_stone,
            transfer_to_account=conta_sicredi,
            transaction_type='transfer',
            amount=valor_transferencia,
            description='Teste de transferência corrigida',
            status='completed',
            created_by=user,
            transaction_date='2025-09-23'
        )
        
        # Recarregar saldos
        conta_stone.refresh_from_db()
        conta_sicredi.refresh_from_db()
        
        saldo_stone_depois = conta_stone.current_balance
        saldo_sicredi_depois = conta_sicredi.current_balance
        
        print(f"\n=== RESULTADOS ===")
        print(f"Conta Stone:")
        print(f"  Antes: R$ {saldo_stone_antes}")
        print(f"  Depois: R$ {saldo_stone_depois}")
        print(f"  Diferença: R$ {saldo_stone_depois - saldo_stone_antes}")
        
        print(f"Conta Sicredi:")
        print(f"  Antes: R$ {saldo_sicredi_antes}")
        print(f"  Depois: R$ {saldo_sicredi_depois}")
        print(f"  Diferença: R$ {saldo_sicredi_depois - saldo_sicredi_antes}")
        
        # Verificar se foi criada a transação espelho
        mirror_transactions = Transaction.objects.filter(
            account=conta_sicredi,
            description__contains="Transferência de"
        ).order_by('-created_at')[:1]
        
        if mirror_transactions:
            mirror = mirror_transactions[0]
            print(f"\n=== TRANSAÇÃO ESPELHO ===")
            print(f"Conta: {mirror.account.name}")
            print(f"Tipo: {mirror.transaction_type}")
            print(f"Valor: R$ {mirror.amount}")
            print(f"Descrição: {mirror.description}")
            
        # Verificar todas as transações de transferência nas duas contas
        print(f"\n=== TODAS AS TRANSFERÊNCIAS ===")
        print("Conta Stone (saídas):")
        for t in Transaction.objects.filter(account=conta_stone, transaction_type='transfer'):
            print(f"  - {t.transaction_type}: R$ {t.amount} - {t.description}")
            
        print("Conta Sicredi (entradas):")
        for t in Transaction.objects.filter(account=conta_sicredi, transaction_type='transfer'):
            print(f"  - {t.transaction_type}: R$ {t.amount} - {t.description}")
        
        # Teste: Verificar se os valores não estão sendo contados em dobro no fluxo de caixa
        print(f"\n=== ANÁLISE FLUXO DE CAIXA ===")
        
        # Contar receitas reais (não transferências)
        receitas_stone = Transaction.objects.filter(
            account=conta_stone, 
            transaction_type='income'
        ).count()
        
        receitas_sicredi = Transaction.objects.filter(
            account=conta_sicredi, 
            transaction_type='income'  
        ).count()
        
        print(f"Receitas reais na Stone: {receitas_stone}")
        print(f"Receitas reais na Sicredi: {receitas_sicredi}")
        
        # Total de transferências (devem ser todas tipo 'transfer' agora)
        total_transfers = Transaction.objects.filter(
            company=company,
            transaction_type='transfer'
        ).count()
        
        print(f"Total de transações de transferência: {total_transfers}")
        
        print("\n✅ TESTE CONCLUÍDO - Verifique se os valores estão corretos")
        
    except Exception as e:
        print(f"Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transfer_correction()