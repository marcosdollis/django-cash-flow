#!/usr/bin/env python
"""
Script para testar funcionalidades de logout e sessão
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Company

def test_logout_functionality():
    """Testa a funcionalidade de logout"""
    
    print("🔐 Testando funcionalidade de logout e sessão...")
    
    # Criar cliente de teste
    client = Client()
    
    # Pegar usuário existente
    user = User.objects.first()
    if not user:
        print("❌ Nenhum usuário encontrado")
        return
    
    print(f"👤 Usuário de teste: {user.username}")
    
    # Fazer login
    login_successful = client.force_login(user)
    print(f"✅ Login realizado: {user.username}")
    
    # Verificar se está autenticado
    response = client.get('/core/')
    if response.status_code == 200:
        print("✅ Usuário autenticado - acesso ao dashboard OK")
    elif response.status_code == 302:
        print("ℹ️ Redirecionamento detectado (normal se não logado)")
    else:
        print(f"⚠️ Status inesperado: {response.status_code}")
    
    # Testar logout via GET (deve falhar ou redirecionar)
    print("\n🔗 Testando logout via GET...")
    logout_url = reverse('accounts:logout')
    response = client.get(logout_url)
    print(f"   Status GET: {response.status_code}")
    
    # Testar logout via POST (deve funcionar)
    print("\n📤 Testando logout via POST...")
    response = client.post(logout_url)
    print(f"   Status POST: {response.status_code}")
    
    if response.status_code == 302:
        print(f"   Redirecionamento para: {response.url}")
        
        # Verificar se realmente foi deslogado
        response_after_logout = client.get('/core/')
        if response_after_logout.status_code == 302:
            print("✅ Logout bem-sucedido - redirecionando para login")
        else:
            print("❌ Logout falhou - ainda autenticado")
    
    # Testar acesso a páginas protegidas após logout
    print("\n🔒 Testando acesso a páginas protegidas após logout...")
    protected_urls = [
        '/core/',
        '/transactions/',
        '/reports/',
        '/accounts/profile/'
    ]
    
    for url in protected_urls:
        try:
            response = client.get(url)
            if response.status_code == 302:
                print(f"   {url}: ✅ Redirecionando para login (correto)")
            elif response.status_code == 200:
                print(f"   {url}: ❌ Acesso permitido (incorreto!)")
            else:
                print(f"   {url}: Status {response.status_code}")
        except Exception as e:
            print(f"   {url}: Erro - {e}")

def test_session_settings():
    """Testa configurações de sessão"""
    print("\n🛠️ Verificando configurações de sessão...")
    
    from django.conf import settings
    
    session_settings = {
        'SESSION_COOKIE_AGE': getattr(settings, 'SESSION_COOKIE_AGE', 'Não definido'),
        'SESSION_SAVE_EVERY_REQUEST': getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', 'Não definido'),
        'SESSION_EXPIRE_AT_BROWSER_CLOSE': getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', 'Não definido'),
        'SESSION_COOKIE_HTTPONLY': getattr(settings, 'SESSION_COOKIE_HTTPONLY', 'Não definido'),
        'LOGIN_URL': getattr(settings, 'LOGIN_URL', 'Não definido'),
        'LOGOUT_REDIRECT_URL': getattr(settings, 'LOGOUT_REDIRECT_URL', 'Não definido'),
    }
    
    for setting, value in session_settings.items():
        print(f"   {setting}: {value}")

def test_middleware_order():
    """Verifica a ordem dos middlewares"""
    print("\n⚙️ Verificando ordem dos middlewares...")
    
    from django.conf import settings
    
    expected_order = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
    
    current_middleware = settings.MIDDLEWARE
    
    for i, middleware in enumerate(expected_order):
        if i < len(current_middleware) and middleware == current_middleware[i]:
            print(f"   ✅ {middleware}")
        else:
            print(f"   ❌ {middleware} - posição incorreta ou ausente")

if __name__ == '__main__':
    test_logout_functionality()
    test_session_settings()
    test_middleware_order()
    print("\n🔗 Para testar manualmente:")
    print("   1. Acesse: http://127.0.0.1:8000/accounts/login/")
    print("   2. Faça login")
    print("   3. Clique em 'Sair' no menu do usuário")
    print("   4. Verifique se foi redirecionado para login")
    print("   5. Tente acessar http://127.0.0.1:8000/core/ diretamente")