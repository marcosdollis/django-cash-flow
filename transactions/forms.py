from django import forms
from django.contrib.auth import get_user_model
from .models import Transaction, Category, Account, Goal
from decimal import Decimal

User = get_user_model()


class TransactionForm(forms.ModelForm):
    """Formulário para transações"""
    
    class Meta:
        model = Transaction
        fields = [
            'description', 'amount', 'transaction_type', 'account', 'category',
            'transaction_date', 'due_date', 'transfer_to_account', 'recurrence',
            'recurrence_end_date', 'notes', 'tags', 'attachment'
        ]
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da transação'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'account': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'transfer_to_account': forms.Select(attrs={
                'class': 'form-control'
            }),
            'recurrence': forms.Select(attrs={
                'class': 'form-control'
            }),
            'recurrence_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tags separadas por vírgula'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if self.company:
            # Filtrar contas e categorias pela empresa
            self.fields['account'].queryset = Account.objects.filter(
                company=self.company, is_active=True
            )
            self.fields['category'].queryset = Category.objects.filter(
                company=self.company, is_active=True
            )
            self.fields['transfer_to_account'].queryset = Account.objects.filter(
                company=self.company, is_active=True
            )
            
        # Campos opcionais
        self.fields['category'].required = False
        self.fields['due_date'].required = False
        self.fields['transfer_to_account'].required = False
        self.fields['recurrence_end_date'].required = False
        self.fields['notes'].required = False
        self.fields['tags'].required = False
        self.fields['attachment'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        transfer_to_account = cleaned_data.get('transfer_to_account')
        account = cleaned_data.get('account')
        
        # Validar transferência
        if transaction_type == 'transfer':
            if not transfer_to_account:
                raise forms.ValidationError('Conta de destino é obrigatória para transferências.')
            if transfer_to_account == account:
                raise forms.ValidationError('A conta de origem deve ser diferente da conta de destino.')
        
        return cleaned_data


class CategoryForm(forms.ModelForm):
    """Formulário para categorias"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'category_type', 'color', 'icon', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da categoria'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da categoria'
            }),
            'category_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: fas fa-shopping-cart'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if self.company:
            # Filtrar categorias pai pela empresa
            self.fields['parent'].queryset = Category.objects.filter(
                company=self.company, parent__isnull=True, is_active=True
            )
        
        # Campos opcionais
        self.fields['description'].required = False
        self.fields['parent'].required = False


class AccountForm(forms.ModelForm):
    """Formulário para contas"""
    
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'bank_name', 'account_number', 'initial_balance']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da conta'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do banco'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da conta'
            }),
            'initial_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos opcionais
        self.fields['bank_name'].required = False
        self.fields['account_number'].required = False


class GoalForm(forms.ModelForm):
    """Formulário para metas"""
    
    class Meta:
        model = Goal
        fields = [
            'name', 'description', 'goal_type', 'target_amount', 
            'start_date', 'target_date', 'category'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da meta'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da meta'
            }),
            'goal_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'target_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'category': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if self.company:
            # Filtrar categorias pela empresa
            self.fields['category'].queryset = Category.objects.filter(
                company=self.company, is_active=True
            )
        
        # Campos opcionais
        self.fields['description'].required = False
        self.fields['category'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        target_date = cleaned_data.get('target_date')
        
        if start_date and target_date and start_date >= target_date:
            raise forms.ValidationError('A data alvo deve ser posterior à data de início.')
        
        return cleaned_data


class TransactionFilterForm(forms.Form):
    """Formulário para filtros de transações"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar transações...'
        })
    )
    
    transaction_type = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Transaction.TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Transaction.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        empty_label='Todas as contas',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }, format='%Y-%m-%d')
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }, format='%Y-%m-%d')
    )
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            self.fields['category'].queryset = Category.objects.filter(
                company=company, is_active=True
            )
            self.fields['account'].queryset = Account.objects.filter(
                company=company, is_active=True
            )