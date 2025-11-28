#!/usr/bin/env bash
# Script de inicialização Railway

echo "🚀 Running migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Initialization complete!"
