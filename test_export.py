#!/usr/bin/env python
"""
Script para testar exportação de relatórios
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

def test_export():
    """Testa a funcionalidade de exportação"""
    client = Client()
    
    # Fazer login com usuário admin
    client.login(username='admin', password='admin123')
    
    # Testar exportação PDF
    url = '/core/export/?start_date=2025-09-01&end_date=2025-09-23&type=cash_flow&format=pdf&title=teste'
    
    print("Testando exportação PDF...")
    try:
        response = client.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Exportação PDF funcionou!")
            print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
            print(f"Content-Length: {len(response.content)} bytes")
        elif response.status_code == 302:
            print(f"↪️ Redirecionamento para: {response.get('Location', 'N/A')}")
        else:
            print(f"❌ Erro {response.status_code}")
            print(f"Response: {response.content.decode()[:500]}...")
            
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_export()