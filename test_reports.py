#!/usr/bin/env python
"""
Script para testar todas as URLs de relatórios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import Company, CompanyMember

User = get_user_model()

def test_reports_urls():
    """Testa todas as URLs de relatórios"""
    client = Client()
    
    # Criar usuário de teste se não existir
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
    
    # Fazer login
    client.login(username='admin', password='admin123')
    
    # URLs para testar
    urls = [
        '/reports/',
        '/reports/generate/',
        '/reports/forecasts/',
        '/reports/alerts/',
        '/core/export/',
        '/core/insights/',
    ]
    
    print("Testando URLs de relatórios...")
    
    for url in urls:
        try:
            response = client.get(url)
            status = "✅ OK" if response.status_code == 200 else f"❌ Erro {response.status_code}"
            print(f"{url:30} -> {status}")
            
            if response.status_code >= 400:
                print(f"   Erro: {response.content.decode()[:200]}...")
                
        except Exception as e:
            print(f"{url:30} -> ❌ Exceção: {str(e)}")
    
    print("\nTeste concluído!")

if __name__ == "__main__":
    test_reports_urls()