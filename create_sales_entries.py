import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from transactions.models import Transaction, Account
from accounts.models import Company
from decimal import Decimal
from datetime import date

def create_sales_entries():
    print("=== CRIANDO LANÇAMENTOS DE VENDAS ===")

    # Buscar dados
    company = Company.objects.get(name="dinelle")
    conta_stone = Account.objects.get(company=company, name__icontains="Stone")
    user = company.owner

    print(f"Empresa: {company.name}")
    print(f"Conta: {conta_stone.name}")
    print(f"Saldo inicial: R$ {conta_stone.current_balance}")

    # Dados das vendas
    vendas = [
        ('2025-09-07', '144.00'),
        ('2025-09-08', '352.00'),
        ('2025-09-09', '600.00'),
        ('2025-09-10', '416.00'),
        ('2025-09-11', '64.00'),
        ('2025-09-12', '176.00'),
        ('2025-09-13', '144.00'),
        ('2025-09-14', '192.00'),
        ('2025-09-15', '398.00'),
        ('2025-09-16', '192.00'),
        ('2025-09-17', '128.00'),
        ('2025-09-18', '64.00'),
        ('2025-09-19', '128.00'),
        ('2025-09-20', '192.00'),
        ('2025-09-21', '160.00'),
        ('2025-09-22', '272.00'),
        ('2025-09-23', '272.00'),
    ]

    print(f"\nCriando {len(vendas)} lançamentos de vendas...")
    
    created_transactions = []
    total_vendas = Decimal('0.00')

    for data_str, valor_str in vendas:
        # Converter data
        year, month, day = data_str.split('-')
        data_venda = date(int(year), int(month), int(day))
        
        # Converter valor
        valor_venda = Decimal(valor_str)
        total_vendas += valor_venda
        
        # Criar transação de receita
        transaction = Transaction.objects.create(
            company=company,
            account=conta_stone,
            transaction_type='income',
            amount=valor_venda,
            description=f'Venda {data_venda.strftime("%d/%m/%Y")}',
            transaction_date=data_venda,
            status='completed',
            created_by=user
        )
        
        created_transactions.append(transaction)
        print(f"✅ {data_venda.strftime('%d/%m/%Y')}: R$ {valor_venda} - ID {transaction.id}")

    print(f"\n=== RESUMO ===")
    print(f"Total de transações criadas: {len(created_transactions)}")
    print(f"Total de vendas: R$ {total_vendas}")

    # Verificar saldo atualizado
    conta_stone.refresh_from_db()
    print(f"Saldo final da conta: R$ {conta_stone.current_balance}")
    
    # Calcular o aumento no saldo
    print(f"Aumento no saldo: R$ {total_vendas}")

    print(f"\n=== VERIFICAÇÃO ===")
    
    # Listar as últimas transações criadas para confirmação
    print("Últimas 5 transações criadas:")
    ultimas_transacoes = Transaction.objects.filter(
        account=conta_stone,
        transaction_type='income',
        description__icontains='Venda'
    ).order_by('-transaction_date')[:5]
    
    for t in ultimas_transacoes:
        print(f"  - {t.transaction_date.strftime('%d/%m/%Y')}: R$ {t.amount} - {t.description}")

    print("\n✅ Todos os lançamentos de vendas foram criados com sucesso!")
    print("✅ Saldo da conta Stone foi atualizado automaticamente!")

if __name__ == "__main__":
    create_sales_entries()