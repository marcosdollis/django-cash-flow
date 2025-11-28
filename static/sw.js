// Service Worker para PWA
const CACHE_NAME = 'cashflow-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/accounts/login/',
  '/core/dashboard/',
];

// Instalação do Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Intercepta requisições
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - retorna resposta do cache
        if (response) {
          return response;
        }
        
        // Clone da requisição
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest).then(response => {
          // Verifica se resposta é válida
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone da resposta
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
  );
});

// ==================== PUSH NOTIFICATIONS ====================

// Evento quando uma notificação push é recebida
self.addEventListener('push', event => {
  console.log('Push recebido:', event);
  
  let notificationData = {
    title: 'CashFlow Manager',
    body: 'Nova notificação',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    tag: 'cashflow-notification',
    requireInteraction: false,
  };
  
  // Se a push tem dados, usa eles
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        ...notificationData,
        title: data.title || notificationData.title,
        body: data.body || notificationData.body,
        icon: data.icon || notificationData.icon,
        badge: data.badge || notificationData.badge,
        data: {
          url: data.url || '/',
          timestamp: Date.now(),
        }
      };
    } catch (e) {
      console.error('Erro ao parsear dados da push:', e);
    }
  }
  
  // Mostra a notificação
  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Evento quando usuário clica na notificação
self.addEventListener('notificationclick', event => {
  console.log('Notificação clicada:', event);
  
  event.notification.close();
  
  // URL para abrir (padrão: dashboard)
  const urlToOpen = event.notification.data?.url || '/core/dashboard/';
  
  // Verifica se já existe uma janela aberta com o app
  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then(clientList => {
      // Se encontrar uma janela aberta, foca nela
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i];
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus().then(client => {
            // Navega para a URL da notificação
            if (client.navigate && urlToOpen) {
              return client.navigate(urlToOpen);
            }
          });
        }
      }
      
      // Se não encontrar janela aberta, abre uma nova
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Evento quando notificação é fechada sem clique
self.addEventListener('notificationclose', event => {
  console.log('Notificação fechada:', event);
  
  // Aqui você pode rastrear notificações ignoradas se necessário
  // analytics.trackEvent('notification_closed', { ... });
});

// Background Sync (opcional - para sincronizar dados offline)
self.addEventListener('sync', event => {
  console.log('Background sync:', event);
  
  if (event.tag === 'sync-transactions') {
    event.waitUntil(
      // Sincronizar transações pendentes quando voltar online
      syncPendingTransactions()
    );
  }
});

// Função helper para sincronizar transações pendentes
async function syncPendingTransactions() {
  try {
    // Buscar transações pendentes do IndexedDB ou cache
    // Enviar para o servidor
    console.log('Sincronizando transações pendentes...');
    
    // Implementar lógica de sincronização aqui
    return Promise.resolve();
  } catch (error) {
    console.error('Erro ao sincronizar:', error);
    return Promise.reject(error);
  }
}

