"""
Teste para verificar se as datas do dashboard estão sendo exibidas corretamente
após a correção no JavaScript
"""
import django
import os

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Company
from transactions.models import Transaction, Account
from datetime import date, datetime
from django.utils import timezone

User = get_user_model()

def test_dashboard_dates():
    print("=== Teste de Datas no Dashboard ===")
    
    # Buscar dados existentes
    user = User.objects.first()
    if not user:
        print("❌ Nenhum usuário encontrado")
        return
    
    # Buscar empresa do usuário
    company = user.companies.filter(is_active=True).first()
    if not company:
        print("❌ Nenhuma empresa encontrada para o usuário")
        return
    
    account = Account.objects.filter(company=company).first()
    
    if not account:
        print("❌ Nenhuma conta encontrada")
        return
    
    print(f"✅ Usuário: {user.username}")
    print(f"✅ Empresa: {company.name}")
    print(f"✅ Conta: {account.name}")
    print()
    
    # Criar uma transação de teste para hoje
    today = timezone.now().date()
    yesterday = date(2024, 12, 25)  # Data específica para teste
    
    print(f"📅 Criando transação para a data: {yesterday}")
    
    # Verificar se já existe uma transação para essa data
    existing = Transaction.objects.filter(
        account=account,
        transaction_date=yesterday,
        description="Teste Dashboard - Data Correta"
    ).first()
    
    if existing:
        print(f"✅ Transação já existe: {existing.description} - R$ {existing.amount}")
    else:
        # Criar transação de teste
        test_transaction = Transaction.objects.create(
            company=company,
            account=account,
            transaction_type='income',
            amount=100.00,
            description="Teste Dashboard - Data Correta",
            transaction_date=yesterday
        )
        print(f"✅ Transação criada: {test_transaction.description} - R$ {test_transaction.amount}")
    
    print()
    print("🔍 Verificar no dashboard se a transação aparece na data correta:")
    print(f"   Data esperada: {yesterday.strftime('%d/%m/%Y')}")
    print(f"   URL do dashboard: http://127.0.0.1:8000/")
    print()
    print("📊 Instruções:")
    print("1. Acesse o dashboard no navegador")
    print("2. Verifique se o gráfico mostra a transação na data 25/12/2024")
    print("3. Antes da correção, apareceria em 24/12/2024 (um dia antes)")
    print("4. Após a correção, deve aparecer em 25/12/2024 (data correta)")

if __name__ == '__main__':
    test_dashboard_dates()