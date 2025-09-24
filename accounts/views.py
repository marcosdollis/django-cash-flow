from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, CompanyCreationForm, 
    UserProfileForm, UserManagementForm, CompanyMemberForm, ChangePasswordForm
)
from .models import Company, CompanyMember, User
from .decorators import company_admin_required, can_manage_users_required, company_member_required


class CustomLoginView(LoginView):
    """View customizada de login"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Verificar se o usuário tem uma empresa associada
        user = self.request.user
        if user.companies.exists():
            return reverse_lazy('core:dashboard')
        else:
            return reverse_lazy('accounts:company_setup')


def register_view(request):
    """View de registro de usuário"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Agora configure sua empresa.')
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if user:
                login(request, user)
                return redirect('accounts:company_setup')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def company_setup_view(request):
    """View para configuração inicial da empresa"""
    # Verificar se o usuário já tem uma empresa
    if request.user.companies.exists():
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = CompanyCreationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                company = form.save(commit=False)
                company.owner = request.user
                company.save()
                
                # Adicionar o usuário como membro da empresa
                CompanyMember.objects.create(
                    user=request.user,
                    company=company,
                    role='owner'
                )
                
                messages.success(request, f'Empresa {company.name} criada com sucesso!')
                return redirect('core:dashboard')
    else:
        form = CompanyCreationForm()
    
    return render(request, 'accounts/company_setup.html', {'form': form})


@login_required
def profile_view(request):
    """View do perfil do usuário"""
    profile_form = None
    password_form = None
    
    if request.method == 'POST':
        if 'profile_update' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('accounts:profile')
        elif 'password_change' in request.POST:
            password_form = ChangePasswordForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('accounts:profile')
    
    if profile_form is None:
        profile_form = UserProfileForm(instance=request.user)
    if password_form is None:
        password_form = ChangePasswordForm(request.user)
    
    # Obter empresas do usuário
    user_companies = CompanyMember.objects.filter(user=request.user, is_active=True)
    current_company_id = request.session.get('current_company_id')
    current_company = None
    
    if current_company_id:
        try:
            current_company = Company.objects.get(id=current_company_id)
        except Company.DoesNotExist:
            current_company = user_companies.first().company if user_companies else None
    else:
        current_company = user_companies.first().company if user_companies else None
    
    return render(request, 'accounts/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_companies': user_companies,
        'current_company': current_company
    })


@login_required
def profile_update_view(request):
    """View específica para atualização do perfil"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
        else:
            messages.error(request, 'Erro ao atualizar perfil. Verifique os dados.')
    
    return redirect('accounts:profile')


@login_required
def change_password_view(request):
    """View específica para alteração de senha"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Senha alterada com sucesso!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('accounts:profile')


@login_required
@company_admin_required
def company_settings_view(request):
    """View para configurações da empresa"""
    company = request.current_company
    user_role = request.user.get_company_role(company)
    can_edit_company = user_role in ['owner', 'admin']
    can_manage_users = request.user.can_manage_users(company)
    
    company_form = None
    
    if request.method == 'POST' and can_edit_company:
        company_form = CompanyCreationForm(request.POST, request.FILES, instance=company)
        if company_form.is_valid():
            company_form.save()
            messages.success(request, 'Configurações da empresa atualizadas com sucesso!')
            return redirect('accounts:company_settings')
    
    if company_form is None:
        company_form = CompanyCreationForm(instance=company)
    
    # Obter membros da empresa
    company_members = CompanyMember.objects.filter(
        company=company, 
        is_active=True
    ).select_related('user').order_by('-role', 'user__first_name')
    
    active_users_count = company_members.filter(is_active=True).count()
    
    return render(request, 'accounts/settings.html', {
        'company_form': company_form,
        'current_company': company,
        'user_role': user_role,
        'can_edit_company': can_edit_company,
        'can_manage_users': can_manage_users,
        'company_members': company_members,
        'active_users_count': active_users_count,
    })


@login_required
@can_manage_users_required
def create_user_view(request):
    """View para criar novos usuários"""
    company = request.current_company
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                
                # Criar membro da empresa
                CompanyMember.objects.create(
                    user=user,
                    company=company,
                    role=form.cleaned_data['role']
                )
                
                messages.success(request, f'Usuário {user.get_full_name()} criado com sucesso!')
                return redirect('accounts:company_settings')
        else:
            messages.error(request, 'Erro ao criar usuário. Verifique os dados.')
    else:
        form = UserManagementForm()
    
    return render(request, 'accounts/create_user.html', {
        'form': form,
        'current_company': company
    })


