#!/usr/bin/env python
"""
Script para inicializar dados básicos no ambiente de produção
Executa após as migrações no deploy
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from accounts.models import Company, CompanyMember
from transactions.models import Category


def create_default_categories(company):
    """Criar categorias padrão para MEI"""
    
    # Categorias de receita
    income_categories = [
        'Vendas de Produtos',
        'Prestação de Serviços',
        'Vendas Online',
        'Comissões',
        'Outras Receitas',
    ]
    
    # Categorias de despesa
    expense_categories = [
        'Compra de Mercadorias',
        'Material de Escritório',
        'Combustível',
        'Manutenção',
        'Marketing e Publicidade',
        'Telefone/Internet',
        'Contador',
        'Taxas e Impostos',
        'Alimentação',
        'Outras Despesas',
    ]
    
    print("📊 Criando categorias padrão...")
    
    # Criar categorias de receita
    for name in income_categories:
        category, created = Category.objects.get_or_create(
            company=company,
            name=name,
            defaults={
                'category_type': 'income',
                'description': f'Categoria de receita: {name}',
                'is_active': True
            }
        )
        if created:
            print(f"✅ Receita: {name}")
    
    # Criar categorias de despesa
    for name in expense_categories:
        category, created = Category.objects.get_or_create(
            company=company,
            name=name,
            defaults={
                'category_type': 'expense', 
                'description': f'Categoria de despesa: {name}',
                'is_active': True
            }
        )
        if created:
            print(f"✅ Despesa: {name}")


def setup_demo_company():
    """Criar empresa demo se não existir nenhuma"""
    
    if Company.objects.count() == 0:
        print("🏢 Criando empresa demo...")
        
        company = Company.objects.create(
            name='MEI Exemplo',
            cnpj='12345678000100',
            business_type='service',
            is_active=True
        )
        
        # Associar ao superuser se existir
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            CompanyMember.objects.create(
                user=admin_user,
                company=company,
                role='admin',
                is_active=True
            )
            print(f"✅ Empresa associada ao usuário admin")
        
        # Criar categorias padrão
        create_default_categories(company)
        
        print(f"✅ Empresa demo criada: {company.name}")
        return company
    else:
        company = Company.objects.first()
        print(f"✅ Empresa existente: {company.name}")
        return company


def main():
    """Função principal de inicialização"""
    print("🚀 INICIALIZANDO DADOS DE PRODUÇÃO")
    print("=" * 50)
    
    try:
        # Verificar se já existe um superuser
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superuser já existe")
        else:
            print("⚠️  Nenhum superuser encontrado")
            print("   Use: python manage.py createsuperuser")
        
        # Configurar empresa demo
        company = setup_demo_company()
        
        print("\n" + "=" * 50)
        print("✅ INICIALIZAÇÃO CONCLUÍDA!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Acesse /admin para configurar o sistema")
        print("2. Crie usuários e empresas conforme necessário")
        print("3. Configure as categorias personalizadas")
        print("4. Teste o sistema completo")
        
    except Exception as e:
        print(f"\n❌ ERRO NA INICIALIZAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()