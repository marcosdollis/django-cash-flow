"""
Sistema de geração automática de alertas baseado em dados reais
"""
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Avg, Count

from transactions.models import Transaction, Account, Goal
from reports.models import Alert
from core.financial_analyzer import FinancialAnalyzer


def generate_dynamic_alerts(company, user=None):
    """
    Gera alertas dinâmicos baseados no comportamento atual dos dados
    """
    if not user:
        user = company.users.first()
    
    # Limpar alertas antigos (mais de 30 dias)
    old_alerts = Alert.objects.filter(
        company=company,
        triggered_at__lt=timezone.now() - timedelta(days=30)
    )
    old_alerts.delete()
    
    alerts_created = []
    
    # 1. Verificar contas com saldo baixo
    alerts_created.extend(_check_low_balance_alerts(company, user))
    
    # 2. Verificar transações vencidas
    alerts_created.extend(_check_overdue_transactions(company, user))
    
    # 3. Verificar metas próximas do prazo
    alerts_created.extend(_check_goal_deadlines(company, user))
    
    # 4. Verificar padrões de gastos anômalos
    alerts_created.extend(_check_spending_anomalies(company, user))
    
    # 5. Verificar fluxo de caixa
    alerts_created.extend(_check_cash_flow_risks(company, user))
    
    return alerts_created