@login_required
@can_manage_users_required
def add_member_view(request):
    """View para adicionar membros existentes à empresa"""
    company = request.current_company
    
    if request.method == 'POST':
        form = CompanyMemberForm(request.POST, company=company)
        if form.is_valid():
            member = form.save(commit=False)
            member.company = company
            member.save()
            
            messages.success(request, f'Usuário {member.user.get_full_name()} adicionado à empresa!')
            return redirect('accounts:company_settings')
        else:
            messages.error(request, 'Erro ao adicionar membro. Verifique os dados.')
    
    return redirect('accounts:company_settings')


@login_required
@can_manage_users_required
def edit_user_view(request, user_id):
    """View para editar usuários"""
    company = request.current_company
    user_to_edit = get_object_or_404(User, id=user_id)
    
    # Verificar se o usuário é membro da empresa
    member = get_object_or_404(CompanyMember, user=user_to_edit, company=company)
    
    # Não permitir edição do próprio usuário ou do owner (se não for owner)
    current_user_role = request.user.get_company_role(company)
    if user_to_edit == request.user or (member.role == 'owner' and current_user_role != 'owner'):
        messages.error(request, 'Você não tem permissão para editar este usuário.')
        return redirect('accounts:company_settings')
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user_to_edit, is_editing=True)
        # Definir o papel atual no formulário
        form.initial['role'] = member.role
        
        if form.is_valid():
            user = form.save()
            
            # Atualizar papel na empresa
            member.role = form.cleaned_data['role']
            member.save()
            
            messages.success(request, f'Usuário {user.get_full_name()} atualizado com sucesso!')
            return redirect('accounts:company_settings')
        else:
            messages.error(request, 'Erro ao atualizar usuário. Verifique os dados.')
    else:
        form = UserManagementForm(instance=user_to_edit, is_editing=True)
        form.initial['role'] = member.role
    
    return render(request, 'accounts/edit_user.html', {
        'form': form,
        'user_to_edit': user_to_edit,
        'member': member,
        'current_company': company
    })


@login_required
@can_manage_users_required
def remove_member_view(request, member_id):
    """View para remover membros da empresa"""
    company = request.current_company
    member = get_object_or_404(CompanyMember, id=member_id, company=company)
    
    # Não permitir remoção do próprio usuário ou do owner
    current_user_role = request.user.get_company_role(company)
    if member.user == request.user or (member.role == 'owner' and current_user_role != 'owner'):
        messages.error(request, 'Você não tem permissão para remover este usuário.')
        return redirect('accounts:company_settings')
    
    if request.method == 'POST':
        user_name = member.user.get_full_name()
        member.is_active = False
        member.save()
        
        messages.success(request, f'Usuário {user_name} removido da empresa.')
    
    return redirect('accounts:company_settings')


@login_required
@can_manage_users_required
def get_user_form(request):
    """API para obter formulário de usuário via AJAX"""
    form_type = request.GET.get('type', 'create')
    company = request.current_company
    
    if form_type == 'create':
        form = UserManagementForm()
    elif form_type == 'add_member':
        form = CompanyMemberForm(company=company)
    else:
        return JsonResponse({'error': 'Tipo de formulário inválido'}, status=400)
    
    # Renderizar formulário como HTML
    form_html = render(request, 'accounts/partials/user_form.html', {
        'form': form,
        'form_type': form_type
    }).content.decode('utf-8')
    
    return JsonResponse({'form_html': form_html})


@login_required
def switch_company_view(request, company_id):
    """View para trocar de empresa"""
    company = get_object_or_404(Company, id=company_id)
    
    # Verificar se o usuário é membro da empresa
    if not CompanyMember.objects.filter(user=request.user, company=company, is_active=True).exists():
        messages.error(request, 'Você não tem acesso a essa empresa.')
        return redirect('core:dashboard')
    
    # Salvar a empresa atual na sessão
    request.session['current_company_id'] = company.id
    messages.success(request, f'Empresa alterada para {company.name}')
    
    return redirect('core:dashboard')


@require_POST
@login_required
def custom_logout_view(request):
    """View customizada de logout com POST obrigatório"""
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'Você foi desconectado com sucesso. Até logo, {user_name}!')
    return redirect('accounts:login')


class CustomLogoutView(LogoutView):
    """View customizada de logout usando class-based view"""
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        """Adiciona mensagem de sucesso no logout"""
        if request.user.is_authenticated:
            user_name = request.user.get_full_name() or request.user.username
            messages.success(request, f'Você foi desconectado com sucesso. Até logo, {user_name}!')
        return super().dispatch(request, *args, **kwargs)
