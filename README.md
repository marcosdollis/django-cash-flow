# 💰 CashFlow Manager

Sistema completo de gestão financeira para MEIs com Inteligência Artificial.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/django-cashflow)

## 🚀 **Recursos Principais**

- 🧠 **IA Financeira** - Score de saúde, detecção de anomalias, alertas inteligentes
- 📊 **Relatórios Profissionais** - PDF, Excel, dashboards em tempo real
- 📋 **DASN-SIMEI Automático** - Único sistema com geração automática do relatório MEI
- 🏢 **Multi-Empresa** - Gerencie múltiplos negócios
- 🔒 **Segurança Avançada** - Autenticação robusta e dados criptografados
- 📱 **100% Responsivo** - Funciona perfeitamente em mobile

## 🎯 **Deploy Rápido**

### **Railway (Recomendado)**
1. Clique no botão "Deploy on Railway" acima
2. Configure as variáveis de ambiente
3. Aguarde ~3 minutos
4. Pronto! 🎉

Veja o guia completo: [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)

### **Render.com**
Veja: [render.yaml](render.yaml)

## 🛠️ **Desenvolvimento Local**

### **Pré-requisitos**
- Python 3.13+
- pip
- Git

### **Instalação**

```bash
# Clonar repositório
git clone https://github.com/marcosdollis/django-cash-flow.git
cd django-cash-flow

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Copiar configurações
copy .env.example .env  # Windows
# ou
cp .env.example .env  # Linux/Mac

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

Acesse: http://localhost:8000

## 📊 **Tecnologias**

- **Backend:** Django 5.0.7
- **Database:** PostgreSQL (produção) / SQLite (dev)
- **Frontend:** Bootstrap 5, Chart.js
- **Deployment:** Railway / Render
- **Server:** Gunicorn + WhiteNoise

## 🔐 **Variáveis de Ambiente**

```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=*.railway.app,localhost
```

## 📝 **Licença**

MIT License

## 👨‍💻 **Autor**

Marcos Dollis - [@marcosdollis](https://github.com/marcosdollis)

---

**⭐ Se este projeto te ajudou, deixe uma estrela!**