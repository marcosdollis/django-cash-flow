from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from transactions.models import Transaction
from accounts.models import Company


def generate_dasn_simei_report(company, year=None):
    """
    Gera relatório DASN-SIMEI (Declaração Anual do Simples Nacional - MEI)
    para auxiliar o MEI no preenchimento da declaração anual
    """
    if year is None:
        year = timezone.now().year - 1  # Ano anterior por padrão
    
    # Período da declaração (ano completo)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # Buscar transações do período
    transactions = Transaction.objects.filter(
        company=company,
        transaction_date__range=[start_date, end_date]
    )
    
    # Cálculos para DASN-SIMEI
    receita_total = transactions.filter(transaction_type='income').aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0')
    
    # Receitas por categoria (importante para MEI)
    receitas_por_categoria = {}
    for transaction in transactions.filter(transaction_type='income'):
        categoria = transaction.category.name if transaction.category else 'Sem categoria'
        if categoria not in receitas_por_categoria:
            receitas_por_categoria[categoria] = Decimal('0')
        receitas_por_categoria[categoria] += transaction.amount
    
    # Despesas dedutíveis (para controle)
    despesas_dedutiveis = transactions.filter(
        transaction_type='expense',
        category__name__in=[
            'Material de escritório',
            'Telefone/Internet',
            'Combustível',
            'Manutenção de veículos',
            'Aluguel do local de trabalho',
            'Energia elétrica',
            'Água',
            'IPTU',
            'Materiais e insumos',
            'Equipamentos',
            'Cursos e capacitação'
        ]
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    # Informações importantes para DASN-SIMEI
    dados_dasn = {
        'empresa': company,
        'ano_declaracao': year,
        'periodo': f"01/01/{year} a 31/12/{year}",
        'receita_bruta_total': receita_total,
        'receitas_por_categoria': receitas_por_categoria,
        'despesas_dedutiveis': despesas_dedutiveis,
        'limite_mei': Decimal('81000.00'),  # Limite MEI para 2024/2025
        'dentro_do_limite': receita_total <= Decimal('81000.00'),
        'percentual_limite': (receita_total / Decimal('81000.00') * 100) if receita_total > 0 else 0,
    }
    
    # Informações adicionais
    dados_dasn.update({
        'possui_funcionario': False,  # MEI não pode ter funcionário CLT
        'receita_mensal_media': receita_total / 12,
        'alertas': []
    })
    
    # Alertas importantes
    if receita_total > Decimal('81000.00'):
        dados_dasn['alertas'].append({
            'tipo': 'erro',
            'mensagem': f'ATENÇÃO: Receita excedeu o limite MEI de R$ 81.000,00. Você pode precisar migrar para ME.'
        })
    elif receita_total > Decimal('64800.00'):  # 80% do limite
        dados_dasn['alertas'].append({
            'tipo': 'aviso',
            'mensagem': f'ATENÇÃO: Receita ultrapassou 80% do limite MEI. Monitore para não exceder R$ 81.000,00.'
        })
    
    if receita_total == 0:
        dados_dasn['alertas'].append({
            'tipo': 'info',
            'mensagem': 'Mesmo sem receita, você deve fazer a declaração DASN-SIMEI.'
        })
    
    return create_dasn_simei_pdf(dados_dasn)


def create_dasn_simei_pdf(dados):
    """Cria PDF do relatório DASN-SIMEI"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563eb')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#1f2937')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Construir documento
    elements = []
    
    # Título
    elements.append(Paragraph("RELATÓRIO DASN-SIMEI", title_style))
    elements.append(Paragraph(f"Declaração Anual do Simples Nacional - MEI", styles['Normal']))
    elements.append(Paragraph(f"Ano-calendário: {dados['ano_declaracao']}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Informações da empresa
    elements.append(Paragraph("DADOS DA EMPRESA", heading_style))
    empresa_data = [
        ['Razão Social:', dados['empresa'].name],
        ['CNPJ:', dados['empresa'].cnpj or 'Não informado'],
        ['Período da Declaração:', dados['periodo']],
    ]
    
    empresa_table = Table(empresa_data, colWidths=[4*cm, 12*cm])
    empresa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(empresa_table)
    elements.append(Spacer(1, 20))
    
    # Resumo da Receita Bruta
    elements.append(Paragraph("RESUMO DA RECEITA BRUTA", heading_style))
    
    # Status do limite
    status_cor = colors.green if dados['dentro_do_limite'] else colors.red
    status_text = "DENTRO DO LIMITE" if dados['dentro_do_limite'] else "EXCEDEU O LIMITE"
    
    receita_data = [
        ['Receita Bruta Total:', f"R$ {dados['receita_bruta_total']:,.2f}"],
        ['Limite MEI 2024:', f"R$ {dados['limite_mei']:,.2f}"],
        ['Percentual do Limite:', f"{dados['percentual_limite']:.1f}%"],
        ['Situação:', status_text],
        ['Receita Média Mensal:', f"R$ {dados['receita_mensal_media']:,.2f}"],
    ]
    
    receita_table = Table(receita_data, colWidths=[6*cm, 10*cm])
    receita_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        # Destaque na linha da situação
        ('BACKGROUND', (1, 3), (1, 3), status_cor),
        ('TEXTCOLOR', (1, 3), (1, 3), colors.white),
        ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
    ]))
    
    elements.append(receita_table)
    elements.append(Spacer(1, 20))
    
    # Receitas por categoria
    if dados['receitas_por_categoria']:
        elements.append(Paragraph("RECEITAS POR CATEGORIA", heading_style))
        
        categoria_data = [['Categoria', 'Valor', '% do Total']]
        for categoria, valor in sorted(dados['receitas_por_categoria'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentual = (valor / dados['receita_bruta_total'] * 100) if dados['receita_bruta_total'] > 0 else 0
            categoria_data.append([
                categoria,
                f"R$ {valor:,.2f}",
                f"{percentual:.1f}%"
            ])
        
        categoria_table = Table(categoria_data, colWidths=[8*cm, 4*cm, 4*cm])
        categoria_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(categoria_table)
        elements.append(Spacer(1, 20))
    
    # Alertas e observações
    if dados['alertas']:
        elements.append(Paragraph("ALERTAS E OBSERVAÇÕES", heading_style))
        
        for alerta in dados['alertas']:
            cor_fundo = {
                'erro': colors.HexColor('#fee2e2'),
                'aviso': colors.HexColor('#fef3c7'),
                'info': colors.HexColor('#dbeafe')
            }.get(alerta['tipo'], colors.HexColor('#f3f4f6'))
            
            elements.append(Paragraph(f"• {alerta['mensagem']}", normal_style))
        
        elements.append(Spacer(1, 20))
    
    # Instruções para preenchimento
    elements.append(Paragraph("INSTRUÇÕES PARA PREENCHIMENTO DA DASN-SIMEI", heading_style))
    
    instrucoes = [
        "1. Acesse o Portal do Empreendedor (www.gov.br/empreendedor)",
        "2. Clique em 'Já sou MEI' > 'Declaração Anual'",
        "3. Informe seu CNPJ e código de acesso",
        "4. Na pergunta 'Teve receita?', responda 'SIM' se houve faturamento",
        f"5. Informe a receita bruta total: R$ {dados['receita_bruta_total']:,.2f}",
        "6. Na pergunta 'Teve funcionário?', responda 'NÃO' (MEI não pode ter CLT)",
        "7. Confira todos os dados e transmita a declaração",
        "8. Guarde o comprovante de transmissão"
    ]
    
    if dados['receita_bruta_total'] == 0:
        instrucoes[3] = "4. Na pergunta 'Teve receita?', responda 'NÃO'"
        instrucoes[4] = "5. Pule a informação de receita bruta"
    
    for instrucao in instrucoes:
        elements.append(Paragraph(instrucao, normal_style))
    
    elements.append(Spacer(1, 20))
    
    # Informações importantes
    elements.append(Paragraph("INFORMAÇÕES IMPORTANTES", heading_style))
    
    info_importantes = [
        "• A DASN-SIMEI deve ser entregue até 31 de maio do ano seguinte",
        "• Mesmo sem receita, a declaração é obrigatória",
        "• Multa por atraso: R$ 50,00 por mês ou fração",
        "• Mantenha todos os comprovantes organizados para consulta",
        f"• Este relatório foi gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}",
        "• Consulte sempre um contador para orientações específicas"
    ]
    
    for info in info_importantes:
        elements.append(Paragraph(info, normal_style))
    
    # Rodapé
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Relatório gerado pelo CashFlow Manager", 
                             ParagraphStyle('Footer', parent=styles['Normal'], 
                                          fontSize=8, alignment=TA_CENTER, 
                                          textColor=colors.grey)))
    
    # Gerar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


# Adicionar import necessário
from django.db import models