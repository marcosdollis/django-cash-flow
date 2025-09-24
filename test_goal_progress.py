#!/usr/bin/env python
"""
Script para testar o progresso das metas com filtros de data
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from transactions.models import Goal, Transaction, Category, Account
from accounts.models import Company

def test_goal_progress():
    """Testa o cálculo de progresso das metas com filtros de data"""
    
    # Pegar a primeira empresa
    company = Company.objects.first()
    if not company:
        print("❌ Nenhuma empresa encontrada")
        return
    
    print(f"🏢 Testando com empresa: {company.name}")
    
    # Pegar metas ativas
    goals = Goal.objects.filter(company=company, is_active=True)
    if not goals.exists():
        print("❌ Nenhuma meta ativa encontrada")
        return
    
    print(f"🎯 Encontradas {goals.count()} metas ativas")
    
    # Definir períodos de teste
    end_date = datetime.now().date()
    start_date_7d = end_date - timedelta(days=7)
    start_date_30d = end_date - timedelta(days=30)
    
    for goal in goals:
        print(f"\n📊 Meta: {goal.name}")
        print(f"   Tipo: {goal.goal_type}")
        print(f"   Meta: R$ {goal.target_amount}")
        print(f"   Progresso Total: R$ {goal.current_amount} ({goal.progress_percentage:.1f}%)")
        
        # Testar progresso para 7 dias
        progress_7d = goal.calculate_progress_for_period(start_date_7d, end_date)
        percentage_7d = min((progress_7d / goal.target_amount) * 100, 100) if goal.target_amount > 0 else 0
        print(f"   Últimos 7 dias: R$ {progress_7d} ({percentage_7d:.1f}%)")
        
        # Testar progresso para 30 dias
        progress_30d = goal.calculate_progress_for_period(start_date_30d, end_date)
        percentage_30d = min((progress_30d / goal.target_amount) * 100, 100) if goal.target_amount > 0 else 0
        print(f"   Últimos 30 dias: R$ {progress_30d} ({percentage_30d:.1f}%)")
        
        # Mostrar transações relacionadas nos últimos 7 dias
        if goal.category:
            recent_transactions = goal.category.transactions.filter(
                company=company,
                status='completed',
                transaction_date__range=[start_date_7d, end_date]
            ).order_by('-transaction_date')[:3]
            
            if recent_transactions.exists():
                print(f"   📝 Transações recentes (últimos 7 dias):")
                for trans in recent_transactions:
                    symbol = "+" if trans.transaction_type == 'income' else "-"
                    print(f"      {trans.transaction_date}: {symbol}R$ {trans.amount} - {trans.description}")
            else:
                print(f"   📝 Nenhuma transação recente na categoria {goal.category.name}")

if __name__ == '__main__':
    test_goal_progress()