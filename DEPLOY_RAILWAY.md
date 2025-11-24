# 🚂 DEPLOY NO RAILWAY - GUIA COMPLETO

## 📋 **PRÉ-REQUISITOS**
- Conta no Railway.app (https://railway.app)
- Repositório GitHub com o código
- Conhecimentos básicos de Git

---

## 🚀 **PASSO A PASSO PARA DEPLOY**

### **1️⃣ CRIAR CONTA NO RAILWAY**
1. Acesse https://railway.app
2. Clique em "Start a New Project"
3. Faça login com GitHub

### **2️⃣ CRIAR NOVO PROJETO**
1. No dashboard do Railway, clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha o repositório `django-cash-flow`
4. O Railway detectará automaticamente que é um projeto Python/Django

### **3️⃣ CONFIGURAR BANCO DE DADOS POSTGRESQL**
1. No projeto Railway, clique em "New" → "Database" → "Add PostgreSQL"
2. O Railway criará automaticamente o banco e a variável `DATABASE_URL`
3. Aguarde o provisionamento (leva ~30 segundos)

### **4️⃣ CONFIGURAR VARIÁVEIS DE AMBIENTE**

No Railway, vá em **Settings → Variables** e adicione:

```bash
# Obrigatórias
SECRET_KEY=sua-chave-secreta-super-segura-aqui-min-50-chars
DATABASE_URL=postgresql://... (gerado automaticamente pelo Railway)
DEBUG=False
ALLOWED_HOSTS=*.railway.app,seu-dominio.com

# Opcionais
WEB_CONCURRENCY=4
DJANGO_SETTINGS_MODULE=cashflow_manager.settings
PYTHONUNBUFFERED=1
```

**⚠️ IMPORTANTE:** Gere uma SECRET_KEY segura com:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### **5️⃣ CONFIGURAR DOMÍNIO (OPCIONAL)**
1. Vá em **Settings → Domains**
2. Railway gera um domínio automático: `*.railway.app`
3. Para domínio customizado, clique em "Custom Domain" e siga instruções

### **6️⃣ DEPLOY AUTOMÁTICO**
O Railway detecta automaticamente os arquivos:
- ✅ `Procfile` - Define comando de start
- ✅ `requirements.txt` - Dependências Python
- ✅ `runtime.txt` - Versão do Python
- ✅ `railway.json` - Configurações específicas Railway
- ✅ `nixpacks.toml` - Build configuration

O deploy iniciará automaticamente após push para `main`!

---

## 🔧 **ARQUIVOS DE CONFIGURAÇÃO CRIADOS**

### **Procfile**
```
web: gunicorn cashflow_manager.wsgi --log-file -
```

### **runtime.txt**
```
python-3.13.0
```

### **railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput"
  },
  "deploy": {
    "startCommand": "gunicorn cashflow_manager.wsgi:application --bind 0.0.0.0:$PORT --workers 4",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **nixpacks.toml**
```toml
[phases.setup]
nixPkgs = ["python313", "postgresql"]

[phases.install]
cmds = [
  "pip install --upgrade pip",
  "pip install -r requirements.txt"
]

[phases.build]
cmds = [
  "python manage.py collectstatic --noinput",
  "python manage.py migrate --noinput"
]

[start]
cmd = "gunicorn cashflow_manager.wsgi:application --bind 0.0.0.0:$PORT --workers 4"
```

---

## 📊 **MONITORAMENTO**

### **Logs em Tempo Real**
1. No Railway, clique no serviço web
2. Vá para a aba "Deployments"
3. Clique no deployment ativo para ver logs

### **Comandos Úteis via Railway CLI**
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs

# Executar comandos Django
railway run python manage.py createsuperuser
railway run python manage.py shell
```

---

## 🔍 **VERIFICAÇÃO PÓS-DEPLOY**

### **1. Verificar Status**
- Acesse o domínio Railway gerado
- Deve exibir a landing page do projeto

### **2. Criar Superusuário**
```bash
railway run python manage.py createsuperuser
```

### **3. Testar Funcionalidades**
- Login/Logout
- Dashboard
- Transações
- Relatórios
- DASN-SIMEI

---

## 🐛 **TROUBLESHOOTING**

### **Erro: "Application failed to start"**
```bash
# Verificar logs
railway logs

# Verificar variáveis de ambiente
railway variables
```

### **Erro: "Static files not found"**
```bash
# Forçar collectstatic
railway run python manage.py collectstatic --noinput
```

### **Erro: "Database connection failed"**
```bash
# Verificar se DATABASE_URL está configurada
railway variables | grep DATABASE_URL

# Testar conexão
railway run python manage.py dbshell
```

### **Erro: "ALLOWED_HOSTS validation error"**
```bash
# Adicionar domínio Railway em ALLOWED_HOSTS
railway variables set ALLOWED_HOSTS="*.railway.app,localhost"
```

---

## 💰 **CUSTOS RAILWAY**

### **Plano Gratuito (Trial)**
- $5 de crédito grátis/mês
- Suficiente para projetos pequenos
- Aplicação hiberna após inatividade

### **Plano Hobby ($5/mês)**
- $5 de créditos inclusos
- Sem hibernação
- Ideal para produção

### **Estimativa para este projeto:**
- Web Service: ~$3-5/mês
- PostgreSQL: ~$2-3/mês
- **Total: ~$5-8/mês**

---

## 🔄 **CI/CD AUTOMÁTICO**

O Railway faz deploy automático quando você fizer push para GitHub:

```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

O Railway detecta o push e:
1. ✅ Faz build do projeto
2. ✅ Roda collectstatic
3. ✅ Executa migrações
4. ✅ Inicia gunicorn
5. ✅ Atualiza domínio

---

## 🎯 **PRÓXIMOS PASSOS**

1. ✅ Fazer push do código para GitHub
2. ✅ Criar projeto no Railway
3. ✅ Adicionar PostgreSQL
4. ✅ Configurar variáveis de ambiente
5. ✅ Aguardar deploy automático
6. ✅ Criar superusuário
7. ✅ Testar aplicação
8. ✅ Configurar domínio customizado (opcional)

---

## 📞 **SUPORTE**

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Railway Status:** https://status.railway.app

---

## 🎉 **PRONTO!**

Seu projeto Django Cash Flow está configurado para deploy no Railway!

**Link do projeto:** Será gerado após primeiro deploy
**Custo estimado:** $5-8/mês
**Tempo de deploy:** 3-5 minutos

Boa sorte com o deploy! 🚀
