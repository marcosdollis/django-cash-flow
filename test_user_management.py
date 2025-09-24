"""
Script para testar o sistema de perfil e gerenciamento de usuários
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Company, CompanyMember
from django.db import transaction

User = get_user_model()

def test_user_permissions():
    """Testa sistema de permissões de usuários"""
    print("🧪 Testando sistema de permissões de usuários...")
    
    try:
        # Encontrar ou criar uma empresa de teste
        company = Company.objects.first()
        if not company:
            print("❌ Nenhuma empresa encontrada no sistema")
            return False
        
        print(f"✅ Empresa encontrada: {company.name}")
        
        # Testar usuários existentes
        users = User.objects.all()[:3]
        
        for user in users:
            print(f"\n👤 Testando usuário: {user.username}")
            
            # Testar métodos de permissão
            role = user.get_company_role(company)
            print(f"   - Papel na empresa: {role}")
            
            is_admin = user.is_company_admin(company)
            print(f"   - É admin: {is_admin}")
            
            can_manage = user.can_manage_users(company)
            print(f"   - Pode gerenciar usuários: {can_manage}")
            
            can_create = user.can_create_users(company)
            print(f"   - Pode criar usuários: {can_create}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar permissões: {e}")
        return False

def test_company_members():
    """Testa sistema de membros da empresa"""
    print("\n🧪 Testando sistema de membros da empresa...")
    
    try:
        company = Company.objects.first()
        if not company:
            print("❌ Nenhuma empresa encontrada")
            return False
        
        members = CompanyMember.objects.filter(company=company)
        print(f"✅ Membros encontrados: {members.count()}")
        
        for member in members:
            print(f"   - {member.user.get_full_name() or member.user.username} - {member.get_role_display()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar membros: {e}")
        return False

def test_create_test_users():
    """Cria usuários de teste para diferentes papéis"""
    print("\n🧪 Criando usuários de teste...")
    
    try:
        company = Company.objects.first()
        if not company:
            print("❌ Nenhuma empresa encontrada")
            return False
        
        # Usuários de teste
        test_users = [
            {
                'username': 'admin_test',
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'Teste',
                'role': 'admin'
            },
            {
                'username': 'manager_test',
                'email': 'manager@test.com',
                'first_name': 'Manager',
                'last_name': 'Teste',
                'role': 'manager'
            },
            {
                'username': 'user_test',
                'email': 'user@test.com',
                'first_name': 'User',
                'last_name': 'Teste',
                'role': 'user'
            }
        ]
        
        with transaction.atomic():
            for user_data in test_users:
                # Verificar se já existe
                if User.objects.filter(username=user_data['username']).exists():
                    print(f"   ⚠️  Usuário {user_data['username']} já existe")
                    continue
                
                # Criar usuário
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password='teste123'
                )
                
                # Adicionar à empresa
                CompanyMember.objects.create(
                    user=user,
                    company=company,
                    role=user_data['role']
                )
                
                print(f"   ✅ Usuário {user_data['username']} criado com papel {user_data['role']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários de teste: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema de perfil e gerenciamento de usuários\n")
    
    # Executar testes
    tests = [
        test_company_members,
        test_user_permissions,
        test_create_test_users,
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
        print("\n🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    return all(results)

if __name__ == '__main__':
    main()