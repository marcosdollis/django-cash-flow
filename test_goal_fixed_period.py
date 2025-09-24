#!/usr/bin/env python
"""
Script para testar o novo comportamento das metas (período fixo da meta)
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

def test_goal_fixed_period():
    """Testa o cálculo de progresso das metas considerando apenas o período da meta"""
    
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
    
    for goal in goals:
        print(f"\n📊 Meta: {goal.name}")
        print(f"   Tipo: {goal.goal_type}")
        print(f"   Período da Meta: {goal.start_date} até {goal.target_date}")
        print(f"   Meta: R$ {goal.target_amount}")
        print(f"   Progresso Atual: R$ {goal.current_amount} ({goal.progress_percentage:.1f}%)")
        
        # Mostrar dias restantes
        print(f"   Dias restantes: {goal.days_remaining}")
        
        # Verificar se há transações no período da meta
        if goal.category:
            from django.utils import timezone
            end_date = min(timezone.now().date(), goal.target_date)
            
            transactions_in_period = goal.category.transactions.filter(
                company=company,
                status='completed',
                transaction_date__gte=goal.start_date,
                transaction_date__lte=end_date
            ).order_by('-transaction_date')
            
            print(f"   📝 Transações no período da meta ({goal.start_date} - {end_date}):")
            
            if transactions_in_period.exists():
                for trans in transactions_in_period[:5]:  # Mostrar apenas as 5 mais recentes
                    symbol = "+" if trans.transaction_type == 'income' else "-"
                    print(f"      {trans.transaction_date}: {symbol}R$ {trans.amount} - {trans.description}")
                
                if transactions_in_period.count() > 5:
                    print(f"      ... e mais {transactions_in_period.count() - 5} transações")
            else:
                print(f"      Nenhuma transação encontrada na categoria {goal.category.name}")
        
        # Forçar atualização do progresso
        goal.update_progress()
        goal.refresh_from_db()
        print(f"   🔄 Após atualização: R$ {goal.current_amount} ({goal.progress_percentage:.1f}%)")

if __name__ == '__main__':
    test_goal_fixed_period()