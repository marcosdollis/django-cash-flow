from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from transactions.models import Transaction, Account, Category
from accounts.models import Company


class FinancialAnalyzer:
    """Analisador financeiro inteligente para alertas e insights"""
    
    def __init__(self, company):
        self.company = company
        self.today = timezone.now().date()
    
    def get_cash_flow_health_score(self):
        """Calcula score de saúde do fluxo de caixa (0-100)"""
        # Últimos 30 dias
        start_date = self.today - timedelta(days=30)
        
        income = Transaction.objects.filter(
            company=self.company,
            transaction_type='income',
            transaction_date__gte=start_date,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        expense = Transaction.objects.filter(
            company=self.company,
            transaction_type='expense',
            transaction_date__gte=start_date,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        if expense == 0:
            return 100 if income > 0 else 50
        
        ratio = float(income / expense)
        
        # Score baseado na relação receita/despesa
        if ratio >= 1.5:
            return 100
        elif ratio >= 1.2:
            return 85
        elif ratio >= 1.0:
            return 70
        elif ratio >= 0.8:
            return 50
        elif ratio >= 0.6:
            return 30
        else:
            return 10
    
    def detect_spending_spikes(self):
        """Detecta picos de gastos anômalos"""
        alerts = []
        
        # Média de gastos dos últimos 90 dias
        ninety_days_ago = self.today - timedelta(days=90)
        seven_days_ago = self.today - timedelta(days=7)
        
        avg_expense = Transaction.objects.filter(
            company=self.company,
            transaction_type='expense',
            transaction_date__gte=ninety_days_ago,
            transaction_date__lt=seven_days_ago,
            status='completed'
        ).aggregate(avg=Avg('amount'))['avg'] or Decimal('0')
        
        # Gastos da última semana
        recent_expenses = Transaction.objects.filter(
            company=self.company,
            transaction_type='expense',
            transaction_date__gte=seven_days_ago,
            status='completed'
        )
        
        for expense in recent_expenses:
            if expense.amount > avg_expense * Decimal('2'):  # 200% acima da média
                alerts.append({
                    'type': 'spending_spike',
                    'severity': 'high',
                    'title': 'Gasto Anômalo Detectado',
                    'message': f'Despesa de R$ {expense.amount} em {expense.category.name if expense.category else "categoria não definida"} está 200% acima da média histórica',
                    'transaction': expense,
                    'recommendation': 'Verifique se este gasto está dentro do planejado'
                })
        
        return alerts
    
    def check_low_balance_risk(self):
        """Verifica risco de saldo baixo"""
        alerts = []
        
        # Projeção baseada na média de gastos dos últimos 30 dias
        thirty_days_ago = self.today - timedelta(days=30)
        
        avg_daily_expense = Transaction.objects.filter(
            company=self.company,
            transaction_type='expense',
            transaction_date__gte=thirty_days_ago,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        avg_daily_expense = avg_daily_expense / 30
        
        for account in Account.objects.filter(company=self.company, is_active=True):
            days_remaining = float(account.current_balance / avg_daily_expense) if avg_daily_expense > 0 else 999
            
            if days_remaining < 7:
                alerts.append({
                    'type': 'low_balance',
                    'severity': 'critical',
                    'title': 'Risco de Saldo Insuficiente',
                    'message': f'A conta {account.name} pode ficar sem saldo em {int(days_remaining)} dias',
                    'account': account,
                    'recommendation': 'Considere reduzir gastos ou aumentar receitas'
                })
            elif days_remaining < 15:
                alerts.append({
                    'type': 'low_balance',
                    'severity': 'medium',
                    'title': 'Atenção ao Saldo',
                    'message': f'A conta {account.name} pode ficar sem saldo em {int(days_remaining)} dias',
                    'account': account,
                    'recommendation': 'Monitore os gastos desta conta'
                })
        
        return alerts
    
    def analyze_category_trends(self):
        """Analisa tendências por categoria"""
        insights = []
        
        # Comparar últimos 30 dias com 30 dias anteriores
        current_period_start = self.today - timedelta(days=30)
        previous_period_start = self.today - timedelta(days=60)
        previous_period_end = self.today - timedelta(days=30)
        
        categories = Category.objects.filter(company=self.company)
        
        for category in categories:
            current_total = Transaction.objects.filter(
                company=self.company,
                category=category,
                transaction_date__gte=current_period_start,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            previous_total = Transaction.objects.filter(
                company=self.company,
                category=category,
                transaction_date__gte=previous_period_start,
                transaction_date__lt=previous_period_end,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if previous_total > 0:
                change_percent = ((current_total - previous_total) / previous_total) * 100
                
                if abs(change_percent) > 20:  # Mudança significativa
                    trend = 'aumento' if change_percent > 0 else 'redução'
                    insights.append({
                        'type': 'category_trend',
                        'category': category.name,
                        'change_percent': float(change_percent),
                        'trend': trend,
                        'current_total': current_total,
                        'previous_total': previous_total,
                        'message': f'{trend.capitalize()} de {abs(change_percent):.1f}% em {category.name}'
                    })
        
        return insights
    
    def generate_financial_forecast(self, days=30):
        """Gera previsão financeira baseada em tendências"""
        # Média de receitas e despesas dos últimos 60 dias
        sixty_days_ago = self.today - timedelta(days=60)
        
        avg_daily_income = Transaction.objects.filter(
            company=self.company,
            transaction_type='income',
            transaction_date__gte=sixty_days_ago,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        avg_daily_income = avg_daily_income / 60
        
        avg_daily_expense = Transaction.objects.filter(
            company=self.company,
            transaction_type='expense',
            transaction_date__gte=sixty_days_ago,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        avg_daily_expense = avg_daily_expense / 60
        
        # Saldo atual total
        current_balance = sum(account.current_balance for account in Account.objects.filter(company=self.company, is_active=True))
        
        # Projeção
        projected_income = avg_daily_income * days
        projected_expense = avg_daily_expense * days
        projected_balance = current_balance + projected_income - projected_expense
        
        return {
            'current_balance': current_balance,
            'projected_income': projected_income,
            'projected_expense': projected_expense,
            'projected_balance': projected_balance,
            'net_flow': projected_income - projected_expense,
            'avg_daily_income': avg_daily_income,
            'avg_daily_expense': avg_daily_expense,
            'forecast_days': days
        }
    
    def get_all_insights(self):
        """Retorna todos os insights e alertas"""
        insights = {
            'health_score': self.get_cash_flow_health_score(),
            'spending_spikes': self.detect_spending_spikes(),
            'balance_risks': self.check_low_balance_risk(),
            'category_trends': self.analyze_category_trends(),
            'forecast': self.generate_financial_forecast(),
            'generated_at': timezone.now()
        }
        
        return insights