#!/usr/bin/env python
"""
Script para testar o processo completo de registro e criação de empresa
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import Company, CompanyMember
from django.urls import reverse

User = get_user_model()

def test_company_setup_flow():
    """Testa o fluxo completo de setup de empresa"""
    print("🧪 Testando fluxo de setup de empresa...")
    
    client = Client()
    
    # Criar usuário de teste
    test_username = 'test_company_setup'
    test_email = 'testcompany@setup.com'
    
    # Limpar usuário de teste anterior se existir
    User.objects.filter(username=test_username).delete()
    
    try:
        # 1. Criar usuário via registro
        print("\n1️⃣ Testando registro de usuário...")
        register_data = {
            'username': test_username,
            'first_name': 'Test',
            'last_name': 'Company',
            'email': test_email,
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        register_response = client.post(reverse('accounts:register'), register_data)
        print(f"   Status do registro: {register_response.status_code}")
        
        if register_response.status_code == 302:
            print("   ✅ Usuário registrado com sucesso")
            redirect_url = register_response.url
            print(f"   Redirecionado para: {redirect_url}")
        else:
            print("   ❌ Erro no registro")
            return False
        
        # 2. Verificar se o usuário foi criado
        test_user = User.objects.get(username=test_username)
        print(f"   Usuário criado: {test_user.username} - {test_user.email}")
        print(f"   Empresas do usuário: {test_user.companies.count()}")
        
        # 3. Testar acesso à página de setup
        print("\n2️⃣ Testando acesso à página de setup...")
        
        # Login do usuário
        login_success = client.login(username=test_username, password='testpass123')
        print(f"   Login realizado: {login_success}")
        
        if not login_success:
            print("   ❌ Falha no login")
            return False
        
        # Acessar página de setup
        setup_url = reverse('accounts:company_setup')
        setup_response = client.get(setup_url)
        print(f"   Status setup page: {setup_response.status_code}")
        
        if setup_response.status_code == 200:
            print("   ✅ Página de setup acessível")
            
            # Verificar se tem o formulário
            if b'Configure sua Empresa' in setup_response.content:
                print("   ✅ Formulário de empresa encontrado")
            else:
                print("   ⚠️  Conteúdo da página parece incorreto")
        else:
            print(f"   ❌ Erro ao acessar página de setup: {setup_response.status_code}")
            if hasattr(setup_response, 'url'):
                print(f"   Redirecionado para: {setup_response.url}")
            return False
        
        # 4. Testar criação de empresa
        print("\n3️⃣ Testando criação de empresa...")
        
        company_data = {
            'name': 'Empresa Teste Setup',
            'cnpj': '12345678000190',
            'phone': '(11) 99999-9999',
            'email': 'teste@empresa.com',
            'address': 'Rua Teste, 123',
            'primary_color': '#007bff'
        }
        
        create_response = client.post(setup_url, company_data)
        print(f"   Status criação empresa: {create_response.status_code}")
        
        if create_response.status_code == 302:
            print("   ✅ Empresa criada com sucesso")
            print(f"   Redirecionado para: {create_response.url}")
            
            # Verificar se a empresa foi criada
            test_user.refresh_from_db()
            if test_user.companies.count() > 0:
                company = test_user.companies.first()
                print(f"   Empresa criada: {company.name}")
                print(f"   Papel do usuário: {test_user.get_company_role(company)}")
                return True
            else:
                print("   ❌ Empresa não foi criada no banco de dados")
                return False
        else:
            print(f"   ❌ Erro na criação da empresa")
            print(f"   Conteúdo da resposta: {setup_response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False
    
    finally:
        # Limpar dados de teste
        print("\n🧹 Limpando dados de teste...")
        try:
            User.objects.filter(username=test_username).delete()
            Company.objects.filter(name='Empresa Teste Setup').delete()
            print("   ✅ Dados de teste removidos")
        except:
            pass


def test_existing_user_without_company():
    """Testa usuário existente sem empresa"""
    print("\n🧪 Testando usuário existente sem empresa...")
    
    # Encontrar usuário sem empresa
    users_without_company = User.objects.filter(companies__isnull=True)
    
    if users_without_company.exists():
        user = users_without_company.first()
        print(f"   Usuário encontrado: {user.username}")
        
        # Testar login e redirecionamento
        client = Client()
        
        # Simular que conhecemos a senha ou definir uma
        user.set_password('teste123')
        user.save()
        
        login_success = client.login(username=user.username, password='teste123')
        
        if login_success:
            print("   ✅ Login realizado")
            
            # Testar acesso ao dashboard (deveria redirecionar para setup)
            dashboard_response = client.get('/core/')
            print(f"   Status dashboard: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 302:
                print(f"   Redirecionado para: {dashboard_response.url}")
                if 'company/setup' in dashboard_response.url:
                    print("   ✅ Redirecionamento para setup funcionando")
                    return True
            else:
                print("   ⚠️  Não foi redirecionado")
        else:
            print("   ❌ Falha no login")
            
    else:
        print("   ℹ️  Nenhum usuário sem empresa encontrado")
    
    return False


if __name__ == '__main__':
    print("🚀 Iniciando testes de setup de empresa...\n")
    
    # Teste 1: Fluxo completo de registro e setup
    success1 = test_company_setup_flow()
    
    # Teste 2: Usuário existente sem empresa
    success2 = test_existing_user_without_company()
    
    print(f"\n📊 Resultados:")
    print(f"   Fluxo completo: {'✅' if success1 else '❌'}")
    print(f"   Usuário sem empresa: {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print("\n🎉 Todos os testes passaram!")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os problemas acima.")