def _check_low_balance_alerts(company, user):
    """Verifica alertas de saldo baixo"""
    alerts = []
    
    for account in Account.objects.filter(company=company, is_active=True):
        # Considera saldo baixo quando menor que R$ 500 ou 
        # quando não consegue cobrir despesas dos próximos 7 dias
        
        upcoming_expenses = Transaction.objects.filter(
            account=account,
            transaction_type='expense',
            status='pending',
            transaction_date__lte=timezone.now().date() + timedelta(days=7)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        critical_threshold = max(Decimal('500'), upcoming_expenses * Decimal('1.2'))
        
        if account.current_balance < critical_threshold:
            # Verificar se já existe alerta similar recente
            existing = Alert.objects.filter(
                company=company,
                alert_type='low_balance',
                status='active',
                triggered_at__gte=timezone.now() - timedelta(hours=24)
            ).filter(
                message__contains=account.name
            ).exists()
            
            if not existing:
                severity = 'critical' if account.current_balance < upcoming_expenses else 'high'
                
                alert = Alert.objects.create(
                    company=company,
                    user=user,
                    title=f'Saldo Baixo - {account.name}',
                    message=f'Conta {account.name} com saldo de R$ {account.current_balance:.2f}. '
                           f'Despesas pendentes: R$ {upcoming_expenses:.2f}',
                    alert_type='low_balance',
                    severity=severity,
                    status='active',
                    related_data={'account_id': account.id, 'balance': float(account.current_balance)}
                )
                alerts.append(alert)
    
    return alerts


def _check_overdue_transactions(company, user):
    """Verifica transações vencidas"""
    alerts = []
    
    overdue_transactions = Transaction.objects.filter(
        company=company,
        status='pending',
        transaction_date__lt=timezone.now().date()
    )
    
    if overdue_transactions.exists():
        count = overdue_transactions.count()
        total_amount = overdue_transactions.aggregate(Sum('amount'))['amount__sum']
        
        # Verificar se já existe alerta similar recente
        existing = Alert.objects.filter(
            company=company,
            alert_type='overdue_transaction',
            status='active',
            triggered_at__gte=timezone.now() - timedelta(hours=12)
        ).exists()
        
        if not existing:
            severity = 'critical' if count > 5 else 'high'
            
            alert = Alert.objects.create(
                company=company,
                user=user,
                title='Transações em Atraso',
                message=f'{count} transação(ões) vencidas totalizando R$ {total_amount:.2f}. '
                       f'Regularize os pagamentos para evitar multas e juros.',
                alert_type='overdue_transaction',
                severity=severity,
                status='active',
                related_data={'count': count, 'total_amount': float(total_amount)}
            )
            alerts.append(alert)
    
    return alerts


def _check_goal_deadlines(company, user):
    """Verifica metas próximas do prazo"""
    alerts = []
    
    urgent_goals = Goal.objects.filter(
        company=company,
        is_active=True,
        target_date__lte=timezone.now().date() + timedelta(days=10)
    )
    
    for goal in urgent_goals:
        progress = goal.progress_percentage
        days_remaining = goal.days_remaining
        
        # Alerta se progresso for muito baixo para o tempo restante
        expected_progress = max(70, 100 - (days_remaining * 5))  # Expectativa baseada em dias restantes
        
        if progress < expected_progress and days_remaining > 0:
            # Verificar se já existe alerta para esta meta
            existing = Alert.objects.filter(
                company=company,
                alert_type='goal_deadline',
                status='active',
                triggered_at__gte=timezone.now() - timedelta(days=2)
            ).filter(
                message__contains=goal.name
            ).exists()
            
            if not existing:
                if days_remaining <= 3:
                    severity = 'high'
                elif days_remaining <= 7:
                    severity = 'medium'
                else:
                    severity = 'low'
                
                alert = Alert.objects.create(
                    company=company,
                    user=user,
                    title='Meta em Risco',
                    message=f'Meta "{goal.name}" com {progress:.1f}% de progresso e '
                           f'{days_remaining} dias restantes. Acelere os esforços!',
                    alert_type='goal_deadline',
                    severity=severity,
                    status='active',
                    related_data={'goal_id': goal.id, 'progress': float(progress)}
                )
                alerts.append(alert)
    
    return alerts


def _check_spending_anomalies(company, user):
    """Verifica anomalias nos gastos usando FinancialAnalyzer"""
    alerts = []
    
    try:
        analyzer = FinancialAnalyzer(company)
        spending_spikes = analyzer.detect_spending_spikes()
        
        for spike in spending_spikes:
            # Verificar se já existe alerta similar recente
            existing = Alert.objects.filter(
                company=company,
                alert_type='unusual_expense',
                status='active',
                triggered_at__gte=timezone.now() - timedelta(hours=6)
            ).exists()
            
            if not existing:
                alert = Alert.objects.create(
                    company=company,
                    user=user,
                    title=spike['title'],
                    message=spike['message'] + f" Recomendação: {spike['recommendation']}",
                    alert_type='unusual_expense',
                    severity=spike['severity'],
                    status='active',
                    related_data={
                        'transaction_id': spike.get('transaction', {}).get('id') if spike.get('transaction') else None
                    }
                )
                alerts.append(alert)
    
    except Exception as e:
        print(f"Erro ao verificar anomalias de gastos: {e}")
    
    return alerts


def _check_cash_flow_risks(company, user):
    """Verifica riscos no fluxo de caixa"""
    alerts = []
    
    try:
        analyzer = FinancialAnalyzer(company)
        balance_risks = analyzer.check_low_balance_risk()
        
        for risk in balance_risks:
            # Verificar se já existe alerta similar recente
            existing = Alert.objects.filter(
                company=company,
                alert_type='cash_flow_negative',
                status='active',
                triggered_at__gte=timezone.now() - timedelta(hours=12)
            ).exists()
            
            if not existing:
                alert = Alert.objects.create(
                    company=company,
                    user=user,
                    title=risk['title'],
                    message=risk['message'] + f" Recomendação: {risk['recommendation']}",
                    alert_type='cash_flow_negative',
                    severity=risk['severity'],
                    status='active'
                )
                alerts.append(alert)
    
    except Exception as e:
        print(f"Erro ao verificar fluxo de caixa: {e}")
    
    return alerts


def auto_resolve_outdated_alerts(company):
    """
    Resolve automaticamente alertas que não são mais relevantes
    """
    resolved_count = 0
    
    # Resolver alertas de saldo baixo se o saldo melhorou
    low_balance_alerts = Alert.objects.filter(
        company=company,
        alert_type='low_balance',
        status='active'
    )
    
    for alert in low_balance_alerts:
        account_id = alert.related_data.get('account_id')
        if account_id:
            try:
                account = Account.objects.get(id=account_id)
                if account.current_balance > Decimal('1000'):  # Saldo melhorou significativamente
                    alert.resolve()
                    resolved_count += 1
            except Account.DoesNotExist:
                pass
    
    # Resolver alertas de transações vencidas se não há mais transações vencidas
    overdue_alerts = Alert.objects.filter(
        company=company,
        alert_type='overdue_transaction',
        status='active'
    )
    
    current_overdue = Transaction.objects.filter(
        company=company,
        status='pending',
        transaction_date__lt=timezone.now().date()
    ).count()
    
    if current_overdue == 0:
        for alert in overdue_alerts:
            alert.resolve()
            resolved_count += 1
    
    # Resolver alertas de metas se foram alcançadas
    goal_alerts = Alert.objects.filter(
        company=company,
        alert_type='goal_deadline',
        status='active'
    )
    
    for alert in goal_alerts:
        goal_id = alert.related_data.get('goal_id')
        if goal_id:
            try:
                goal = Goal.objects.get(id=goal_id)
                if goal.is_achieved or goal.progress_percentage >= 90:
                    alert.resolve()
                    resolved_count += 1
            except Goal.DoesNotExist:
                pass
    
    return resolved_count