# PUSH NOTIFICATIONS - Configuração e Uso

## 📱 Sistema Completo de Notificações Push Implementado!

### ✅ O que foi implementado:

1. **Modelos de Banco de Dados** (`core/models.py`)
   - `PushSubscription`: Armazena subscrições de dispositivos
   - `PushNotificationLog`: Registra histórico de notificações enviadas

2. **API Endpoints** (`api/views.py` e `api/urls.py`)
   - `POST /api/push/subscribe/`: Registra nova subscrição
   - `POST /api/push/unsubscribe/`: Remove subscrição
   - `POST /api/push/test/`: Envia notificação de teste
   - Função `send_push_notification()`: Helper para enviar notificações

3. **Service Worker** (`static/sw.js`)
   - Handler de eventos `push` para receber notificações
   - Handler de `notificationclick` para navegação
   - Handler de `notificationclose` para tracking
   - Suporte a background sync

4. **JavaScript Client** (`static/js/push-notifications.js`)
   - Classe `PushNotificationManager` completa
   - Gerenciamento de permissões
   - Subscribe/unsubscribe automático
   - Conversão de VAPID keys
   - Detecção de dispositivo
   - Sistema de toasts para feedback

5. **Integração com Alertas** (`core/alert_generator.py`)
   - Alertas críticos enviam notificações push automaticamente
   - Ícones personalizados por tipo de alerta

6. **Configurações** (`settings.py`)
   - VAPID keys via variáveis de ambiente
   - Context processor para disponibilizar chave pública nos templates

---

## 🚀 Como Usar:

### 1. Gerar Chaves VAPID

```bash
python generate_vapid_keys.py
```

Isso gerará:
- `private_key.pem`
- `public_key.pem`
- Exibirá as variáveis de ambiente necessárias

### 2. Configurar Variáveis de Ambiente

Adicione ao seu `.env`:
```bash
VAPID_PRIVATE_KEY=sua_chave_privada_aqui
VAPID_PUBLIC_KEY=sua_chave_publica_aqui
VAPID_ADMIN_EMAIL=admin@seudominio.com
```

No Railway, adicione as mesmas variáveis nas configurações do projeto.

### 3. Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Testar Localmente

```bash
# Iniciar servidor
python manage.py runserver

# Em outro terminal, testar com HTTPS (necessário para push)
# Ou use ngrok: ngrok http 8000
```

### 5. Ativar Notificações no Frontend

No navegador (após login), abra o console e execute:

```javascript
// Solicitar permissão e criar subscrição
await pushManager.subscribe();

// Enviar notificação de teste
await pushManager.sendTestNotification();

// Verificar status
console.log('Inscrito?', pushManager.isSubscribed);

// Cancelar subscrição
await pushManager.unsubscribe();
```

---

## 🎯 Uso Programático

### Enviar Notificação para um Usuário

```python
from api.views import send_push_notification

# Enviar notificação
results = send_push_notification(
    user=user,
    title='Título da Notificação',
    body='Mensagem da notificação',
    url='/core/dashboard/',  # URL opcional
    icon='/static/icons/icon-192x192.png'
)

print(f"Enviadas: {results['sent']}")
print(f"Falhadas: {results['failed']}")
```

### Integração com Alertas Automáticos

As notificações já estão integradas com o sistema de alertas.
Alertas de severidade `critical` ou `high` enviam push automaticamente:

```python
from core.alert_generator import generate_dynamic_alerts

# Gera alertas e envia notificações push
alerts = generate_dynamic_alerts(company=company, user=user)
```

---

## 📱 Suporte por Plataforma

### ✅ Android (Chrome, Edge, Firefox)
- ✅ Notificações push funcionam perfeitamente
- ✅ PWA instalado ou no navegador
- ✅ Ícones, badges, ações customizadas

### ⚠️ iOS/Safari (iPhone/iPad)
- ⚠️ Requer iOS 16.4+ (março 2023)
- ⚠️ **Apenas funciona com PWA instalado** na tela inicial
- ❌ NÃO funciona no Safari browser normal
- ✅ Após instalado, funciona como Android

