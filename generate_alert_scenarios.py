#!/usr/bin/env python
"""
Script para gerar cenários de teste dos alertas inteligentes
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
    
    if not company or not user:
        print("❌ Empresa ou usuário não encontrados")
        return
    
    print(f"🏢 Gerando cenários para: {company.name}")
    
    # Pegar contas e categorias existentes
    account = Account.objects.filter(company=company).first()
    categories = list(Category.objects.filter(company=company))
    
    if not account or not categories:
        print("❌ Conta ou categorias não encontradas")
        return
    
    # Limpar alertas anteriores para começar limpo
    Alert.objects.filter(company=company).delete()
    print("🧹 Alertas anteriores removidos")
    
    # Cenários específicos para diferentes tipos de alertas
    scenarios = [
        create_spending_spike_scenario,
        create_low_balance_scenario,
        create_goal_deadline_scenario,
        create_overdue_transactions_scenario,
        create_unusual_expense_pattern_scenario,
        create_cash_flow_negative_scenario,
        create_budget_exceeded_scenario
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Cenário {i}: {scenario.__name__.replace('create_', '').replace('_scenario', '').title()}")
        try:
            scenario(company, user, account, categories)
            print(f"✅ Cenário {i} criado com sucesso")
        except Exception as e:
            print(f"❌ Erro no cenário {i}: {e}")
    
    # Executar análise para gerar alertas
    print(f"\n🤖 Executando análise de alertas...")
    analyzer = FinancialAnalyzer(company)
    insights = analyzer.get_all_insights()
    
    print(f"📊 Resultado da análise:")
    print(f"   • Picos de gastos: {len(insights['spending_spikes'])}")
    print(f"   • Riscos de saldo: {len(insights['balance_risks'])}")
    
    # Criar alertas no banco baseados nos insights
    create_alerts_from_insights(company, user, insights)
    
    print(f"\n📈 Alertas criados no sistema:")
    alerts = Alert.objects.filter(company=company)
    for alert in alerts:
        severity_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🟠', 'critical': '🔴'}
        print(f"   {severity_emoji.get(alert.severity, '⚪')} {alert.title} ({alert.alert_type})")

def create_spending_spike_scenario(company, user, account, categories):
    """Cenário: Pico de gastos anômalos"""
    
    # Criar histórico de gastos normais (últimos 90 dias)
    base_date = datetime.now().date() - timedelta(days=90)
    food_category = next((c for c in categories if 'aliment' in c.name.lower() or 'comida' in c.name.lower()), categories[0])
    
    # Gastos normais: R$ 300-500 por semana em alimentação
    for week in range(12):  # 12 semanas
        week_date = base_date + timedelta(weeks=week)
        weekly_amount = Decimal(str(random.uniform(300, 500)))
        
        Transaction.objects.create(
            company=company,
            account=account,
            category=food_category,
            transaction_type='expense',
            amount=weekly_amount,
            description=f'Gastos semanais com alimentação - semana {week+1}',
            transaction_date=week_date,
            status='completed',
            created_by=user
        )
    
    # Criar pico anômalo: R$ 2.500 em alimentação (muito acima da média)
    spike_date = datetime.now().date() - timedelta(days=2)
    Transaction.objects.create(
        company=company,
        account=account,
        category=food_category,
        transaction_type='expense',
        amount=Decimal('2500.00'),
        description='Evento corporativo - buffet completo',
        transaction_date=spike_date,
        status='completed',
        created_by=user
    )

def create_low_balance_scenario(company, user, account, categories):
    """Cenário: Risco de saldo baixo"""
    
    # Reduzir saldo da conta para valor baixo
    account.balance = Decimal('250.00')  # Saldo muito baixo
    account.save()
    
    # Criar despesas futuras (próximos dias) que podem zerar a conta
    tomorrow = datetime.now().date() + timedelta(days=1)
    utilities_category = next((c for c in categories if 'utilidad' in c.name.lower() or 'conta' in c.name.lower()), categories[0])
    
    Transaction.objects.create(
        company=company,
        user=user,
        account=account,
        category=utilities_category,
        transaction_type='expense',
        amount=Decimal('180.00'),
        description='Conta de luz - vencimento amanhã',
        transaction_date=tomorrow,
        status='pending'
    )
    
    day_after = tomorrow + timedelta(days=1)
    Transaction.objects.create(
        company=company,
        user=user,
        account=account,
        category=utilities_category,
        transaction_type='expense',
        amount=Decimal('120.00'),
        description='Conta de água - vencimento',
        transaction_date=day_after,
        status='pending'
    )

def create_goal_deadline_scenario(company, user, account, categories):
    """Cenário: Meta próxima do prazo"""
    
    # Criar meta com prazo próximo e progresso insuficiente
    sales_category = next((c for c in categories if 'venda' in c.name.lower() or 'receita' in c.name.lower()), categories[0])
    
    near_deadline = datetime.now().date() + timedelta(days=3)
    goal = Goal.objects.create(
        company=company,
        user=user,
        name='Meta de Vendas Trimestral',
        description='Atingir R$ 50.000 em vendas até o final do trimestre',
        goal_type='income_increase',
        target_amount=Decimal('50000.00'),
        current_amount=Decimal('15000.00'),  # Apenas 30% atingido
        start_date=datetime.now().date() - timedelta(days=87),  # 90 dias de meta
        target_date=near_deadline,
        category=sales_category,
        is_active=True
    )

def create_overdue_transactions_scenario(company, user, account, categories):
    """Cenário: Transações vencidas"""
    
    # Criar transações vencidas
    overdue_dates = [
        datetime.now().date() - timedelta(days=5),
        datetime.now().date() - timedelta(days=10),
        datetime.now().date() - timedelta(days=15)
    ]
    
    services_category = next((c for c in categories if 'serviço' in c.name.lower()), categories[0])
    
    for i, overdue_date in enumerate(overdue_dates, 1):
        Transaction.objects.create(
            company=company,
            user=user,
            account=account,
            category=services_category,
            transaction_type='expense',
            amount=Decimal(str(random.uniform(200, 800))),
            description=f'Serviço em atraso #{i} - Pagamento vencido',
            transaction_date=overdue_date,
            status='pending'  # Ainda não pago
        )

def create_unusual_expense_pattern_scenario(company, user, account, categories):
    """Cenário: Padrão de gastos incomuns"""
    
    # Criar gastos em categoria nova/pouco usada
    misc_category = categories[-1]  # Última categoria
    
    # Vários gastos pequenos e frequentes (suspeito)
    for day in range(7):
        expense_date = datetime.now().date() - timedelta(days=day)
        Transaction.objects.create(
            company=company,
            user=user,
            account=account,
            category=misc_category,
            transaction_type='expense',
            amount=Decimal(str(random.uniform(45, 89))),
            description=f'Gasto frequente #{day+1}',
            transaction_date=expense_date,
            status='completed'
        )

def create_cash_flow_negative_scenario(company, user, account, categories):
    """Cenário: Fluxo de caixa negativo"""
    
    # Criar mais saídas que entradas no período
    last_week = datetime.now().date() - timedelta(days=7)
    
    # Muitas despesas
    for i in range(5):
        expense_date = last_week + timedelta(days=i)
        Transaction.objects.create(
            company=company,
            user=user,
            account=account,
            category=random.choice(categories),
            transaction_type='expense',
            amount=Decimal(str(random.uniform(800, 1500))),
            description=f'Grande despesa #{i+1}',
            transaction_date=expense_date,
            status='completed'
        )
    
    # Poucas receitas
    Transaction.objects.create(
        company=company,
        user=user,
        account=account,
        category=random.choice(categories),
        transaction_type='income',
        amount=Decimal('1200.00'),
        description='Única receita da semana',
        transaction_date=last_week + timedelta(days=3),
        status='completed'
    )

def create_budget_exceeded_scenario(company, user, account, categories):
    """Cenário: Orçamento excedido (simulado)"""
    
    # Criar muitos gastos em uma categoria específica
    transport_category = next((c for c in categories if 'transport' in c.name.lower() or 'combustível' in c.name.lower()), categories[0])
    
    # Simular orçamento mensal de R$ 800 sendo excedido
    month_start = datetime.now().date().replace(day=1)
    
    for i in range(8):
        expense_date = month_start + timedelta(days=i*3)
        Transaction.objects.create(
            company=company,
            user=user,
            account=account,
            category=transport_category,
            transaction_type='expense',
            amount=Decimal(str(random.uniform(150, 250))),
            description=f'Combustível #{i+1}',
            transaction_date=expense_date,
            status='completed'
        )

def create_alerts_from_insights(company, user, insights):
    """Cria alertas no banco baseados nos insights gerados"""
    
    # Alertas de picos de gastos
    for spike in insights['spending_spikes']:
        Alert.objects.create(
            company=company,
            user=user,
            title=spike['title'],
            message=spike['message'],
            alert_type='unusual_expense',
            severity=spike['severity'],
            status='active',
            action_required=True,
            auto_resolve=False
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
            status='active',
            action_required=True,
            auto_resolve=False
        )
    
    # Alertas de transações vencidas
    overdue_count = Transaction.objects.filter(
        company=company,
        status='pending',
        transaction_date__lt=datetime.now().date()
    ).count()
    
    if overdue_count > 0:
        Alert.objects.create(
            company=company,
            user=user,
            title='Transações Vencidas',
            message=f'{overdue_count} transação(ões) estão em atraso e precisam de atenção',
            alert_type='overdue_transaction',
            severity='high',
            status='active',
            action_required=True,
            auto_resolve=False
        )
    
    # Alertas de metas próximas ao prazo
    urgent_goals = Goal.objects.filter(
        company=company,
        is_active=True,
        target_date__lte=datetime.now().date() + timedelta(days=7)
    )
    
    for goal in urgent_goals:
        if goal.progress_percentage < 80:  # Meta com menos de 80% de progresso
            Alert.objects.create(
                company=company,
                user=user,
                title='Meta em Risco',
                message=f'Meta "{goal.name}" tem apenas {goal.progress_percentage:.1f}% de progresso e vence em {goal.days_remaining} dias',
                alert_type='goal_deadline',
                severity='medium' if goal.days_remaining > 3 else 'high',
                status='active',
                action_required=True,
                auto_resolve=False
            )

if __name__ == '__main__':
    print("🚀 Gerando cenários de teste para alertas inteligentes...")
    create_test_scenarios()
    print("\n✅ Cenários criados! Acesse o dashboard para ver os alertas.")
    print("📱 Dashboard: http://127.0.0.1:8000/core/")
    print("🔔 Alertas: http://127.0.0.1:8000/reports/alerts/")