from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse


def landing_page(request):
    """
    View para a landing page do sistema
    """
    # Se o usuário já estiver logado, redireciona para o dashboard
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    context = {
        'page_title': 'CashFlow Manager - Gestão Financeira Inteligente',
        'meta_description': 'Sistema completo de gestão financeira com IA, relatórios profissionais e análises avançadas. Por apenas R$ 59,90/mês com ROI de até 19.100%.',
    }
    
    return render(request, 'landing/landing_new.html', context)


@require_http_methods(["POST"])
def start_trial(request):
    """
    View para iniciar teste grátis - redireciona para registro
    """
    return redirect('accounts:register')


@require_http_methods(["POST"])
def schedule_demo(request):
    """
    View para agendar demonstração - redireciona para login
    """
    return redirect('accounts:login')


def redirect_to_dashboard(request):
    """
    View para redirecionar usuários interessados para o dashboard
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    else:
        return redirect('accounts:login')