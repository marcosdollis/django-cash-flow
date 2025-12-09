# Configuração de Notificações Push Agendadas
# CashFlow Manager

Este documento explica como configurar as notificações push automáticas diárias.

## Notificações Configuradas

### 1. 8:00 - Lembrete para Registrar
- **Título**: 📝 Hora de Registrar!
- **Mensagem**: Bom dia! Que tal começar o dia registrando suas transações? Mantenha seu controle financeiro sempre atualizado.
- **Link**: /transactions/create/

### 2. 18:00 - Importância da Gestão
- **Título**: 💡 Gestão Financeira é Fundamental
- **Mensagem**: Boa noite! Lembre-se: uma boa gestão financeira é a base para alcançar seus objetivos. Continue acompanhando seus gastos e receitas!
- **Link**: /core/dashboard/

## Configuração do Cron Job

### No Linux/Ubuntu:
```bash
# Editar crontab
crontab -e

# Adicionar estas linhas:
# Notificações às 8:00 todos os dias
0 8 * * * cd /caminho/para/seu/projeto && /caminho/para/venv/bin/python manage.py send_scheduled_notifications

# Notificações às 18:00 todos os dias
0 18 * * * cd /caminho/para/seu/projeto && /caminho/para/venv/bin/python manage.py send_scheduled_notifications
```

### No Windows (Task Scheduler):
1. Abrir **Task Scheduler**
2. Criar nova tarefa básica
3. Configurar:
   - **Nome**: CashFlow - Notificações 8h
   - **Trigger**: Daily às 8:00
   - **Action**: Start a program
   - **Program**: `C:\Users\[seu_usuario]\Documents\python projects\django-cash-flow\venv\Scripts\python.exe`
   - **Arguments**: `manage.py send_scheduled_notifications`
   - **Start in**: `C:\Users\[seu_usuario]\Documents\python projects\django-cash-flow`

4. Repetir para as 18:00

### No Railway (Deploy):
Adicionar ao `Procfile` ou configurar cron job no painel do Railway.

### No Render:
Configurar cron job no painel do Render ou usar serviço externo como cron-job.org.

## Verificação

Para testar manualmente:
```bash
cd /caminho/para/seu/projeto
python manage.py send_scheduled_notifications
```

## Personalização

Para modificar as notificações, acesse o admin do Django:
/admin/core/schedulednotification/

## Logs

As notificações enviadas são registradas em:
/admin/core/pushnotificationlog/