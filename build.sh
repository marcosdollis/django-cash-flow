#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Iniciando build do Django Cash Flow..."

# Install dependencies
echo "📦 Instalando dependências..."
pip install -r requirements.txt || pip install -r requirements_production.txt

# Collect static files
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗄️ Executando migrações do banco..."
python manage.py migrate

# Create superuser if it doesn't exist (optional)
echo "👤 Configurando superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cashflow.com', 'CashFlow@2025')
    print('✅ Superuser criado: admin / CashFlow@2025')
else:
    print('✅ Superuser já existe')
"

# Initialize production data
echo "🔧 Inicializando dados de produção..."
python init_production_data.py

echo "✅ Build completed successfully!"
echo "🎉 Django Cash Flow está pronto para uso!"