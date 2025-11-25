#!/usr/bin/env bash
# Railway.app build script

echo "🚀 Starting Railway deployment..."

# Atualizar pip
echo "📦 Updating pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Executar migrações
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"
