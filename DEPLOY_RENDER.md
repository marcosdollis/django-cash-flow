# 🚀 Deploy Django Cash Flow no Render

Este guia te ensina como fazer o deploy completo da aplicação Django Cash Flow no Render.com com PostgreSQL.

## 📋 Pré-requisitos

- Conta no [Render.com](https://render.com) (gratuita)
- Repositório no GitHub com o código
- Git configurado localmente

## 🎯 Passo a Passo Completo

### **1. Preparar o Repositório**

```bash
# Clone ou navegue até o projeto
cd django-cash-flow

# Adicione todos os arquivos ao Git
git add .
git commit -m "Configuração para deploy no Render"
git push origin main
```

### **2. Configurar no Render.com**

#### **2.1. Criar Banco PostgreSQL**

1. Acesse [render.com](https://render.com) e faça login
2. Clique em **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `django-cash-flow-db`
   - **Database**: `cashflow_db`
   - **User**: `cashflow_user`
   - **Region**: `Ohio` (mais barato)
   - **Plan**: `Free` (até 1GB, suficiente para começar)
4. Clique em **"Create Database"**
5. **Aguarde** a criação (2-3 minutos)
6. **Anote a URL de conexão** que aparecerá

#### **2.2. Criar Web Service**

1. Clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub
3. Configure:
   - **Name**: `django-cash-flow`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn cashflow_manager.wsgi:application`
   - **Plan**: `Free` (para começar)

#### **2.3. Configurar Variáveis de Ambiente**

Na seção **Environment Variables**, adicione:

```env
DATABASE_URL
# Clique em "Add from Database" e selecione django-cash-flow-db

SECRET_KEY
# Clique em "Generate" para criar uma chave segura

PYTHON_VERSION
# Valor: 3.11.9

WEB_CONCURRENCY  
# Valor: 4
```

#### **2.4. Deploy Automático**

1. Clique em **"Create Web Service"**
2. O Render vai:
   - Clonar seu repositório
   - Instalar dependências (`pip install -r requirements.txt`)
   - Executar migrações (`python manage.py migrate`)
   - Coletar arquivos estáticos (`collectstatic`)
   - Criar superuser (`admin / CashFlow@2025`)
   - Inicializar dados básicos
   - Iniciar o servidor

### **3. Primeiro Acesso**

Após o deploy (5-10 minutos):

1. **URL da aplicação**: `https://django-cash-flow.onrender.com`
2. **Admin**: `https://django-cash-flow.onrender.com/admin`
   - **Usuário**: `admin`
   - **Senha**: `CashFlow@2025`

### **4. Configuração Inicial**

1. **Acesse o admin** e altere a senha padrão
2. **Teste a landing page**: `https://seu-app.onrender.com/landing/`
3. **Crie conta de usuário** através da landing page
4. **Teste todas as funcionalidades**

## 🔧 Arquivos de Configuração

### **render.yaml** (Deploy automático)
```yaml
databases:
  - name: django-cash-flow-db
    databaseName: cashflow_db
    user: cashflow_user
    
services:
  - type: web
    name: django-cash-flow
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn cashflow_manager.wsgi:application"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: django-cash-flow-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
```

### **build.sh** (Script de build)
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# Criar superuser e dados iniciais
python init_production_data.py
```

## 🗄️ Banco de Dados

### **PostgreSQL vs SQLite**

- **Desenvolvimento**: SQLite (automático)
- **Produção**: PostgreSQL (Render)
- **Migração**: Automática via `DATABASE_URL`

### **Estrutura do Banco**
```sql
-- Principais tabelas criadas automaticamente:
- auth_user (usuários)
- accounts_company (empresas)  
- transactions_transaction (transações)
- transactions_category (categorias)
- transactions_goal (metas)
- reports_alert (alertas)
```

### **Dados Iniciais**
O script `init_production_data.py` cria:
- ✅ Categorias padrão para MEI
- ✅ Empresa demo
- ✅ Associação com superuser

## 🔒 Segurança em Produção

### **Configurações Aplicadas**
- ✅ `DEBUG = False`
- ✅ HTTPS redirect automático
- ✅ Headers de segurança
- ✅ Cookies seguros
- ✅ WhiteNoise para arquivos estáticos
- ✅ SECRET_KEY gerada automaticamente

### **Monitoramento**
- **Logs**: Disponíveis no painel do Render
- **Métricas**: CPU, Memória, Requests
- **Alertas**: Configuráveis por email

## 🚨 Troubleshooting

### **Erro de Build**
```bash
# Verificar logs no Render dashboard
# Problemas comuns:
- requirements.txt incompleto
- Erro nas migrações
- Permissões do build.sh
```

### **Erro de Banco**
```bash
# Verificar se DATABASE_URL está configurada
# Recriar banco se necessário
# Executar migrações manualmente
```

### **Erro de Static Files**
```bash
# Verificar STATIC_ROOT
# Executar collectstatic
# Verificar WhiteNoise configuração
```

## 🎉 Funcionalidades Disponíveis

### **Para MEI**
- ✅ Dashboard com filtros futuros (próximos 30/60 dias)
- ✅ Controle de faturamento R$ 81mil
- ✅ Relatórios DASN-SIMEI
- ✅ Multi-CNPJ
- ✅ Alertas inteligentes
- ✅ Landing page otimizada

### **Tecnologias**
- ✅ Django 5.0.7
- ✅ PostgreSQL 15
- ✅ Bootstrap 5
- ✅ Chart.js
- ✅ WhiteNoise
- ✅ Gunicorn

## 💰 Custos Estimados

### **Render Free Tier**
- **Web Service**: Gratuito (750h/mês)
- **PostgreSQL**: Gratuito (1GB)
- **Total**: **R$ 0/mês** para começar

### **Render Paid**
- **Web Service**: $7/mês (Starter)
- **PostgreSQL**: $7/mês (Starter - 1GB)
- **Total**: **~R$ 70/mês** (produção)

## 🔄 Atualizações Futuras

```bash
# Para atualizar a aplicação:
git add .
git commit -m "Nova funcionalidade"
git push origin main

# Render fará deploy automático!
```

## 📞 Suporte

- **Documentação Render**: [render.com/docs](https://render.com/docs)
- **Logs**: Painel do Render → Service → Logs
- **Django Debug**: Ative temporariamente `DEBUG=True` se necessário

---

✅ **Aplicação pronta para produção!**  
🚀 **Acesse**: `https://seu-app.onrender.com`  
🛡️ **Admin**: `https://seu-app.onrender.com/admin`