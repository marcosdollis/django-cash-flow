from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Transaction, Category, Account, Goal
from .forms import TransactionForm, CategoryForm, AccountForm, GoalForm


@login_required
def transaction_list_view(request):
    """Lista de transações"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    transactions = Transaction.objects.filter(company=current_company)
    
    # Filtros
    search = request.GET.get('search')
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) |
            Q(notes__icontains=search)
        )
    
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    category_id = request.GET.get('category')
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    # Paginação
    paginator = Paginator(transactions.order_by('-transaction_date', '-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(company=current_company, is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_filters': request.GET,
    }
    return render(request, 'transactions/list.html', context)


@login_required
def transaction_create_view(request):
    """Criar nova transação"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, company=current_company)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.company = current_company
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Transação criada com sucesso!')
            return redirect('transactions:list')
    else:
        form = TransactionForm(company=current_company)
    
    return render(request, 'transactions/form.html', {'form': form, 'title': 'Nova Transação'})


@login_required
def transaction_detail_view(request, uuid):
    """Detalhes da transação"""
    from datetime import date
    
    current_company = request.user.companies.first()
    transaction = get_object_or_404(Transaction, uuid=uuid, company=current_company)
    
    return render(request, 'transactions/detail.html', {
        'transaction': transaction,
        'today': date.today()
    })


@login_required
def transaction_update_view(request, uuid):
    """Editar transação"""
    current_company = request.user.companies.first()
    transaction = get_object_or_404(Transaction, uuid=uuid, company=current_company)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction, company=current_company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada com sucesso!')
            return redirect('transactions:detail', uuid=transaction.uuid)
    else:
        form = TransactionForm(instance=transaction, company=current_company)
    
    return render(request, 'transactions/form.html', {'form': form, 'title': 'Editar Transação', 'transaction': transaction})


@login_required
def transaction_delete_view(request, uuid):
    """Excluir transação"""
    current_company = request.user.companies.first()
    transaction = get_object_or_404(Transaction, uuid=uuid, company=current_company)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transação excluída com sucesso!')
        return redirect('transactions:list')
    
    return render(request, 'transactions/delete.html', {'transaction': transaction})


@login_required
def transaction_update_status_view(request, uuid):
    """Atualizar status da transação"""
    current_company = request.user.companies.first()
    transaction = get_object_or_404(Transaction, uuid=uuid, company=current_company)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'completed', 'cancelled']:
            old_status = transaction.status
            transaction.status = new_status
            transaction.save()
            
            status_labels = {
                'pending': 'Pendente',
                'completed': 'Concluída',
                'cancelled': 'Cancelada'
            }
            
            messages.success(
                request, 
                f'Status da transação alterado de "{status_labels.get(old_status, old_status)}" para "{status_labels.get(new_status, new_status)}"!'
            )
        else:
            messages.error(request, 'Status inválido!')
    
    return redirect('transactions:detail', uuid=transaction.uuid)


@login_required
@require_POST
def transaction_bulk_update_status_view(request):
    """Atualizar status de múltiplas transações de uma vez"""
    current_company = request.user.companies.first()
    if not current_company:
        return JsonResponse({'success': False, 'error': 'Empresa não encontrada'}, status=400)
    
    transaction_ids = request.POST.getlist('transaction_ids[]')
    new_status = request.POST.get('status')
    
    if not transaction_ids:
        messages.error(request, 'Nenhuma transação foi selecionada!')
        return redirect('transactions:list')
    
    if new_status not in ['pending', 'completed', 'cancelled']:
        messages.error(request, 'Status inválido!')
        return redirect('transactions:list')
    
    # Atualiza todas as transações selecionadas
    updated_count = Transaction.objects.filter(
        uuid__in=transaction_ids,
        company=current_company
    ).update(status=new_status)
    
    status_labels = {
        'pending': 'Pendente',
        'completed': 'Concluída',
        'cancelled': 'Cancelada'
    }
    
    messages.success(
        request,
        f'{updated_count} transação(ões) marcada(s) como "{status_labels.get(new_status)}"!'
    )
    
    return redirect('transactions:list')


