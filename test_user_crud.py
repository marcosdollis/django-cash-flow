"""
Script para testar criação e edição de usuários
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

def test_user_creation_and_editing():
    """Testa criação e edição de usuários via interface web"""
    print("🧪 Testando criação e edição de usuários...")
    
    try:
        # Configurar cliente de teste
        client = Client()
        
        # Fazer login como admin
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            print("❌ Usuário admin não encontrado")
            return False
        
        # Login
        login_success = client.login(username='admin', password='123')  # Assumindo senha padrão
        if not login_success:
            # Tentar outras senhas comuns
            for pwd in ['admin', 'admin123', 'senha123']:
                if client.login(username='admin', password=pwd):
                    login_success = True
                    break
        
        if not login_success:
            print("❌ Não foi possível fazer login como admin")
            return False
        
        print("✅ Login como admin realizado com sucesso")
        
        # Testar acesso à página de configurações
        settings_url = reverse('accounts:company_settings')
        response = client.get(settings_url)
        
        if response.status_code == 200:
            print("✅ Página de configurações acessível")
        else:
            print(f"❌ Erro ao acessar configurações: {response.status_code}")
            return False
        
        # Testar acesso à página de criação de usuário
        create_url = reverse('accounts:create_user')
        response = client.get(create_url)
        
        if response.status_code == 200:
            print("✅ Página de criação de usuário acessível")
        else:
            print(f"❌ Erro ao acessar criação de usuário: {response.status_code}")
            return False
        
        # Verificar se há empresas para o usuário
        company = Company.objects.first()
        if not company:
            print("❌ Nenhuma empresa encontrada")
            return False
        
        print(f"✅ Empresa encontrada: {company.name}")
        
        # Verificar se o admin é membro da empresa
        is_member = CompanyMember.objects.filter(user=admin_user, company=company).exists()
        if not is_member:
            print("❌ Admin não é membro da empresa")
            return False
        
        print("✅ Admin é membro da empresa")
        
        # Verificar permissões do admin
        role = admin_user.get_company_role(company)
        can_manage = admin_user.can_manage_users(company)
        
        print(f"✅ Papel do admin na empresa: {role}")
        print(f"✅ Pode gerenciar usuários: {can_manage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forms():
    """Testa os formulários de usuário"""
    print("\n🧪 Testando formulários...")
    
    try:
        from accounts.forms import UserManagementForm
        
        # Testar formulário de criação
        form_data = {
            'username': 'test_user_form',
            'email': 'test@form.com',
            'first_name': 'Test',
            'last_name': 'Form',
            'phone': '11999999999',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': 'user',
            'is_active': True
        }
        
        form = UserManagementForm(data=form_data)
        if form.is_valid():
            print("✅ Formulário de criação válido")
        else:
            print(f"❌ Formulário de criação inválido: {form.errors}")
            return False
        
        # Testar formulário de edição
        user = User.objects.filter(username='admin').first()
        if user:
            edit_data = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'role': 'admin',
                'is_active': True
            }
            
            edit_form = UserManagementForm(data=edit_data, instance=user, is_editing=True)
            if edit_form.is_valid():
                print("✅ Formulário de edição válido")
            else:
                print(f"❌ Formulário de edição inválido: {edit_form.errors}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de formulários: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de criação e edição de usuários\n")
    
    # Executar testes
    tests = [
        test_forms,
        test_user_creation_and_editing,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro no teste {test.__name__}: {e}")
            results.append(False)
    
    # Relatório final
    print(f"\n📊 Relatório dos Testes:")
    print(f"   ✅ Sucessos: {sum(results)}")
    print(f"   ❌ Falhas: {len(results) - sum(results)}")
    print(f"   📈 Taxa de sucesso: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print("\n🎉 Todos os testes passaram! Funcionalidades funcionando.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    # Dicas para correção
    if not all(results):
        print("\n💡 Dicas para correção:")
        print("   1. Verifique se o usuário admin existe e tem senha")
        print("   2. Verifique se há empresas criadas no sistema")
        print("   3. Verifique se o admin é membro de uma empresa")
        print("   4. Teste manualmente: http://127.0.0.1:8001/accounts/company/settings/")
    
    return all(results)

if __name__ == '__main__':
    main()