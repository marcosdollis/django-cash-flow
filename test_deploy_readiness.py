#!/usr/bin/env python
"""
Script para testar a aplicação localmente antes do deploy
Simula o ambiente de produção
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Executar comando e mostrar resultado"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    print("-" * 40)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - Sucesso!")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
    else:
        print(f"❌ {description} - Erro!")
        if result.stderr:
            print(f"Erro: {result.stderr.strip()}")
        return False
    
    return True

def check_dependencies():
    """Verificar se todas as dependências estão instaladas"""
    print("📦 Verificando dependências...")
    
    try:
        import django
        import psycopg2
        import gunicorn
        import whitenoise
        import dj_database_url
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def test_settings():
    """Testar configurações do Django"""
    print("⚙️ Testando configurações...")
    
    # Configurar ambiente de teste
    os.environ['DEBUG'] = 'False'
    os.environ['SECRET_KEY'] = 'test-key-for-validation'
    os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
        import django
        django.setup()
        
        from django.conf import settings
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ DATABASE: {settings.DATABASES['default']['ENGINE']}")
        print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"✅ MIDDLEWARE: WhiteNoise {'✅' if 'whitenoise' in str(settings.MIDDLEWARE) else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_migrations():
    """Testar migrações"""
    print("🗄️ Testando migrações...")
    
    return run_command(
        "python manage.py check --deploy",
        "Verificação de deployment"
    )

def test_static_files():
    """Testar coleta de arquivos estáticos"""
    print("📁 Testando arquivos estáticos...")
    
    return run_command(
        "python manage.py collectstatic --dry-run --verbosity=0",
        "Coleta de arquivos estáticos (dry-run)"
    )

def test_build_script():
    """Testar o script de build"""
    print("🔨 Testando script de build...")
    
    # Verificar se o build.sh existe e tem permissões
    if not os.path.exists('build.sh'):
        print("❌ Arquivo build.sh não encontrado")
        return False
    
    print("✅ Arquivo build.sh encontrado")
    
    # No Windows, testar os comandos individualmente
    commands = [
        ("pip install -r requirements.txt --dry-run", "Teste de dependências"),
        ("python manage.py check", "Verificação do Django"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def test_production_readiness():
    """Testar se está pronto para produção"""
    print("🚀 Verificando prontidão para produção...")
    
    checks = [
        ("Arquivo render.yaml existe", os.path.exists('render.yaml')),
        ("Arquivo build.sh existe", os.path.exists('build.sh')),
        ("Arquivo requirements.txt existe", os.path.exists('requirements.txt')),
        ("Arquivo .env.example existe", os.path.exists('.env.example')),
        ("Arquivo .gitignore existe", os.path.exists('.gitignore')),
        ("Script de inicialização existe", os.path.exists('init_production_data.py')),
    ]
    
    all_good = True
    for check, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_good = False
    
    return all_good

def main():
    """Função principal"""
    print("🧪 TESTE PRÉ-DEPLOY - DJANGO CASH FLOW")
    print("=" * 50)
    
    tests = [
        ("Dependências", check_dependencies),
        ("Configurações", test_settings),
        ("Migrações", test_migrations),
        ("Arquivos Estáticos", test_static_files),
        ("Script de Build", test_build_script),
        ("Prontidão para Produção", test_production_readiness),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: PASSOU")
            else:
                print(f"❌ {name}: FALHOU")
        except Exception as e:
            print(f"❌ {name}: ERRO - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TUDO PRONTO PARA O DEPLOY!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Faça commit das alterações: git add . && git commit -m 'Preparado para deploy'")
        print("2. Envie para o GitHub: git push origin main")
        print("3. Configure no Render seguindo o DEPLOY_RENDER.md")
        print("4. Aguarde o deploy automático")
        return 0
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("Corrija os problemas antes de fazer o deploy")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)