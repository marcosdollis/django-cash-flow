# 🚂 Railway - Comandos Úteis

## 📦 **INSTALAÇÃO DA CLI**

```bash
# Via NPM
npm i -g @railway/cli

# Via Homebrew (Mac)
brew install railway

# Verificar instalação
railway --version
```

---

## 🔐 **AUTENTICAÇÃO**

```bash
# Login
railway login

# Logout
railway logout

# Verificar usuário atual
railway whoami
```

---

## 🚀 **GERENCIAMENTO DE PROJETOS**

```bash
# Listar projetos
railway list

# Selecionar projeto
railway link

# Informações do projeto
railway status

# Abrir dashboard no browser
railway open
```

---

## 📊 **LOGS E MONITORAMENTO**

```bash
# Ver logs em tempo real
railway logs

# Logs de um deployment específico
railway logs --deployment <deployment-id>

# Filtrar logs por serviço
railway logs --service web

# Salvar logs em arquivo
railway logs > logs.txt
```

---

## 🔧 **VARIÁVEIS DE AMBIENTE**

```bash
# Listar todas as variáveis
railway variables

# Definir variável
railway variables set KEY=value

# Definir múltiplas variáveis
railway variables set KEY1=value1 KEY2=value2

# Deletar variável
railway variables delete KEY

# Exportar variáveis localmente
railway variables > .env.railway
```

**Exemplos práticos:**
```bash
# Configurar Django
railway variables set DEBUG=False
railway variables set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
railway variables set ALLOWED_HOSTS="*.railway.app"
railway variables set WEB_CONCURRENCY=4
```

---

## 🗄️ **BANCO DE DADOS**

```bash
# Conectar ao PostgreSQL
railway connect postgres

# Executar query SQL
railway run psql -c "SELECT * FROM auth_user LIMIT 5;"

# Backup do banco
railway run pg_dump > backup.sql

# Restaurar backup
railway run psql < backup.sql

# Ver informações do database
railway run psql -c "\l"
```

---

## 🐍 **COMANDOS DJANGO**

```bash
# Migrations
railway run python manage.py migrate

# Criar superusuário
railway run python manage.py createsuperuser

# Collectstatic
railway run python manage.py collectstatic --noinput

# Shell Django
railway run python manage.py shell

# Executar script Python
railway run python manage.py runscript meu_script

# Limpar sessões expiradas
railway run python manage.py clearsessions

# Verificar sistema
railway run python manage.py check
```

---

## 🔄 **DEPLOY E BUILD**

```bash
# Deploy manual (forçar rebuild)
railway up

# Deploy de branch específica
railway up --branch staging

# Redeploy (sem rebuild)
railway restart

# Cancelar deploy em andamento
railway cancel

# Ver histórico de deploys
railway deployments

# Rollback para deploy anterior
railway rollback <deployment-id>
```

---

## 📁 **TRANSFERÊNCIA DE ARQUIVOS**

```bash
# Upload de arquivo
railway run --upload <arquivo> python manage.py shell

# Download de logs
railway logs > logs.txt

# Backup de arquivos estáticos
railway run tar -czf static.tar.gz staticfiles/
```

---

## 🔍 **DEBUG E TROUBLESHOOTING**

```bash
# Ver configuração do build
railway run env

# Testar conectividade
railway run ping -c 3 google.com

# Ver uso de recursos
railway metrics

# Shell interativo no container
railway shell

# Executar comando customizado
railway run <seu-comando>
```

**Exemplos de debug:**
```bash
# Verificar Python version
railway run python --version

# Verificar pip packages
railway run pip list

# Verificar Django settings
railway run python -c "from django.conf import settings; print(settings.DEBUG)"

# Ver variáveis de ambiente
railway run printenv

# Testar import
railway run python -c "import django; print(django.VERSION)"
```

---

## 📊 **MONITORING E ANALYTICS**

```bash
# Métricas do serviço
railway metrics

# Status de saúde
railway status

# Ver uso de créditos
railway usage

# Histórico de builds
railway deployments --limit 10
```

---

## 🎯 **WORKFLOWS COMUNS**

### **Deploy Completo**
```bash
# 1. Commit mudanças
git add .
git commit -m "Update feature"
git push origin main

# 2. Verificar deploy
railway logs --follow

# 3. Testar
railway open
```

### **Hotfix Rápido**
```bash
# 1. Fazer mudança
# 2. Deploy forçado
railway up --detach

# 3. Ver logs
railway logs
```

### **Rollback de Emergência**
```bash
# 1. Ver deploys
railway deployments

# 2. Rollback
railway rollback <deployment-id>

# 3. Confirmar
railway status
```

### **Database Backup**
```bash
# 1. Conectar
railway connect postgres

# 2. Dump
pg_dump > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Comprimir
gzip backup_*.sql
```

### **Executar Migration**
```bash
# 1. Criar migration local
python manage.py makemigrations

# 2. Commit
git add . && git commit -m "Add migration"

# 3. Push (deploy automático)
git push

# 4. Verificar logs
railway logs --follow
```

---

## 🔒 **SEGURANÇA**

```bash
# Gerar nova SECRET_KEY
railway variables set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Forçar HTTPS
railway variables set SECURE_SSL_REDIRECT=True

# Configurar sessões seguras
railway variables set SESSION_COOKIE_SECURE=True
railway variables set CSRF_COOKIE_SECURE=True
```

---

## 📝 **SCRIPTS ÚTEIS**

### **Setup Completo (setup.sh)**
```bash
#!/bin/bash
echo "🚂 Railway Setup..."

# Login
railway login

# Link projeto
railway link

# Configurar variáveis
railway variables set DEBUG=False
railway variables set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
railway variables set ALLOWED_HOSTS="*.railway.app"
railway variables set WEB_CONCURRENCY=4

# Deploy
railway up

echo "✅ Setup concluído!"
```

### **Deploy com Verificação (deploy.sh)**
```bash
#!/bin/bash
echo "🚀 Starting deploy..."

# Commit
git add .
git commit -m "${1:-Update}"
git push

# Aguardar build
echo "⏳ Waiting for build..."
sleep 60

# Ver logs
railway logs --limit 50

echo "✅ Deploy concluído!"
```

### **Backup Diário (backup.sh)**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
railway run pg_dump > backup_$DATE.sql
gzip backup_$DATE.sql
echo "✅ Backup criado: backup_$DATE.sql.gz"
```

---

## 🎓 **BOAS PRÁTICAS**

1. **Use `.railwayignore`** para excluir arquivos do deploy
2. **Sempre teste localmente** antes de fazer deploy
3. **Configure variáveis sensíveis** via CLI, não no código
4. **Monitore logs** após cada deploy
5. **Faça backups regulares** do banco de dados
6. **Use branches** para staging/production
7. **Documente mudanças** nos commits

---

## 📚 **RECURSOS**

- **Docs:** https://docs.railway.app
- **Discord:** https://discord.gg/railway
- **Status:** https://status.railway.app
- **CLI Docs:** https://docs.railway.app/develop/cli

---

## 🆘 **AJUDA RÁPIDA**

```bash
# Ver ajuda geral
railway --help

# Ajuda de comando específico
railway logs --help

# Ver versão
railway --version

# Atualizar CLI
npm update -g @railway/cli
```

---

**💡 Dica:** Adicione `alias rw='railway'` no seu `.bashrc` ou `.zshrc` para comandos mais rápidos!

```bash
# Ao invés de
railway logs

# Use
rw logs
```

🚂 **Happy deploying!**
