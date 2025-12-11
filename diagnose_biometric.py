"""
Script de diagnóstico para autenticação biométrica WebAuthn
Execute: python diagnose_biometric.py
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import WebAuthnCredential

User = get_user_model()

def diagnose_biometric_auth():
    print("🔐 DIAGNÓSTICO DE AUTENTICAÇÃO BIOMÉTRICA")
    print("=" * 60)

    # 1. Verificar biblioteca WebAuthn
    try:
        import webauthn
        print("✅ Biblioteca webauthn instalada")
        print(f"   Versão: {webauthn.__version__}")
    except ImportError:
        print("❌ Biblioteca webauthn NÃO instalada")
        print("   Execute: pip install webauthn")
        return

    # 2. Verificar modelo WebAuthnCredential
    try:
        from core.models import WebAuthnCredential
        print("✅ Modelo WebAuthnCredential encontrado")

        # Verificar se tabela existe
        count = WebAuthnCredential.objects.count()
        print(f"   Credenciais registradas: {count}")

    except Exception as e:
        print(f"❌ Erro no modelo WebAuthnCredential: {str(e)}")
        return

    # 3. Verificar usuários
    users = User.objects.all()
    print(f"\n👥 USUÁRIOS ({users.count()} encontrados):")
    for user in users[:5]:  # Mostrar apenas os primeiros 5
        has_biometric = hasattr(user, 'webauthn_credential')
        status = "✅ Registrado" if has_biometric else "❌ Não registrado"
        print(f"   {user.email}: {status}")

    # 4. Verificar URLs WebAuthn
    from django.urls import reverse
    try:
        urls_to_check = [
            'webauthn_register_options',
            'webauthn_register_verify',
            'webauthn_auth_options',
            'webauthn_auth_verify',
            'webauthn_remove'
        ]

        print("\n🔗 URLs WEBAUTHN:")
        for url_name in urls_to_check:
            try:
                url = reverse(f'api:{url_name}')
                print(f"   ✅ {url_name}: {url}")
            except Exception as e:
                print(f"   ❌ {url_name}: Erro - {str(e)}")

    except Exception as e:
        print(f"❌ Erro ao verificar URLs: {str(e)}")

    # 5. Verificar arquivos estáticos
    static_files = [
        'static/js/biometric-auth.js',
        'templates/accounts/settings.html',
        'templates/accounts/login.html'
    ]

    print("\n📁 ARQUIVOS ESTÁTICOS:")
    for file_path in static_files:
        full_path = os.path.join(settings.BASE_DIR, file_path)
        exists = os.path.exists(full_path)
        status = "✅ Existe" if exists else "❌ Não encontrado"
        print(f"   {file_path}: {status}")

    print("\n" + "=" * 60)
    print("📋 PRÓXIMOS PASSOS PARA TESTAR:")
    print("1. Acesse /accounts/login/ e veja se aparece o botão 'Entrar com Biometria'")
    print("2. Vá em Configurações > Autenticação Biométrica")
    print("3. Clique em 'Registrar Biometria' (se disponível)")
    print("4. Teste o login biométrico")
    print("\n🔧 DEPURAÇÃO:")
    print("- Verifique o console do navegador (F12) para erros JavaScript")
    print("- Verifique os logs do Django para erros do servidor")
    print("- Certifique-se de que está usando HTTPS em produção")

if __name__ == '__main__':
    diagnose_biometric_auth()