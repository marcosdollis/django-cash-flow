#!/usr/bin/env python
"""
Script simplificado para gerar cenários de teste dos alertas inteligentes
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from transactions.models import Transaction, Category, Account, Goal
from accounts.models import Company, User
from reports.models import Alert
from core.financial_analyzer import FinancialAnalyzer

def create_test_scenarios():
    """Cria cenários de teste para alertas inteligentes"""
    
    company = Company.objects.first()
    user = User.objects.first()
    account = Account.objects.filter(company=company).first()
    categories = list(Category.objects.filter(company=company))
    
    if not all([company, user, account, categories]):
        print("❌ Dados necessários não encontrados")
        return
    
    print(f"🏢 Gerando cenários para: {company.name}")
    
    # Limpar alertas anteriores
    Alert.objects.filter(company=company).delete()
    print("🧹 Alertas anteriores removidos")
    
    # 1. Cenário: Pico de gastos anômalos
    print("\n🎯 Cenário 1: Picos de Gastos Anômalos")
    food_category = categories[0] if categories else None
    
    # Histórico normal (últimos 90 dias)
    for i in range(15):
        Transaction.objects.create(
            company=company,
            account=account,
            category=food_category,
            transaction_type='expense',
            amount=Decimal(str(random.uniform(200, 400))),
            description=f'Gasto normal #{i+1}',
            transaction_date=datetime.now().date() - timedelta(days=90-i*6),
            status='completed',
            created_by=user
        )
    
    # Pico anômalo
    Transaction.objects.create(
        company=company,
        account=account,
        category=food_category,
        transaction_type='expense',
        amount=Decimal('2500.00'),
        description='Gasto anômalo - evento corporativo',
        transaction_date=datetime.now().date() - timedelta(days=3),
        status='completed',
        created_by=user
    )
    print("✅ Pico de gastos criado")
    
    # 2. Cenário: Saldo baixo
    print("\n🎯 Cenário 2: Risco de Saldo Baixo")
    account.current_balance = Decimal('150.00')
    account.save()
    
    # Despesas futuras que podem causar problema
    Transaction.objects.create(
        company=company,
        account=account,
        category=categories[1] if len(categories) > 1 else food_category,
        transaction_type='expense',
        amount=Decimal('120.00'),
        description='Conta de luz vencendo',
        transaction_date=datetime.now().date() + timedelta(days=1),
        status='pending',
        created_by=user
    )
    print("✅ Risco de saldo baixo criado")
    
    # 3. Cenário: Meta próxima do prazo
    print("\n🎯 Cenário 3: Meta com Prazo Próximo")
    goal = Goal.objects.create(
        company=company,
        name='Meta Urgente',
        description='Meta com prazo próximo e baixo progresso',
        goal_type='income_increase',
        target_amount=Decimal('10000.00'),
        current_amount=Decimal('2000.00'),
        start_date=datetime.now().date() - timedelta(days=85),
        target_date=datetime.now().date() + timedelta(days=5),
        category=food_category,
        is_active=True,
        created_by=user
    )
    print("✅ Meta urgente criada")
    
    # 4. Cenário: Transações vencidas
    print("\n🎯 Cenário 4: Transações Vencidas")
    for i in range(3):
        Transaction.objects.create(
            company=company,
            account=account,
            category=categories[i % len(categories)],
            transaction_type='expense',
            amount=Decimal(str(random.uniform(300, 600))),
            description=f'Transação vencida #{i+1}',
            transaction_date=datetime.now().date() - timedelta(days=5+i*3),
            status='pending',
            created_by=user
        )
    print("✅ Transações vencidas criadas")
    
    # 5. Cenário: Fluxo de caixa negativo
    print("\n🎯 Cenário 5: Fluxo de Caixa Negativo")
    # Muitas despesas, poucas receitas
    for i in range(7):
        Transaction.objects.create(
            company=company,
            account=account,
            category=categories[i % len(categories)],
            transaction_type='expense',
            amount=Decimal(str(random.uniform(600, 1200))),
            description=f'Grande despesa #{i+1}',
            transaction_date=datetime.now().date() - timedelta(days=10-i),
            status='completed',
            created_by=user
        )
    
    # Apenas uma receita pequena
    Transaction.objects.create(
        company=company,
        account=account,
        category=food_category,
        transaction_type='income',
        amount=Decimal('800.00'),
        description='Única receita pequena',
        transaction_date=datetime.now().date() - timedelta(days=7),
        status='completed',
        created_by=user
    )
    print("✅ Fluxo negativo criado")
    
    # 6. Executar análise para gerar alertas
    print(f"\n🤖 Executando análise de alertas...")
    analyzer = FinancialAnalyzer(company)
    insights = analyzer.get_all_insights()
    
    print(f"📊 Insights detectados:")
    print(f"   • Picos de gastos: {len(insights['spending_spikes'])}")
    print(f"   • Riscos de saldo: {len(insights['balance_risks'])}")
    
    # 7. Criar alertas no banco baseados nos insights
    create_system_alerts(company, user, insights)
    
    # 8. Mostrar alertas criados
    print(f"\n📈 Alertas ativos no sistema:")
    alerts = Alert.objects.filter(company=company, status='active')
    for alert in alerts:
        severity_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🟠', 'critical': '🔴'}
        print(f"   {severity_emoji.get(alert.severity, '⚪')} {alert.title}")
    
    print(f"\n✅ {alerts.count()} alertas criados com sucesso!")

def create_system_alerts(company, user, insights):
    """Cria alertas sistemáticos baseados nos insights"""
    
    # Alertas de picos de gastos
    for spike in insights['spending_spikes']:
        Alert.objects.create(
            company=company,
            user=user,
            title=spike['title'],
            message=spike['message'],
            alert_type='unusual_expense',
            severity=spike['severity'],
            status='active'
        )
    
    # Alertas de risco de saldo
    for risk in insights['balance_risks']:
        Alert.objects.create(
            company=company,
            user=user,
            title=risk['title'],
            message=risk['message'],
            alert_type='low_balance',
            severity=risk['severity'],
            status='active'
        )
    
    # Verificar transações vencidas
    overdue_count = Transaction.objects.filter(
        company=company,
        status='pending',
        transaction_date__lt=datetime.now().date()
    ).count()
    
    if overdue_count > 0:
        Alert.objects.create(
            company=company,
            user=user,
            title='Transações em Atraso',
            message=f'{overdue_count} transação(ões) estão vencidas e precisam de atenção',
            alert_type='overdue_transaction',
            severity='high',
            status='active'
        )
    
    # Verificar metas próximas ao prazo
    urgent_goals = Goal.objects.filter(
        company=company,
        is_active=True,
        target_date__lte=datetime.now().date() + timedelta(days=7)
    )
    
    for goal in urgent_goals:
        if goal.progress_percentage < 80:
            Alert.objects.create(
                company=company,
                user=user,
                title='Meta em Risco',
                message=f'Meta "{goal.name}" com apenas {goal.progress_percentage:.1f}% de progresso e {goal.days_remaining} dias restantes',
                alert_type='goal_deadline',
                severity='medium' if goal.days_remaining > 3 else 'high',
                status='active'
            )

if __name__ == '__main__':
    print("🚀 Gerando cenários de teste para alertas inteligentes...")
    create_test_scenarios()
    print("\n🔗 Links úteis:")
    print("   📱 Dashboard: http://127.0.0.1:8000/core/")
    print("   🔔 Alertas: http://127.0.0.1:8000/reports/alerts/")