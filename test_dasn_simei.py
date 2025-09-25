import os
import sys
import django
from datetime import date

# Setup do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashflow_manager.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import Company
from transactions.models import Transaction, Category, Account
from reports.dasn_simei import generate_dasn_simei_report
from decimal import Decimal

def test_dasn_simei_functionality():
    """Teste básico da funcionalidade DASN-SIMEI"""
    
    print("🧪 Iniciando testes do DASN-SIMEI...")
    
    User = get_user_model()
    
    # Buscar dados existentes
    user = User.objects.first()
    if not user:
        print("❌ Nenhum usuário encontrado")
        return False
        
    company = user.companies.first()
    if not company:
        print("❌ Nenhuma empresa encontrada")
        return False
    
    print(f"✅ Testando com empresa: {company.name}")
    
    # Verificar transações de 2024
    transactions_2024 = Transaction.objects.filter(
        company=company,
        transaction_date__year=2024,
        transaction_type='income'
    )
    
    total_receitas = sum(t.amount for t in transactions_2024)
    print(f"📊 Total de receitas 2024: R$ {total_receitas:,.2f}")
    print(f"📈 Quantidade de transações: {transactions_2024.count()}")
    
    # Testar geração do relatório
    try:
        print("🔄 Gerando relatório DASN-SIMEI...")
        pdf_buffer = generate_dasn_simei_report(company, 2024)
        
        if pdf_buffer and len(pdf_buffer.getvalue()) > 0:
            print(f"✅ PDF gerado com sucesso! Tamanho: {len(pdf_buffer.getvalue())} bytes")
            
            # Salvar para verificação
            with open('test_dasn_simei.pdf', 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print("💾 PDF salvo como 'test_dasn_simei.pdf'")
            
            return True
        else:
            print("❌ Erro: PDF vazio")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dasn_simei_functionality()
    if success:
        print("\n🎉 Todos os testes passaram! Funcionalidade DASN-SIMEI está funcionando.")
        sys.exit(0)
    else:
        print("\n💥 Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)