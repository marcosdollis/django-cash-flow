from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from .models import Transaction

def test_main_page(request):
    """Página principal de teste"""
    return render(request, 'test_page.html')

@login_required
def test_transaction_detail(request, uuid):
    """View de teste para debug"""
    try:
        transaction = Transaction.objects.get(uuid=uuid)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Teste - Detalhes da Transação</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <div class="card">
                    <div class="card-header">
                        <h3>✅ Detalhes da Transação - FUNCIONANDO!</h3>
                    </div>
                    <div class="card-body">
                        <p><strong>UUID:</strong> {transaction.uuid}</p>
                        <p><strong>Descrição:</strong> {transaction.description}</p>
                        <p><strong>Valor:</strong> R$ {transaction.amount}</p>
                        <p><strong>Tipo:</strong> {transaction.transaction_type}</p>
                        <p><strong>Status Atual:</strong> 
                            <span class="badge bg-warning">{transaction.status}</span>
                        </p>
                        
                        <hr>
                        
                        <h5>🔄 Alterar Status:</h5>
                        <form method="post" action="/transactions/{transaction.uuid}/status/">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                            <div class="mb-3">
                                <select name="status" class="form-select" onchange="this.form.submit()">
                                    <option value="pending" {'selected' if transaction.status == 'pending' else ''}>Pendente</option>
                                    <option value="completed" {'selected' if transaction.status == 'completed' else ''}>Concluída</option>
                                    <option value="cancelled" {'selected' if transaction.status == 'cancelled' else ''}>Cancelada</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary">Alterar Status</button>
                        </form>
                        
                        <hr>
                        
                        <a href="/transactions/" class="btn btn-secondary">← Voltar para Lista</a>
                        <a href="/test/" class="btn btn-info ms-2">← Página de Teste</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)
        
    except Transaction.DoesNotExist:
        return HttpResponse("<h1>Transação não encontrada!</h1>")
    except Exception as e:
        return HttpResponse(f"<h1>Erro: {str(e)}</h1>")