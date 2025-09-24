#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Company, CompanyMember

User = get_user_model()

print(f"Total usuários: {User.objects.count()}")
print(f"Total empresas: {Company.objects.count()}")

admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"✅ Usuário admin existe: {admin_user.email}")
    print(f"Empresas do admin: {admin_user.companies.count()}")
    
    if admin_user.companies.count() == 0:
        print("🔧 Criando empresa para o admin...")
        company = Company.objects.create(
            name="Empresa Demo",
            document="12345678000190"
        )
        CompanyMember.objects.create(
            user=admin_user,
            company=company,
            role='admin'
        )
        print(f"✅ Empresa criada: {company.name}")
    else:
        company = admin_user.companies.first()
        print(f"✅ Empresa: {company.name}")
        
else:
    print("❌ Usuário admin não encontrado")
    print("Criando usuário admin...")
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    
    company = Company.objects.create(
        name="Empresa Demo",
        document="12345678000190"
    )
    CompanyMember.objects.create(
        user=admin_user,
        company=company,
        role='admin'
    )
    print(f"✅ Usuário e empresa criados!")