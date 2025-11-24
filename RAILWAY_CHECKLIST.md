# ✅ CHECKLIST DE DEPLOY - RAILWAY

## 📋 **PRÉ-DEPLOY**

### **Código**
- [x] `Procfile` criado
- [x] `runtime.txt` criado  
- [x] `railway.json` criado
- [x] `nixpacks.toml` criado
- [x] `requirements.txt` atualizado
- [x] `.gitignore` configurado
- [x] `.env.example` atualizado
- [x] `settings.py` configurado para Railway
- [x] `README.md` atualizado

### **Arquivos de Build**
- [x] `railway_build.sh` - Script de build
- [x] `railway_setup.py` - Setup pós-deploy
- [x] `DEPLOY_RAILWAY.md` - Guia completo
- [x] `RAILWAY_README.md` - Quick start

---

## 🚀 **DURANTE O DEPLOY**

### **1. Criar Projeto no Railway**
- [ ] Conta Railway criada
- [ ] Novo projeto criado
- [ ] Repositório GitHub conectado

### **2. Adicionar Banco de Dados**
- [ ] PostgreSQL adicionado
- [ ] Variável `DATABASE_URL` verificada

### **3. Configurar Variáveis de Ambiente**
- [ ] `SECRET_KEY` configurada (gerar nova!)
- [ ] `DEBUG=False` configurada
- [ ] `ALLOWED_HOSTS` configurada
- [ ] `WEB_CONCURRENCY=4` configurada
- [ ] `PYTHONUNBUFFERED=1` configurada

**Gerar SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### **4. Iniciar Deploy**
- [ ] Push para branch `main`
- [ ] Build iniciado automaticamente
- [ ] Logs monitorados
- [ ] Deploy concluído com sucesso

---

## ✅ **PÓS-DEPLOY**

### **1. Verificações Básicas**
- [ ] Site está acessível
- [ ] Landing page carrega corretamente
- [ ] Arquivos estáticos funcionando (CSS/JS)
- [ ] Login/Logout funcionando

### **2. Setup Inicial**
```bash
# Via Railway CLI
railway run python railway_setup.py

# Ou criar manualmente
railway run python manage.py createsuperuser
```

- [ ] Superusuário criado
- [ ] Login admin funcionando
- [ ] Dashboard acessível

### **3. Testes Funcionais**
- [ ] Criar empresa
- [ ] Adicionar transações
- [ ] Gerar relatórios
- [ ] Exportar PDF/Excel
- [ ] Gerar DASN-SIMEI
- [ ] Testar alertas IA

### **4. Performance**
- [ ] Tempo de carregamento < 3s
- [ ] Imagens otimizadas
- [ ] Cache funcionando
- [ ] Logs sem erros

### **5. Segurança**
- [ ] HTTPS ativado
- [ ] DEBUG=False verificado
- [ ] SECRET_KEY única gerada
- [ ] ALLOWED_HOSTS correto
- [ ] Session cookies seguros

---

## 🔧 **COMANDOS ÚTEIS**

### **Railway CLI**
```bash
# Instalar
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs

# Executar comando
railway run python manage.py shell

# Ver variáveis
railway variables

# Configurar variável
railway variables set KEY=value
```

### **Django Management**
```bash
# Migrations
railway run python manage.py migrate

# Collectstatic
railway run python manage.py collectstatic --noinput

# Shell
railway run python manage.py shell

# DB Shell
railway run python manage.py dbshell

# Criar superuser
railway run python manage.py createsuperuser
```

---

## 🐛 **TROUBLESHOOTING**

### **Build Falhou**
```bash
# Ver logs detalhados
railway logs --deployment [deployment-id]

# Verificar requirements.txt
cat requirements.txt

# Testar build local
pip install -r requirements.txt
```

### **Application Crashed**
```bash
# Ver logs de runtime
railway logs

# Verificar variáveis
railway variables

# Reiniciar serviço
railway restart
```

### **Database Error**
```bash
# Verificar conexão
railway run python manage.py dbshell

# Rodar migrations
railway run python manage.py migrate

# Verificar DATABASE_URL
railway variables | grep DATABASE_URL
```

### **Static Files 404**
```bash
# Forçar collectstatic
railway run python manage.py collectstatic --noinput --clear

# Verificar STATIC_ROOT
railway run python manage.py shell -c "from django.conf import settings; print(settings.STATIC_ROOT)"
```

---

## 📊 **MONITORAMENTO**

### **Métricas a Acompanhar**
- [ ] Uptime (meta: 99.9%)
- [ ] Response time (meta: < 500ms)
- [ ] Error rate (meta: < 0.1%)
- [ ] Database performance
- [ ] Memory usage
- [ ] CPU usage

### **Ferramentas**
- Railway Dashboard
- Railway Logs
- PostgreSQL Insights
- Sentry (opcional)

---

## 💰 **CUSTOS**

### **Estimativa Mensal**
- Web Service: $3-5
- PostgreSQL: $2-3
- Bandwidth: $0-1
- **Total: ~$5-8/mês**

### **Otimizações**
- Usar Hobby plan ($5/mês)
- Configurar auto-scaling
- Monitorar uso de recursos
- Limpar logs antigos

---

## 🎯 **PRÓXIMOS PASSOS**

Após deploy bem-sucedido:

1. [ ] Configurar domínio customizado
2. [ ] Configurar email (SMTP)
3. [ ] Configurar backups automáticos
4. [ ] Configurar monitoramento (Sentry)
5. [ ] Documentar URLs principais
6. [ ] Treinar usuários
7. [ ] Planejar marketing

---

## 📞 **CREDENCIAIS PADRÃO**

**⚠️ Após primeiro acesso via `railway_setup.py`:**

```
Email: admin@cashflow.com
Senha: Change.This.Password.123!
```

**🔴 ALTERAR IMEDIATAMENTE APÓS LOGIN!**

---

## ✅ **DEPLOY CONCLUÍDO!**

Se todos os itens acima estão marcados, seu deploy está completo!

**URL do projeto:** https://[seu-projeto].railway.app
**Status:** ✅ PRODUÇÃO

**🎉 Parabéns! Seu CashFlow Manager está no ar!**
