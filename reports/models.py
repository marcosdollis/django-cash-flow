from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Company
from django.utils import timezone
import uuid

User = get_user_model()


class Report(models.Model):
    """Modelo para relatórios personalizados"""
    REPORT_TYPES = [
        ('cash_flow', 'Fluxo de Caixa'),
        ('income_statement', 'Demonstrativo de Resultado'),
        ('balance_sheet', 'Balanço Patrimonial'),
        ('category_analysis', 'Análise por Categoria'),
        ('trends', 'Análise de Tendências'),
        ('goals_progress', 'Progresso de Metas'),
        ('dasn_simei', 'DASN-SIMEI (Declaração Anual MEI)'),
        ('custom', 'Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('generating', 'Gerando'),
        ('ready', 'Pronto'),
        ('error', 'Erro'),
    ]
    
    # Identificação
    uuid = models.UUIDField('UUID', default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', blank=True)
    report_type = models.CharField('Tipo', max_length=20, choices=REPORT_TYPES)
    
    # Parâmetros do relatório
    start_date = models.DateField('Data Inicial')
    end_date = models.DateField('Data Final')
    filters = models.JSONField('Filtros', default=dict, blank=True)
    
    # Status e resultados
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='generating')
    data = models.JSONField('Dados', default=dict, blank=True)
    file_pdf = models.FileField('Arquivo PDF', upload_to='reports/pdf/', blank=True, null=True)
    file_excel = models.FileField('Arquivo Excel', upload_to='reports/excel/', blank=True, null=True)
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reports', verbose_name='Empresa')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_reports', verbose_name='Criado por')
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    expires_at = models.DateTimeField('Expira em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"
    
    def is_expired(self):
        """Verifica se o relatório expirou"""
        return self.expires_at and timezone.now() > self.expires_at


class Dashboard(models.Model):
    """Modelo para dashboards personalizados"""
    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', blank=True)
    
    # Configurações do dashboard
    layout = models.JSONField('Layout', default=dict)
    widgets = models.JSONField('Widgets', default=list)
    refresh_interval = models.IntegerField('Intervalo de Atualização (minutos)', default=30)
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='dashboards', verbose_name='Empresa')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_dashboards', verbose_name='Criado por')
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_dashboards', verbose_name='Compartilhado com')
    
    # Metadata
    is_default = models.BooleanField('Dashboard Padrão', default=False)
    is_public = models.BooleanField('Público', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
        ordering = ['-is_default', 'name']
        unique_together = ['company', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


class Forecast(models.Model):
    """Modelo para previsões financeiras"""
    FORECAST_TYPES = [
        ('cash_flow', 'Fluxo de Caixa'),
        ('revenue', 'Receita'),
        ('expenses', 'Despesas'),
        ('balance', 'Saldo'),
    ]
    
    PERIOD_TYPES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    name = models.CharField('Nome', max_length=200)
    forecast_type = models.CharField('Tipo', max_length=20, choices=FORECAST_TYPES)
    period_type = models.CharField('Período', max_length=20, choices=PERIOD_TYPES)
    
    # Dados da previsão
    start_date = models.DateField('Data Inicial')
    end_date = models.DateField('Data Final')
    data = models.JSONField('Dados', default=dict)
    accuracy = models.FloatField('Precisão (%)', null=True, blank=True)
    
    # Parâmetros do modelo
    model_parameters = models.JSONField('Parâmetros do Modelo', default=dict)
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='forecasts', verbose_name='Empresa')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_forecasts', verbose_name='Criado por')
    
    # Metadata
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Previsão'
        verbose_name_plural = 'Previsões'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_forecast_type_display()}"


class Alert(models.Model):
    """Modelo para alertas e notificações"""
    ALERT_TYPES = [
        ('low_balance', 'Saldo Baixo'),
        ('goal_deadline', 'Prazo de Meta'),
        ('overdue_transaction', 'Transação Vencida'),
        ('budget_exceeded', 'Orçamento Excedido'),
        ('unusual_expense', 'Gasto Incomum'),
        ('cash_flow_negative', 'Fluxo de Caixa Negativo'),
        ('custom', 'Personalizado'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('acknowledged', 'Reconhecido'),
        ('resolved', 'Resolvido'),
        ('dismissed', 'Dispensado'),
    ]
    
    # Dados do alerta
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensagem')
    alert_type = models.CharField('Tipo', max_length=20, choices=ALERT_TYPES)
    severity = models.CharField('Severidade', max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Dados relacionados
    related_data = models.JSONField('Dados Relacionados', default=dict, blank=True)
    action_url = models.URLField('URL de Ação', blank=True)
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='alerts', verbose_name='Empresa')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts', verbose_name='Usuário')
    
    # Metadata
    triggered_at = models.DateTimeField('Disparado em', auto_now_add=True)
    acknowledged_at = models.DateTimeField('Reconhecido em', null=True, blank=True)
    resolved_at = models.DateTimeField('Resolvido em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['alert_type', 'severity']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"
    
    def acknowledge(self, user=None):
        """Marca o alerta como reconhecido"""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.save(update_fields=['status', 'acknowledged_at'])
    
    def resolve(self, user=None):
        """Marca o alerta como resolvido"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at'])


class Budget(models.Model):
    """Modelo para orçamentos"""
    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', blank=True)
    
    # Período do orçamento
    start_date = models.DateField('Data Inicial')
    end_date = models.DateField('Data Final')
    
    # Valores
    total_budget = models.DecimalField('Orçamento Total', max_digits=15, decimal_places=2)
    spent_amount = models.DecimalField('Valor Gasto', max_digits=15, decimal_places=2, default=0)
    
    # Relacionamentos
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='budgets', verbose_name='Empresa')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_budgets', verbose_name='Criado por')
    
    # Metadata
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} (R$ {self.total_budget})"
    
    @property
    def remaining_budget(self):
        """Calcula o orçamento restante"""
        return self.total_budget - self.spent_amount
    
    @property
    def usage_percentage(self):
        """Calcula o percentual de uso do orçamento"""
        if self.total_budget == 0:
            return 0
        return (self.spent_amount / self.total_budget) * 100
    
    def update_spent_amount(self):
        """Atualiza o valor gasto baseado nas transações"""
        from django.db.models import Sum
        from transactions.models import Transaction
        
        total_spent = Transaction.objects.filter(
            company=self.company,
            transaction_type='expense',
            status='completed',
            transaction_date__range=[self.start_date, self.end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        self.spent_amount = total_spent
        self.save(update_fields=['spent_amount'])
