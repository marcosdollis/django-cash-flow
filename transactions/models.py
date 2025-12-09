from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Company
from decimal import Decimal
from django.utils import timezone
import uuid

User = get_user_model()


class Category(models.Model):
    """Modelo para categorias de transações"""
    CATEGORY_TYPES = [
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('both', 'Ambos'),
    ]
    
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    category_type = models.CharField('Tipo', max_length=10, choices=CATEGORY_TYPES)
    color = models.CharField('Cor', max_length=7, default='#6c757d')
    icon = models.CharField('Ícone', max_length=50, default='fas fa-tag')
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='categories', verbose_name='Empresa')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', verbose_name='Categoria Pai')
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
        unique_together = ['name', 'company']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Account(models.Model):
    """Modelo para contas bancárias/financeiras"""
    ACCOUNT_TYPES = [
        ('checking', 'Conta Corrente'),
        ('savings', 'Poupança'),
        ('credit', 'Cartão de Crédito'),
        ('cash', 'Dinheiro'),
        ('investment', 'Investimento'),
        ('other', 'Outros'),
    ]
    
    name = models.CharField('Nome', max_length=100)
    account_type = models.CharField('Tipo', max_length=20, choices=ACCOUNT_TYPES)
    bank_name = models.CharField('Banco', max_length=100, blank=True)
    account_number = models.CharField('Número da Conta', max_length=50, blank=True)
    initial_balance = models.DecimalField('Saldo Inicial', max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField('Saldo Atual', max_digits=15, decimal_places=2, default=0)
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='accounts', verbose_name='Empresa')
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
    
    def save(self, *args, **kwargs):
        """Salva a conta e inicializa o saldo atual se necessário"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Se é uma nova conta, inicializar o saldo atual com o saldo inicial
        if is_new and self.initial_balance != 0:
            self.update_balance()
    
    def update_balance(self):
        """Atualiza o saldo baseado nas transações"""
        from django.db.models import Sum, Q
        
        # Receitas (apenas receitas reais, sem transferências)
        income = self.transactions.filter(
            transaction_type='income',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Despesas
        expense = self.transactions.filter(
            transaction_type='expense',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Transferências enviadas (débito) - onde esta conta é a origem
        transfers_out = self.transactions.filter(
            transaction_type='transfer',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Transferências recebidas (crédito) - onde esta conta é o destino
        # Buscar todas as transferências onde esta conta é o destino
        transfers_in = Transaction.objects.filter(
            company=self.company,
            transaction_type='transfer',
            transfer_to_account=self,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        self.current_balance = self.initial_balance + income - expense - transfers_out + transfers_in
        self.save(update_fields=['current_balance'])


class Transaction(models.Model):
    """Modelo principal para transações financeiras"""
    TRANSACTION_TYPES = [
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('transfer', 'Transferência'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    RECURRENCE_CHOICES = [
        ('none', 'Nenhuma'),
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    # Identificação
    uuid = models.UUIDField('UUID', default=uuid.uuid4, editable=False, unique=True)
    
    # Dados principais
    description = models.CharField('Descrição', max_length=200)
    amount = models.DecimalField('Valor', max_digits=15, decimal_places=2)
    transaction_type = models.CharField('Tipo', max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Datas
    transaction_date = models.DateField('Data da Transação', default=timezone.now)
    due_date = models.DateField('Data de Vencimento', null=True, blank=True)
    paid_date = models.DateTimeField('Data de Pagamento', null=True, blank=True)
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='transactions', verbose_name='Empresa')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions', verbose_name='Conta')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name='Categoria')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_transactions', verbose_name='Criado por')
    
    # Transferências
    transfer_to_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_transfers', verbose_name='Transferir para')
    
    # Recorrência
    recurrence = models.CharField('Recorrência', max_length=20, choices=RECURRENCE_CHOICES, default='none')
    recurrence_end_date = models.DateField('Fim da Recorrência', null=True, blank=True)
    parent_transaction = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='recurring_transactions', verbose_name='Transação Pai')
    
    # Metadata
    notes = models.TextField('Observações', blank=True)
    tags = models.CharField('Tags', max_length=500, blank=True, help_text='Separar por vírgulas')
    attachment = models.FileField('Anexo', upload_to='transactions/', blank=True, null=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['company', 'transaction_date']),
            models.Index(fields=['account', 'status']),
            models.Index(fields=['category', 'transaction_type']),
        ]
    
    def __str__(self):
        if self.transaction_type == 'income':
            symbol = "+"
        elif self.transaction_type == 'transfer':
            symbol = "-"  # Transferência é sempre saída da conta de origem
        else:  # expense
            symbol = "-"
        return f"{symbol}R$ {self.amount} - {self.description}"
    
    def get_amount_for_account(self, account):
        """Retorna o valor da transação com sinal correto para a conta especificada"""
        if self.transaction_type == 'income':
            return self.amount
        elif self.transaction_type == 'expense':
            return -self.amount
        elif self.transaction_type == 'transfer':
            if self.account == account:
                # Conta de origem: saída (negativo)
                return -self.amount
            elif self.transfer_to_account == account:
                # Conta de destino: entrada (positivo)
                return self.amount
        return self.amount
    
    def get_display_for_account(self, account):
        """Retorna a representação da transação para uma conta específica"""
        amount = self.get_amount_for_account(account)
        symbol = "+" if amount >= 0 else "-"
        return f"{symbol}R$ {abs(amount)} - {self.description}"
    
    def save(self, *args, **kwargs):
        # Controle de criação para evitar loops infinitos
        creating = kwargs.pop('creating', False)
        is_new = self.pk is None
        
        # Atualizar status para concluído se a data de pagamento foi definida
        if self.paid_date and self.status == 'pending':
            self.status = 'completed'
        
        # Salvar primeiro a transação principal
        super().save(*args, **kwargs)
        
        # Para transferências, não criar transações espelho - apenas atualizar saldos
        # Atualizar saldo das contas envolvidas
        if not creating:
            if hasattr(self, 'account') and self.account:
                self.account.update_balance()
            if hasattr(self, 'transfer_to_account') and self.transfer_to_account:
                self.transfer_to_account.update_balance()
        
        # Atualizar progresso das metas relacionadas à categoria desta transação
        if self.category and self.status == 'completed' and not creating:
            from .models import Goal
            related_goals = Goal.objects.filter(
                company=self.company,
                category=self.category,
                is_active=True
            )
            for goal in related_goals:
                goal.update_progress()
    
    def delete(self, *args, **kwargs):
        """Override do método delete para atualizar saldos das contas"""
        # Guardar referências das contas antes de deletar
        account = self.account
        transfer_to_account = self.transfer_to_account if hasattr(self, 'transfer_to_account') else None
        
        # Deletar a transação
        super().delete(*args, **kwargs)
        
        # Atualizar saldos das contas envolvidas
        if account:
            account.update_balance()
        if transfer_to_account:
            transfer_to_account.update_balance()


class Goal(models.Model):
    """Modelo para metas financeiras"""
    GOAL_TYPES = [
        ('savings', 'Poupança'),
        ('expense_reduction', 'Redução de Gastos'),
        ('income_increase', 'Aumento de Receita'),
        ('debt_payment', 'Pagamento de Dívida'),
        ('custom', 'Personalizada'),
    ]
    
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    goal_type = models.CharField('Tipo', max_length=20, choices=GOAL_TYPES)
    target_amount = models.DecimalField('Valor Alvo', max_digits=15, decimal_places=2)
    current_amount = models.DecimalField('Valor Atual', max_digits=15, decimal_places=2, default=0)
    
    # Datas
    start_date = models.DateField('Data de Início', default=timezone.now)
    target_date = models.DateField('Data Alvo')
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='goals', verbose_name='Empresa')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals', verbose_name='Categoria')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_goals', verbose_name='Criado por')
    
    # Metadata
    is_active = models.BooleanField('Ativo', default=True)
    is_achieved = models.BooleanField('Alcançado', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['target_date']
    
    def __str__(self):
        return f"{self.name} - R$ {self.target_amount}"
    
    @property
    def progress_percentage(self):
        """Calcula o percentual de progresso da meta"""
        if self.target_amount == 0:
            return 0
        return min((self.current_amount / self.target_amount) * 100, 100)
    
    @property
    def days_remaining(self):
        """Calcula quantos dias restam para a meta"""
        return (self.target_date - timezone.now().date()).days
    
    def update_progress(self):
        """Atualiza o progresso baseado nas transações relacionadas no período da meta"""
        if self.category:
            from django.db.models import Sum
            from django.utils import timezone
            
            # Definir o período da meta (da data inicial até hoje ou data final, o que for menor)
            end_date = min(timezone.now().date(), self.target_date)
            
            if self.goal_type in ['savings', 'income_increase']:
                # Para metas de poupança e aumento de receita, somar receitas da categoria
                total = self.category.transactions.filter(
                    transaction_type='income',
                    status='completed',
                    transaction_date__gte=self.start_date,
                    transaction_date__lte=end_date,
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            elif self.goal_type == 'expense_reduction':
                # Para metas de redução de gastos, somar despesas da categoria
                total = self.category.transactions.filter(
                    transaction_type='expense',
                    status='completed',
                    transaction_date__gte=self.start_date,
                    transaction_date__lte=end_date,
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            else:
                # Para outras metas (custom, debt_payment), somar todas as transações da categoria
                income = self.category.transactions.filter(
                    transaction_type='income',
                    status='completed',
                    transaction_date__gte=self.start_date,
                    transaction_date__lte=end_date,
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                expenses = self.category.transactions.filter(
                    transaction_type='expense',
                    status='completed',
                    transaction_date__gte=self.start_date,
                    transaction_date__lte=end_date,
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                total = income + expenses
            
            self.current_amount = total
            
            # Verificar se a meta foi alcançada
            if self.current_amount >= self.target_amount:
                self.is_achieved = True
            
            self.save(update_fields=['current_amount', 'is_achieved'])
    
    def calculate_progress_for_period(self, start_date, end_date):
        """Calcula o progresso da meta para um período específico"""
        if self.category:
            from django.db.models import Sum
            
            if self.goal_type in ['savings', 'income_increase']:
                # Para metas de poupança e aumento de receita, somar receitas da categoria
                total = self.category.transactions.filter(
                    transaction_type='income',
                    status='completed',
                    transaction_date__range=[start_date, end_date],
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            elif self.goal_type == 'expense_reduction':
                # Para metas de redução de gastos, somar despesas da categoria
                total = self.category.transactions.filter(
                    transaction_type='expense',
                    status='completed',
                    transaction_date__range=[start_date, end_date],
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            else:
                # Para outras metas (custom, debt_payment), somar todas as transações da categoria
                income = self.category.transactions.filter(
                    transaction_type='income',
                    status='completed',
                    transaction_date__range=[start_date, end_date],
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                expenses = self.category.transactions.filter(
                    transaction_type='expense',
                    status='completed',
                    transaction_date__range=[start_date, end_date],
                    company=self.company
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                total = income + expenses
            
            return total
        return Decimal('0')
