from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Sum, Count, Avg  # Fixed Sum import
from datetime import datetime, timedelta
from decimal import Decimal
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
import xlsxwriter
from transactions.models import Transaction, Account, Category
from core.financial_analyzer import FinancialAnalyzer


@login_required
def export_financial_report_pdf(request):
    """Exporta relatório financeiro completo em PDF (PREMIUM FEATURE)"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Parâmetros
    period_days = int(request.GET.get('period', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_days)
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_financeiro_{current_company.name}_{end_date.strftime("%Y%m%d")}.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#2E86AB')
    )
    
    # Título
    story.append(Paragraph(f"Relatório Financeiro - {current_company.name}", title_style))
    story.append(Paragraph(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Resumo Executivo
    analyzer = FinancialAnalyzer(current_company)
    insights = analyzer.get_all_insights()
    
    story.append(Paragraph("RESUMO EXECUTIVO", styles['Heading2']))
    
    # Métricas principais
    income = Transaction.objects.filter(
        company=current_company,
        transaction_type='income',
        transaction_date__range=[start_date, end_date],
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    expense = Transaction.objects.filter(
        company=current_company,
        transaction_type='expense',
        transaction_date__range=[start_date, end_date],
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Tabela de métricas
    metrics_data = [
        ['Métrica', 'Valor'],
        ['Total de Receitas', f'R$ {income:,.2f}'],
        ['Total de Despesas', f'R$ {expense:,.2f}'],
        ['Resultado Líquido', f'R$ {income - expense:,.2f}'],
        ['Score de Saúde Financeira', f'{insights["health_score"]}/100'],
        ['Projeção 30 dias', f'R$ {insights["forecast"]["net_flow"]:,.2f}'],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Transações detalhadas
    story.append(Paragraph("TRANSAÇÕES DETALHADAS", styles['Heading2']))
    
    transactions = Transaction.objects.filter(
        company=current_company,
        transaction_date__range=[start_date, end_date],
        status='completed'
    ).order_by('-transaction_date', '-created_at')[:50]  # Últimas 50
    
    if transactions:
        trans_data = [['Data', 'Tipo', 'Categoria', 'Descrição', 'Valor']]
        
        for trans in transactions:
            trans_data.append([
                trans.transaction_date.strftime('%d/%m/%Y'),
                'Receita' if trans.transaction_type == 'income' else 'Despesa',
                trans.category.name if trans.category else 'Sem categoria',
                trans.description[:30] + '...' if len(trans.description) > 30 else trans.description,
                f'R$ {trans.amount:,.2f}'
            ])
        
        trans_table = Table(trans_data, colWidths=[1*inch, 1*inch, 1.2*inch, 2.3*inch, 1*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(trans_table)
    
    # Insights e Alertas
    if insights['spending_spikes'] or insights['balance_risks']:
        story.append(Spacer(1, 20))
        story.append(Paragraph("ALERTAS INTELIGENTES", styles['Heading2']))
        
        for alert in insights['spending_spikes']:
            story.append(Paragraph(f"⚠️ {alert['title']}: {alert['message']}", styles['Normal']))
            story.append(Paragraph(f"💡 Recomendação: {alert['recommendation']}", styles['Italic']))
            story.append(Spacer(1, 10))
        
        for alert in insights['balance_risks']:
            story.append(Paragraph(f"🚨 {alert['title']}: {alert['message']}", styles['Normal']))
            story.append(Paragraph(f"💡 Recomendação: {alert['recommendation']}", styles['Italic']))
            story.append(Spacer(1, 10))
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(Paragraph("Relatório gerado automaticamente pelo CashFlow Manager", styles['Italic']))
    story.append(Paragraph(f"Data de geração: {timezone.now().strftime('%d/%m/%Y às %H:%M')}", styles['Italic']))
    
    # Construir PDF
    doc.build(story)
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
def export_financial_report_excel(request):
    """Exporta relatório financeiro completo em Excel (PREMIUM FEATURE)"""
    current_company = request.user.companies.first()
    if not current_company:
        return redirect('accounts:company_setup')
    
    # Parâmetros
    period_days = int(request.GET.get('period', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_days)
    
    # Criar arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="relatorio_financeiro_{current_company.name}_{end_date.strftime("%Y%m%d")}.xlsx"'
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Formatos
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'bg_color': '#2E86AB',
        'font_color': 'white'
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D3D3D3',
        'border': 1
    })
    
    money_format = workbook.add_format({
        'num_format': 'R$ #,##0.00',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'border': 1
    })
    
    # Aba 1: Resumo
    summary_sheet = workbook.add_worksheet('Resumo')
    
    # Título
    summary_sheet.merge_range('A1:E1', f'Relatório Financeiro - {current_company.name}', title_format)
    summary_sheet.write('A2', f'Período: {start_date.strftime("%d/%m/%Y")} a {end_date.strftime("%d/%m/%Y")}')
    
    # Métricas principais
    analyzer = FinancialAnalyzer(current_company)
    insights = analyzer.get_all_insights()
    
    income = Transaction.objects.filter(
        company=current_company,
        transaction_type='income',
        transaction_date__range=[start_date, end_date],
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    expense = Transaction.objects.filter(
        company=current_company,
        transaction_type='expense',
        transaction_date__range=[start_date, end_date],
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    summary_sheet.write('A4', 'Métrica', header_format)
    summary_sheet.write('B4', 'Valor', header_format)
    
    row = 5
    metrics = [
        ('Total de Receitas', income),
        ('Total de Despesas', expense),
        ('Resultado Líquido', income - expense),
        ('Score de Saúde Financeira', insights['health_score']),
        ('Projeção 30 dias', insights['forecast']['net_flow']),
    ]
    
    for metric, value in metrics:
        summary_sheet.write(f'A{row}', metric)
        if isinstance(value, (int, float, Decimal)):
            summary_sheet.write(f'B{row}', float(value), money_format if 'Receitas' in metric or 'Despesas' in metric or 'Líquido' in metric or 'Projeção' in metric else None)
        else:
            summary_sheet.write(f'B{row}', value)
        row += 1
    
    # Aba 2: Transações
    trans_sheet = workbook.add_worksheet('Transações')
    
    # Headers
    headers = ['Data', 'Tipo', 'Categoria', 'Conta', 'Descrição', 'Valor']
    for col, header in enumerate(headers):
        trans_sheet.write(0, col, header, header_format)
    
    # Dados das transações
    transactions = Transaction.objects.filter(
        company=current_company,
        transaction_date__range=[start_date, end_date],
        status='completed'
    ).order_by('-transaction_date', '-created_at')
    
    for row, trans in enumerate(transactions, start=1):
        trans_sheet.write(row, 0, trans.transaction_date, date_format)
        trans_sheet.write(row, 1, 'Receita' if trans.transaction_type == 'income' else 'Despesa')
        trans_sheet.write(row, 2, trans.category.name if trans.category else 'Sem categoria')
        trans_sheet.write(row, 3, trans.account.name)
        trans_sheet.write(row, 4, trans.description)
        trans_sheet.write(row, 5, float(trans.amount), money_format)
    
    # Aba 3: Insights
    insights_sheet = workbook.add_worksheet('Insights IA')
    
    insights_sheet.write('A1', 'Insights Inteligentes', title_format)
    insights_sheet.write('A3', f'Score de Saúde Financeira: {insights["health_score"]}/100')
    
    row = 5
    if insights['spending_spikes']:
        insights_sheet.write(f'A{row}', 'ALERTAS DE GASTOS ANÔMALOS:', header_format)
        row += 1
        for alert in insights['spending_spikes']:
            insights_sheet.write(f'A{row}', f"• {alert['title']}: {alert['message']}")
            row += 1
            insights_sheet.write(f'A{row}', f"  Recomendação: {alert['recommendation']}")
            row += 2
    
    if insights['balance_risks']:
        insights_sheet.write(f'A{row}', 'ALERTAS DE SALDO:', header_format)
        row += 1
        for alert in insights['balance_risks']:
            insights_sheet.write(f'A{row}', f"• {alert['title']}: {alert['message']}")
            row += 1
            insights_sheet.write(f'A{row}', f"  Recomendação: {alert['recommendation']}")
            row += 2
    
    # Ajustar largura das colunas
    summary_sheet.set_column('A:A', 25)
    summary_sheet.set_column('B:B', 15)
    trans_sheet.set_column('A:A', 12)
    trans_sheet.set_column('B:B', 10)
    trans_sheet.set_column('C:C', 15)
    trans_sheet.set_column('D:D', 15)
    trans_sheet.set_column('E:E', 30)
    trans_sheet.set_column('F:F', 15)
    insights_sheet.set_column('A:A', 80)
    
    workbook.close()
    
    output.seek(0)
    response.write(output.getvalue())
    output.close()
    
    return response