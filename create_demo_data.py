#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Company
from transactions.models import Transaction, Account, Category

User = get_user_model()

# Pegar usuário admin e empresa
admin_user = User.objects.get(username='admin')
company = admin_user.companies.first()

print(f"Criando dados demo para empresa: {company.name}")

# Criar conta se não existir
account, created = Account.objects.get_or_create(
    company=company,
    name="Caixa Principal",
    defaults={
        'account_type': 'checking',
        'initial_balance': Decimal('10000.00'),
        'current_balance': Decimal('10000.00'),
    }
)

if created:
    print(f"✅ Conta criada: {account.name}")

# Criar categorias se não existirem
income_cat, created = Category.objects.get_or_create(
    company=company,
    name="Vendas",
    defaults={
        'category_type': 'income',
        'description': 'Receitas de vendas',
    }
)

expense_cat, created = Category.objects.get_or_create(
    company=company,
    name="Despesas Operacionais",
    defaults={
        'category_type': 'expense',
        'description': 'Gastos operacionais',
    }
)

# Criar algumas transações de exemplo
base_date = datetime.now().date()

transactions_data = [
    # Receitas
    (base_date - timedelta(days=20), 'income', Decimal('5000.00'), 'Venda de produtos', income_cat),
    (base_date - timedelta(days=15), 'income', Decimal('3000.00'), 'Prestação de serviços', income_cat),
    (base_date - timedelta(days=10), 'income', Decimal('2500.00'), 'Venda online', income_cat),
    (base_date - timedelta(days=5), 'income', Decimal('4000.00'), 'Contrato mensal', income_cat),
    
    # Despesas
    (base_date - timedelta(days=18), 'expense', Decimal('1500.00'), 'Salários', expense_cat),
    (base_date - timedelta(days=12), 'expense', Decimal('800.00'), 'Aluguel', expense_cat),
    (base_date - timedelta(days=8), 'expense', Decimal('300.00'), 'Material de escritório', expense_cat),
    (base_date - timedelta(days=3), 'expense', Decimal('450.00'), 'Marketing', expense_cat),
]

for date, t_type, amount, desc, category in transactions_data:
    transaction, created = Transaction.objects.get_or_create(
        company=company,
        account=account,
        transaction_date=date,
        description=desc,
        defaults={
            'transaction_type': t_type,
            'amount': amount,
            'category': category,
            'status': 'completed',
            'created_by': admin_user,
        }
    )
    if created:
        print(f"✅ Transação criada: {desc} - R$ {amount}")

print(f"\nTotal de transações: {Transaction.objects.filter(company=company).count()}")
print("✅ Dados demo criados com sucesso!")