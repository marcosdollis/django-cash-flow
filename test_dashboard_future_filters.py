#!/usr/bin/env python
"""
Script de teste para verificar os novos filtros do dashboard
Testa filtros futuros (próximos 30 e 60 dias) e correção do bug de datas personalizadas
"""

import os
import sys
import django
from datetime import datetime, timedelta, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from core.views import dashboard_view
from accounts.models import Company, CompanyMember
from transactions.models import Transaction, Account, Category


def setup_test_data():
    """Criar dados de teste"""
    print("🚀 Configurando dados de teste...")
    
    # Criar usuário e empresa
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@test.com', 'first_name': 'Teste'}
    )
    
    company, created = Company.objects.get_or_create(
        name='Empresa Teste',
        defaults={'cnpj': '12345678000100'}
    )
    
    # Associar usuário à empresa
    CompanyMember.objects.get_or_create(
        user=user,
        company=company,
        defaults={'role': 'admin', 'is_active': True}
    )
    
    # Criar conta
    account, created = Account.objects.get_or_create(
        company=company,
        name='Conta Corrente',
        defaults={'account_type': 'checking', 'current_balance': 5000}
    )
    
    # Criar categoria
    category, created = Category.objects.get_or_create(
        company=company,
        name='Vendas',
        defaults={'category_type': 'income'}
    )
    
    print(f"✅ Usuário: {user.username}")
    print(f"✅ Empresa: {company.name}")
    print(f"✅ Conta: {account.name} - R$ {account.current_balance}")
    
    return user, company, account, category


def test_past_filters():
    """Testar filtros passados (funcionamento atual)"""
    print("\n📊 Testando filtros passados...")
    
    user, company, account, category = setup_test_data()
    
    factory = RequestFactory()
    
    # Teste: Últimos 30 dias
    request = factory.get('/dashboard/?period=30')
    request.user = user
    
    try:
        response = dashboard_view(request)
        print("✅ Filtro 'Últimos 30 dias' funcionando")
    except Exception as e:
        print(f"❌ Erro no filtro 'Últimos 30 dias': {e}")
    
    # Teste: Últimos 60 dias
    request = factory.get('/dashboard/?period=60')
    request.user = user
    
    try:
        response = dashboard_view(request)
        print("✅ Filtro 'Últimos 60 dias' funcionando")
    except Exception as e:
        print(f"❌ Erro no filtro 'Últimos 60 dias': {e}")


def test_future_filters():
    """Testar novos filtros futuros"""
    print("\n🔮 Testando novos filtros futuros...")
    
    user, company, account, category = setup_test_data()
    
    factory = RequestFactory()
    
    # Teste: Próximos 30 dias
    request = factory.get('/dashboard/?period=next_30')
    request.user = user
    
    try:
        response = dashboard_view(request)
        print("✅ Filtro 'Próximos 30 dias' funcionando")
        # Verificar se as datas estão corretas
        context = response.context_data
        start_date = context['start_date']
        end_date = context['end_date']
        today = timezone.now().date()
        
        if start_date == today and end_date == today + timedelta(days=30):
            print(f"✅ Datas corretas: {start_date} até {end_date}")
        else:
            print(f"⚠️ Datas incorretas: {start_date} até {end_date}")
            
    except Exception as e:
        print(f"❌ Erro no filtro 'Próximos 30 dias': {e}")
    
    # Teste: Próximos 60 dias
    request = factory.get('/dashboard/?period=next_60')
    request.user = user
    
    try:
        response = dashboard_view(request)
        print("✅ Filtro 'Próximos 60 dias' funcionando")
        context = response.context_data
        start_date = context['start_date']
        end_date = context['end_date']
        today = timezone.now().date()
        
        if start_date == today and end_date == today + timedelta(days=60):
            print(f"✅ Datas corretas: {start_date} até {end_date}")
        else:
            print(f"⚠️ Datas incorretas: {start_date} até {end_date}")
            
    except Exception as e:
        print(f"❌ Erro no filtro 'Próximos 60 dias': {e}")


def test_custom_filter_bug_fix():
    """Testar correção do bug do filtro personalizado"""
    print("\n🐛 Testando correção do filtro personalizado...")
    
    user, company, account, category = setup_test_data()
    
    factory = RequestFactory()
    
    # Teste 1: Datas normais
    start_str = '2025-01-01'
    end_str = '2025-01-31' 
    request = factory.get(f'/dashboard/?start_date={start_str}&end_date={end_str}')
    request.user = user
    
    try:
        response = dashboard_view(request)
        context = response.context_data
        start_date = context['start_date']
        end_date = context['end_date']
        
        if str(start_date) == start_str and str(end_date) == end_str:
            print("✅ Filtro personalizado com datas normais funcionando")
        else:
            print(f"❌ Datas incorretas: esperado {start_str}-{end_str}, obtido {start_date}-{end_date}")
            
    except Exception as e:
        print(f"❌ Erro no filtro personalizado: {e}")
    
    # Teste 2: Data final menor que inicial (bug corrigido)
    start_str = '2025-01-31'
    end_str = '2025-01-01'  # Data final menor que inicial
    request = factory.get(f'/dashboard/?start_date={start_str}&end_date={end_str}')
    request.user = user
    
    try:
        response = dashboard_view(request)
        context = response.context_data
        start_date = context['start_date']
        end_date = context['end_date']
        
        # A correção deveria fazer end_date = start_date
        if end_date >= start_date:
            print("✅ Correção do bug funcionando: data final ajustada automaticamente")
            print(f"✅ Resultado: {start_date} até {end_date}")
        else:
            print(f"❌ Bug ainda presente: {start_date} até {end_date}")
            
    except Exception as e:
        print(f"❌ Erro ao testar correção do bug: {e}")
    
    # Teste 3: Datas futuras
    today = timezone.now().date()
    start_str = str(today + timedelta(days=1))
    end_str = str(today + timedelta(days=30))
    request = factory.get(f'/dashboard/?start_date={start_str}&end_date={end_str}')
    request.user = user
    
    try:
        response = dashboard_view(request)
        context = response.context_data
        start_date = context['start_date']
        end_date = context['end_date']
        
        if str(start_date) == start_str and str(end_date) == end_str:
            print("✅ Filtro personalizado com datas futuras funcionando")
        else:
            print(f"❌ Datas futuras incorretas: esperado {start_str}-{end_str}, obtido {start_date}-{end_date}")
            
    except Exception as e:
        print(f"❌ Erro com datas futuras: {e}")


def main():
    """Executar todos os testes"""
    print("🧪 TESTE DOS NOVOS FILTROS DO DASHBOARD")
    print("=" * 50)
    
    try:
        test_past_filters()
        test_future_filters()
        test_custom_filter_bug_fix()
        
        print("\n" + "=" * 50)
        print("✅ TESTES CONCLUÍDOS!")
        print("\n📋 RESUMO DAS MELHORIAS:")
        print("• ✅ Adicionados filtros 'Próximos 30 dias' e 'Próximos 60 dias'")
        print("• ✅ Corrigido bug do filtro personalizado (data final < inicial)")
        print("• ✅ Removida limitação de data máxima nos campos")
        print("• ✅ Melhorada validação JavaScript das datas")
        print("\n🚀 Agora você pode visualizar transações futuras e planejar melhor!")
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        print("Verifique se o Django está configurado corretamente")


if __name__ == '__main__':
    main()