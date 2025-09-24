from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from io import BytesIO

from transactions.models import Transaction, Account, Category
from .models import Alert


@login_required
def report_list_view(request):
    """Lista de relatórios"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/list.html', {})


@login_required
def report_generate_view(request):
    """Gerar relatório"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/generate.html', {})


@login_required
def report_detail_view(request, uuid):
    """Detalhes do relatório"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/detail.html', {})


@login_required
def report_download_view(request, uuid):
    """Download do relatório"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return redirect('reports:list')


@login_required
def dashboard_list_view(request):
    """Lista de dashboards"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/dashboards.html', {})


@login_required
def dashboard_create_view(request):
    """Criar dashboard"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/dashboard_form.html', {})


@login_required
def dashboard_detail_view(request, pk):
    """Detalhes do dashboard"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/dashboard_detail.html', {})


@login_required
def forecast_list_view(request):
    """Lista de previsões"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/forecasts.html', {})


@login_required
def forecast_create_view(request):
    """Criar previsão"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    return render(request, 'reports/forecast_form.html', {})


@login_required
def alert_list_view(request):
    """Lista de alertas dinâmicos baseados nos dados reais"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Buscar alertas do banco de dados
    alerts = Alert.objects.filter(company=current_company).order_by('-triggered_at')
    
    # Contar por severidade
    alert_counts = {
        'critical': alerts.filter(severity='critical', status='active').count(),
        'high': alerts.filter(severity='high', status='active').count(),
        'medium': alerts.filter(severity='medium', status='active').count(),
        'low': alerts.filter(severity='low', status='active').count(),
        'resolved': alerts.filter(status='resolved').count(),
    }
    
    # Filtrar por status se especificado
    status_filter = request.GET.get('status', 'active')
    severity_filter = request.GET.get('severity')
    
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)
    
    context = {
        'alerts': alerts,
        'alert_counts': alert_counts,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
    }
    
    return render(request, 'reports/alerts.html', context)


@login_required
def alert_acknowledge_view(request, pk):
    """Reconhecer alerta"""
    current_company = request.user.companies.first()
    if not current_company:
        return JsonResponse({'success': False, 'error': 'Empresa não encontrada'})
    
    try:
        alert = get_object_or_404(Alert, pk=pk, company=current_company)
        
        if request.method == 'POST':
            alert.acknowledge(user=request.user)
            return JsonResponse({
                'success': True, 
                'message': 'Alerta reconhecido com sucesso!',
                'alert_id': alert.id
            })
        else:
            return JsonResponse({'success': False, 'error': 'Método não permitido'})
            
    except Alert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alerta não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def alert_resolve_view(request, pk):
    """Resolver/Dispensar alerta"""
    current_company = request.user.companies.first()
    if not current_company:
        return JsonResponse({'success': False, 'error': 'Empresa não encontrada'})
    
    try:
        alert = get_object_or_404(Alert, pk=pk, company=current_company)
        
        if request.method == 'POST':
            action = request.POST.get('action', 'resolve')
            
            if action == 'resolve':
                alert.resolve(user=request.user)
                message = 'Alerta resolvido com sucesso!'
            elif action == 'dismiss':
                alert.status = 'dismissed'
                alert.save()
                message = 'Alerta dispensado com sucesso!'
            else:
                return JsonResponse({'success': False, 'error': 'Ação inválida'})
            
            return JsonResponse({
                'success': True,
                'message': message,
                'alert_id': alert.id
            })
        else:
            return JsonResponse({'success': False, 'error': 'Método não permitido'})
            
    except Alert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alerta não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Views adicionais para relatórios financeiros
@login_required
def reports_overview(request):
    """Visão geral dos relatórios"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Dados básicos para dashboard de relatórios
    context = {
        'total_transactions': Transaction.objects.filter(account__company=current_company).count(),
        'total_categories': Category.objects.filter(company=current_company).count(),
        'total_accounts': Account.objects.filter(company=current_company).count(),
    }
    
    return render(request, 'reports/overview.html', context)


@login_required
def financial_report(request):
    """Relatório financeiro detalhado"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Período (último mês por padrão)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Parâmetros da query
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Filtrar transações
    transactions = Transaction.objects.filter(
        account__company=current_company,
        date__range=[start_date, end_date]
    )
    
    # Receitas e despesas
    income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Por categoria
    category_data = {}
    for transaction in transactions:
        cat_name = transaction.category.name if transaction.category else 'Sem categoria'
        if cat_name not in category_data:
            category_data[cat_name] = {'income': Decimal('0'), 'expense': Decimal('0')}
        category_data[cat_name][transaction.type] += transaction.amount
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'income': income,
        'expense': expense,
        'net': income - expense,
        'transactions': transactions.order_by('-date')[:50],  # Últimas 50
        'category_data': category_data,
    }
    
    return render(request, 'reports/financial.html', context)


@login_required
def cash_flow_report(request):
    """Relatório de fluxo de caixa"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Dados para gráfico de fluxo de caixa (últimos 12 meses)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    monthly_data = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        transactions = Transaction.objects.filter(
            account__company=current_company,
            date__gte=current_date,
            date__lt=next_month
        )
        
        income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        monthly_data.append({
            'month': current_date.strftime('%b %Y'),
            'income': float(income),
            'expense': float(expense),
            'net': float(income - expense)
        })
        
        current_date = next_month
    
    context = {
        'monthly_data': json.dumps(monthly_data),
        'accounts': Account.objects.filter(company=current_company),
    }
    
    return render(request, 'reports/cash_flow.html', context)


@login_required
def api_chart_data(request):
    """API para dados dos gráficos"""
    current_company = request.user.companies.first()
    if not current_company:
        return JsonResponse({'error': 'Empresa não encontrada'}, status=400)
    
    chart_type = request.GET.get('type', 'monthly')
    
    if chart_type == 'monthly':
        # Dados mensais (últimos 6 meses)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=180)
        
        data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            transactions = Transaction.objects.filter(
                account__company=current_company,
                date__gte=current_date,
                date__lt=next_month
            )
            
            income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0')
            expense = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            data.append({
                'month': current_date.strftime('%b'),
                'income': float(income),
                'expense': float(expense)
            })
            
            current_date = next_month
        
        return JsonResponse({'data': data})
    
    elif chart_type == 'categories':
        # Dados por categoria (último mês)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        categories = {}
        transactions = Transaction.objects.filter(
            account__company=current_company,
            date__range=[start_date, end_date]
        )
        
        for transaction in transactions:
            cat_name = transaction.category.name if transaction.category else 'Sem categoria'
            if cat_name not in categories:
                categories[cat_name] = 0
            categories[cat_name] += float(transaction.amount)
        
        data = [{'name': k, 'value': v} for k, v in categories.items()]
        return JsonResponse({'data': data})
    
    return JsonResponse({'error': 'Tipo de gráfico inválido'}, status=400)
