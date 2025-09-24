from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Company, CompanyMember


def company_admin_required(view_func):
    """
    Decorator que requer que o usuário seja admin ou owner da empresa atual
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Obter empresa atual da sessão ou primeira empresa do usuário
        current_company_id = request.session.get('current_company_id')
        if current_company_id:
            try:
                company = Company.objects.get(id=current_company_id)
            except Company.DoesNotExist:
                company = request.user.companies.first()
        else:
            company = request.user.companies.first()
        
        if not company:
            messages.error(request, 'Você precisa estar associado a uma empresa.')
            return redirect('accounts:company_setup')
        
        # Verificar se o usuário é admin ou owner
        if not request.user.is_company_admin(company):
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('core:dashboard')
        
        # Adicionar a empresa ao request para uso na view
        request.current_company = company
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def can_manage_users_required(view_func):
    """
    Decorator que requer que o usuário possa gerenciar outros usuários
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Obter empresa atual
        current_company_id = request.session.get('current_company_id')
        if current_company_id:
            try:
                company = Company.objects.get(id=current_company_id)
            except Company.DoesNotExist:
                company = request.user.companies.first()
        else:
            company = request.user.companies.first()
        
        if not company:
            messages.error(request, 'Você precisa estar associado a uma empresa.')
            return redirect('accounts:company_setup')
        
        # Verificar se o usuário pode gerenciar usuários
        if not request.user.can_manage_users(company):
            messages.error(request, 'Você não tem permissão para gerenciar usuários.')
            return redirect('core:dashboard')
        
        request.current_company = company
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def company_member_required(view_func):
    """
    Decorator que requer que o usuário seja membro de uma empresa
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Verificar se o usuário tem pelo menos uma empresa
        if not request.user.companies.exists():
            messages.info(request, 'Você precisa configurar uma empresa primeiro.')
            return redirect('accounts:company_setup')
        
        # Obter empresa atual
        current_company_id = request.session.get('current_company_id')
        if current_company_id:
            try:
                company = Company.objects.get(id=current_company_id)
                # Verificar se o usuário é membro desta empresa
                if not CompanyMember.objects.filter(
                    user=request.user, 
                    company=company, 
                    is_active=True
                ).exists():
                    company = request.user.companies.first()
            except Company.DoesNotExist:
                company = request.user.companies.first()
        else:
            company = request.user.companies.first()
        
        request.current_company = company
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def role_required(required_roles):
    """
    Decorator que requer que o usuário tenha um papel específico na empresa
    Args:
        required_roles: lista de papéis permitidos ['owner', 'admin', 'manager', 'user']
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Obter empresa atual
            current_company_id = request.session.get('current_company_id')
            if current_company_id:
                try:
                    company = Company.objects.get(id=current_company_id)
                except Company.DoesNotExist:
                    company = request.user.companies.first()
            else:
                company = request.user.companies.first()
            
            if not company:
                messages.error(request, 'Você precisa estar associado a uma empresa.')
                return redirect('accounts:company_setup')
            
            # Verificar o papel do usuário
            user_role = request.user.get_company_role(company)
            if user_role not in required_roles:
                messages.error(request, f'Você precisa ter um dos seguintes papéis: {", ".join(required_roles)}.')
                return redirect('core:dashboard')
            
            request.current_company = company
            request.user_role = user_role
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator