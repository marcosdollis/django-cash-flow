from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
from accounts.models import CompanyMember
from transactions.models import Transaction, Account, Category, Goal
from reports.models import Alert
from .financial_analyzer import FinancialAnalyzer
from .alert_generator import generate_dynamic_alerts, auto_resolve_outdated_alerts
from . import premium_exports
import json


@login_required
def dashboard_view(request):
    """Dashboard principal com visão geral"""
    # Verificar se o usuário tem uma empresa
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Filtros de data personalizados
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    period_preset = request.GET.get('period', '30')
    
    # Definir período baseado nos filtros
    today = timezone.now().date()
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Garantir que end_date não seja menor que start_date
            if end_date < start_date:
                end_date = start_date
            period_days = (end_date - start_date).days + 1
        except ValueError:
            # Se as datas são inválidas, usar período padrão
            period_days = 30
            start_date = today - timedelta(days=period_days-1)
            end_date = today
    else:
        # Usar período pré-definido
        if period_preset == 'next_30':
            # Próximos 30 dias (futuro)
            start_date = today
            end_date = today + timedelta(days=30)
            period_days = 31
        elif period_preset == 'next_60':
            # Próximos 60 dias (futuro)
            start_date = today
            end_date = today + timedelta(days=60)
            period_days = 61
        else:
            # Períodos passados (padrão)
            period_days = int(period_preset) if period_preset.isdigit() else 30
            start_date = today - timedelta(days=period_days-1)
            end_date = today
    
    # Estatísticas básicas
    total_income = Transaction.objects.filter(
        company=current_company,
        transaction_type='income',
        status='completed',
        transaction_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expense = Transaction.objects.filter(
        company=current_company,
        transaction_type='expense',
        status='completed',
        transaction_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    net_income = total_income - total_expense
    
    # Saldo atual de todas as contas
    accounts = Account.objects.filter(company=current_company, is_active=True)
    total_balance = sum(account.current_balance for account in accounts)
    
    # Transações recentes do período
    recent_transactions = Transaction.objects.filter(
        company=current_company,
        transaction_date__range=[start_date, end_date]
    ).order_by('-transaction_date', '-created_at')[:10]
    
    # Metas ativas (sempre consideram o período da própria meta)
    active_goals = Goal.objects.filter(
        company=current_company,
        is_active=True
    ).order_by('target_date')[:5]
    
    # Gerar/atualizar alertas dinâmicos automaticamente
    try:
        # Resolver alertas desatualizados
        auto_resolve_outdated_alerts(current_company)
        
        # Gerar novos alertas baseados nos dados atuais
        generate_dynamic_alerts(current_company, request.user)
    except Exception as e:
        print(f"Erro ao gerar alertas dinâmicos: {e}")
    
    # Alertas ativos (agora dinâmicos)
    active_alerts = Alert.objects.filter(
        company=current_company,
        status='active'
    ).order_by('-severity', '-triggered_at')[:5]
    
    # Dados para gráficos
    chart_data = _get_chart_data(current_company, start_date, end_date)
    
    # Insights inteligentes (PREMIUM FEATURE)
    analyzer = FinancialAnalyzer(current_company)
    insights = analyzer.get_all_insights()
    
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_income': net_income,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'active_goals': active_goals,
        'active_alerts': active_alerts,
        'accounts': accounts,
        'chart_data': json.dumps(chart_data),
        'insights': insights,  # PREMIUM FEATURE
        'period_days': period_days,
        'start_date': start_date,
        'end_date': end_date,
        'current_filters': {
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
            'period': period_preset,
        }
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def overview_view(request):
    """Visão geral mais detalhada"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Período personalizado ou padrão
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Análise por categoria
    category_analysis = Category.objects.filter(
        company=current_company,
        is_active=True
    ).annotate(
        total_amount=Sum('transactions__amount'),
        transaction_count=Count('transactions')
    ).filter(total_amount__gt=0).order_by('-total_amount')
    
    # Evolução mensal
    monthly_data = []
    for i in range(12):
        month_start = (end_date.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        income = Transaction.objects.filter(
            company=current_company,
            transaction_type='income',
            status='completed',
            transaction_date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            company=current_company,
            transaction_type='expense',
            status='completed',
            transaction_date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'income': float(income),
            'expense': float(expense),
            'net': float(income - expense)
        })
    
    monthly_data.reverse()
    
    context = {
        'category_analysis': category_analysis,
        'monthly_data': json.dumps(monthly_data),
        'selected_period': days,
    }
    
    return render(request, 'core/overview.html', context)


@login_required
def insights_view(request):
    """Página dedicada aos insights financeiros (PREMIUM FEATURE)"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    analyzer = FinancialAnalyzer(current_company)
    insights = analyzer.get_all_insights()
    
    # Filtros de data personalizados (mesma lógica do dashboard)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    period_preset = request.GET.get('period', '30')
    
    end_date = timezone.now().date()
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            period_days = (end_date - start_date).days + 1
        except ValueError:
            period_days = int(period_preset) if period_preset.isdigit() else 30
            start_date = end_date - timedelta(days=period_days-1)
    else:
        period_days = int(period_preset) if period_preset.isdigit() else 30
        start_date = end_date - timedelta(days=period_days-1)
    
    # Top categorias de gasto no período
    top_expense_categories = Category.objects.filter(
        company=current_company,
        category_type='expense'
    ).annotate(
        total_spent=Sum('transactions__amount', 
                       filter=Q(transactions__transaction_date__range=[start_date, end_date],
                                transactions__status='completed'))
    ).filter(total_spent__gt=0).order_by('-total_spent')[:5]
    
    # Padrões de gasto por dia da semana no período
    weekday_patterns = {}
    for i in range(7):  # 0=Segunda, 6=Domingo
        day_total = Transaction.objects.filter(
            company=current_company,
            transaction_type='expense',
            transaction_date__week_day=i+2,  # Django week_day: 1=Domingo
            transaction_date__range=[start_date, end_date],
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        weekday_patterns[i] = float(day_total)
    
    context = {
        'insights': insights,
        'top_expense_categories': top_expense_categories,
        'weekday_patterns': weekday_patterns,
        'period_days': period_days,
        'start_date': start_date,
        'end_date': end_date,
        'company': current_company,
        'current_filters': {
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
            'period': period_preset,
        }
    }
    
    return render(request, 'core/insights.html', context)


def _get_chart_data(company, start_date, end_date):
    """Gera dados para gráficos do dashboard"""
    
    # Gráfico de receitas vs despesas por dia
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        income = Transaction.objects.filter(
            company=company,
            transaction_type='income',
            status='completed',
            transaction_date=current_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            company=company,
            transaction_type='expense',
            status='completed',
            transaction_date=current_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'income': float(income),
            'expense': float(expense)
        })
        
        current_date += timedelta(days=1)
    
    # Gráfico por categoria
    category_data = []
    categories = Category.objects.filter(
        company=company,
        is_active=True
    ).annotate(
        total_amount=Sum('transactions__amount')
    ).filter(total_amount__gt=0).order_by('-total_amount')[:10]
    
    for category in categories:
        category_data.append({
            'name': category.name,
            'amount': float(category.total_amount),
            'color': category.color
        })
    
    return {
        'daily': daily_data,
        'categories': category_data
    }


@login_required
def export_financial_report(request):
    """View para redirecionamento de exportação baseado no formato"""
    format_type = request.GET.get('format', 'pdf')
    
    if format_type == 'excel':
        return premium_exports.export_financial_report_excel(request)
    else:
        return premium_exports.export_financial_report_pdf(request)