# Views de Categorias
@login_required
def category_list_view(request):
    """Lista de categorias"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    categories = Category.objects.filter(company=current_company)
    return render(request, 'transactions/categories.html', {'categories': categories})


@login_required
def category_create_view(request):
    """Criar categoria"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, company=current_company)
        if form.is_valid():
            category = form.save(commit=False)
            category.company = current_company
            category.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('transactions:category_list')
    else:
        form = CategoryForm(company=current_company)
    
    return render(request, 'transactions/category_form.html', {'form': form, 'title': 'Nova Categoria'})


@login_required
def category_update_view(request, pk):
    """Editar categoria"""
    current_company = request.user.companies.first()
    category = get_object_or_404(Category, pk=pk, company=current_company)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, company=current_company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('transactions:category_list')
    else:
        form = CategoryForm(instance=category, company=current_company)
    
    return render(request, 'transactions/category_form.html', {'form': form, 'title': 'Editar Categoria', 'category': category})


@login_required
def category_delete_view(request, pk):
    """Excluir categoria"""
    current_company = request.user.companies.first()
    category = get_object_or_404(Category, pk=pk, company=current_company)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('transactions:category_list')
    
    return render(request, 'transactions/delete.html', {'category': category})


# Views de Contas
@login_required
def account_list_view(request):
    """Lista de contas"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    accounts = Account.objects.filter(company=current_company)
    return render(request, 'transactions/accounts.html', {'accounts': accounts})


@login_required
def account_create_view(request):
    """Criar conta"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.company = current_company
            account.current_balance = account.initial_balance
            account.save()
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('transactions:account_list')
    else:
        form = AccountForm()
    
    return render(request, 'transactions/account_form.html', {'form': form, 'title': 'Nova Conta'})


@login_required
def account_update_view(request, pk):
    """Editar conta"""
    current_company = request.user.companies.first()
    account = get_object_or_404(Account, pk=pk, company=current_company)
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta atualizada com sucesso!')
            return redirect('transactions:account_list')
    else:
        form = AccountForm(instance=account)
    
    return render(request, 'transactions/account_form.html', {'form': form, 'title': 'Editar Conta', 'account': account})


@login_required
def account_delete_view(request, pk):
    """Excluir conta"""
    current_company = request.user.companies.first()
    account = get_object_or_404(Account, pk=pk, company=current_company)
    
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Conta excluída com sucesso!')
        return redirect('transactions:account_list')
    
    return render(request, 'transactions/delete.html', {'account': account})


# Views de Metas
@login_required
def goal_list_view(request):
    """Lista de metas"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    goals = Goal.objects.filter(company=current_company)
    return render(request, 'transactions/goals.html', {'goals': goals})


@login_required
def goal_create_view(request):
    """Criar meta"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    if request.method == 'POST':
        form = GoalForm(request.POST, company=current_company)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.company = current_company
            goal.created_by = request.user
            goal.save()
            messages.success(request, 'Meta criada com sucesso!')
            return redirect('transactions:goal_list')
    else:
        form = GoalForm(company=current_company)
    
    return render(request, 'transactions/goal_form.html', {'form': form, 'title': 'Nova Meta'})


@login_required
def goal_update_view(request, pk):
    """Editar meta"""
    current_company = request.user.companies.first()
    goal = get_object_or_404(Goal, pk=pk, company=current_company)
    
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal, company=current_company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta atualizada com sucesso!')
            return redirect('transactions:goal_list')
    else:
        form = GoalForm(instance=goal, company=current_company)
    
    return render(request, 'transactions/goal_form.html', {'form': form, 'title': 'Editar Meta', 'goal': goal})


@login_required
def goal_delete_view(request, pk):
    """Excluir meta"""
    current_company = request.user.companies.first()
    goal = get_object_or_404(Goal, pk=pk, company=current_company)
    
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Meta excluída com sucesso!')
        return redirect('transactions:goal_list')
    
    return render(request, 'transactions/delete.html', {'goal': goal})