### ✅ Desktop (Windows/Mac/Linux)
- ✅ Chrome, Edge, Firefox
- ✅ Notificações nativas do sistema operacional

---

## 🔧 Adicionar Botão de Ativar Notificações

Adicione ao seu template (ex: dashboard):

```html
{% if user.is_authenticated %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title">🔔 Notificações Push</h5>
        <p class="card-text">Receba alertas importantes diretamente no seu dispositivo</p>
        <button id="btnEnableNotifications" class="btn btn-primary" onclick="enableNotifications()">
            Ativar Notificações
        </button>
        <button id="btnTestNotification" class="btn btn-secondary d-none" onclick="testNotification()">
            Testar Notificação
        </button>
    </div>
</div>

<script>
async function enableNotifications() {
    const btn = document.getElementById('btnEnableNotifications');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Ativando...';
    
    const success = await pushManager.subscribe();
    
    if (success) {
        btn.classList.add('d-none');
        document.getElementById('btnTestNotification').classList.remove('d-none');
    } else {
        btn.disabled = false;
        btn.innerHTML = 'Ativar Notificações';
    }
}

async function testNotification() {
    await pushManager.sendTestNotification();
}

// Atualizar UI se já estiver inscrito
if (pushManager.isSubscribed) {
    document.getElementById('btnEnableNotifications').classList.add('d-none');
    document.getElementById('btnTestNotification').classList.remove('d-none');
}
</script>
{% endif %}
```

---

## 📊 Admin - Visualizar Subscrições

Adicione ao `core/admin.py`:

```python
from django.contrib import admin
from .models import PushSubscription, PushNotificationLog

@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'device_name']
    readonly_fields = ['endpoint', 'p256dh', 'auth', 'created_at', 'updated_at']

@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    list_display = ['title', 'subscription', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'body']
    readonly_fields = ['created_at', 'sent_at']
```

---

## 🔐 Segurança

- ✅ Chaves VAPID mantidas em variáveis de ambiente
- ✅ Endpoints protegidos com `@login_required`
- ✅ CSRF exemption apenas onde necessário
- ✅ Validação de dados de entrada
- ✅ Subscrições expiradas são removidas automaticamente (HTTP 410)

---

## 🎨 Personalização

### Customizar Ícone/Badge da Notificação

No `send_push_notification()`:

```python
send_push_notification(
    user=user,
    title='💰 Novo Depósito',
    body=f'Você recebeu R$ {amount}',
    icon='/static/icons/money-icon.png',
)
```

### Adicionar Ações à Notificação

No `static/sw.js`, modifique o evento `push`:

```javascript
notificationData = {
    ...notificationData,
    actions: [
        {action: 'view', title: 'Ver Detalhes'},
        {action: 'dismiss', title: 'Dispensar'}
    ]
};
```

---

## 📝 Checklist de Deploy

- [ ] Gerar chaves VAPID
- [ ] Adicionar variáveis de ambiente no Railway
- [ ] Executar migrações
- [ ] Testar em HTTPS (Railway fornece automaticamente)
- [ ] Testar em dispositivo Android
- [ ] Testar instalação PWA no iOS (se disponível)
- [ ] Adicionar `*.pem` ao `.gitignore`
- [ ] Documentar para usuários finais

---

## 🐛 Troubleshooting

### "VAPID key not found"
- Verifique se as variáveis `VAPID_PRIVATE_KEY` e `VAPID_PUBLIC_KEY` estão configuradas

### "Push not supported"
- Verifique se está usando HTTPS (obrigatório)
- Verifique se o navegador suporta push (iOS requer instalação PWA)

### Notificações não aparecem
- Verifique permissões do navegador
- Confira console do navegador e do service worker
- Verifique logs do servidor Django

### Subscrição falha no iOS
- Certifique-se que o PWA foi instalado na tela inicial
- iOS < 16.4 não suporta push

---

## 📚 Referências

- [Web Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [VAPID Protocol](https://datatracker.ietf.org/doc/html/rfc8292)
- [PyWebPush](https://github.com/web-push-libs/pywebpush)
- [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
