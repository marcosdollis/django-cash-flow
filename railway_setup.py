#!/usr/bin/env python
"""
Script de inicialização pós-deploy para Railway
Cria usuário admin padrão e configurações básicas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Company, CompanyMember

User = get_user_model()

def setup_railway():
    print("🚂 Iniciando setup do Railway...")
    
    # Verificar se já existe usuário admin
    if User.objects.filter(username='admin').exists():
        print("✅ Usuário admin já existe")
        return
    
    # Criar usuário admin
    print("👤 Criando usuário administrador...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@cashflow.com',
        password='Change.This.Password.123!',
        first_name='Admin',
        last_name='Railway'
    )
    print(f"✅ Usuário criado: {admin_user.username}")
    
    # Criar empresa demo
    print("🏢 Criando empresa demo...")
    company = Company.objects.create(
        name="Empresa Demo Railway",
        document="00000000000191"
    )
    
    # Associar admin à empresa
    CompanyMember.objects.create(
        user=admin_user,
        company=company,
        role='owner'
    )
    print(f"✅ Empresa criada: {company.name}")
    
    print("\n" + "="*50)
    print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("="*50)
    print(f"\n📧 Email: admin@cashflow.com")
    print(f"🔑 Senha: Change.This.Password.123!")
    print(f"\n⚠️  IMPORTANTE: Altere a senha após primeiro login!")
    print("="*50 + "\n")

if __name__ == '__main__':
    setup_railway()
