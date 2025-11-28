/**
 * Sistema de Push Notifications para CashFlow Manager
 * Gerencia permissões, subscrições e envio de notificações
 */

class PushNotificationManager {
    constructor() {
        this.swRegistration = null;
        this.isSubscribed = false;
        this.applicationServerKey = null; // Será definido via VAPID public key
    }

    /**
     * Inicializa o sistema de notificações
     */
    async init() {
        // Verifica suporte do navegador
        if (!('serviceWorker' in navigator)) {
            console.warn('Service Workers não suportados neste navegador');
            return false;
        }

        if (!('PushManager' in window)) {
            console.warn('Push notifications não suportadas neste navegador');
            return false;
        }

        try {
            // Aguarda registro do service worker
            this.swRegistration = await navigator.serviceWorker.ready;
            console.log('Service Worker pronto para push notifications');

            // Verifica status atual da subscrição
            await this.checkSubscription();
            
            return true;
        } catch (error) {
            console.error('Erro ao inicializar push notifications:', error);
            return false;
        }
    }

    /**
     * Verifica se já existe uma subscrição ativa
     */
    async checkSubscription() {
        try {
            const subscription = await this.swRegistration.pushManager.getSubscription();
            this.isSubscribed = subscription !== null;
            
            if (this.isSubscribed) {
                console.log('Usuário já está inscrito para notificações');
            }
            
            return this.isSubscribed;
        } catch (error) {
            console.error('Erro ao verificar subscrição:', error);
            return false;
        }
    }

    /**
     * Solicita permissão e cria subscrição
     */
    async subscribe() {
        try {
            // Solicita permissão
            const permission = await Notification.requestPermission();
            
            if (permission !== 'granted') {
                console.warn('Permissão para notificações negada');
                this.showPermissionDeniedMessage();
                return false;
            }

            // Cria subscrição
            const subscription = await this.swRegistration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(this.getVapidPublicKey())
            });

            console.log('Subscrição criada:', subscription);

            // Envia subscrição para o servidor
            await this.sendSubscriptionToServer(subscription);
            
            this.isSubscribed = true;
            this.showSuccessMessage('Notificações ativadas com sucesso! 🔔');
            
            return true;

        } catch (error) {
            console.error('Erro ao criar subscrição:', error);
            this.showErrorMessage('Erro ao ativar notificações');
            return false;
        }
    }

    /**
     * Cancela subscrição de notificações
     */
    async unsubscribe() {
        try {
            const subscription = await this.swRegistration.pushManager.getSubscription();
            
            if (!subscription) {
                console.log('Não há subscrição para cancelar');
                return true;
            }

            // Cancela subscrição no navegador
            await subscription.unsubscribe();

            // Remove subscrição do servidor
            await this.removeSubscriptionFromServer(subscription);
            
            this.isSubscribed = false;
            this.showSuccessMessage('Notificações desativadas');
            
            return true;

        } catch (error) {
            console.error('Erro ao cancelar subscrição:', error);
            this.showErrorMessage('Erro ao desativar notificações');
            return false;
        }
    }

    /**
     * Envia subscrição para o servidor Django
     */
    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/api/push/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON(),
                    device_name: this.getDeviceName()
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao salvar subscrição no servidor');
            }

            const data = await response.json();
            console.log('Subscrição salva no servidor:', data);
            
            return data;

        } catch (error) {
            console.error('Erro ao enviar subscrição:', error);
            throw error;
        }
    }

    /**
     * Remove subscrição do servidor
     */
    async removeSubscriptionFromServer(subscription) {
        try {
            const response = await fetch('/api/push/unsubscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    endpoint: subscription.endpoint
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao remover subscrição do servidor');
            }

            return await response.json();

        } catch (error) {
            console.error('Erro ao remover subscrição:', error);
            throw error;
        }
    }

    /**
     * Envia notificação de teste
     */
    async sendTestNotification() {
        try {
            const response = await fetch('/api/push/test/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao enviar notificação de teste');
            }

            const data = await response.json();
            console.log('Notificação teste enviada:', data);
            
            return data;

        } catch (error) {
            console.error('Erro ao enviar notificação teste:', error);
            this.showErrorMessage('Erro ao enviar notificação de teste');
            throw error;
        }
    }

    /**
     * Converte VAPID key de base64 para Uint8Array
     */
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    /**
     * Retorna a chave pública VAPID (você precisará gerar)
     * Execute: python -c "from pywebpush import generate_vapid_keys; print(generate_vapid_keys())"
     */
    getVapidPublicKey() {
        // IMPORTANTE: Substitua isso pela sua VAPID public key real
        // Essa é apenas uma placeholder - NÃO use em produção
        return window.VAPID_PUBLIC_KEY || 'YOUR_VAPID_PUBLIC_KEY_HERE';
    }

    /**
     * Detecta nome do dispositivo
     */
    getDeviceName() {
        const ua = navigator.userAgent;
        
        if (/iPhone/.test(ua)) return 'iPhone';
        if (/iPad/.test(ua)) return 'iPad';
        if (/Android/.test(ua)) return 'Android';
        if (/Windows/.test(ua)) return 'Windows';
        if (/Mac/.test(ua)) return 'Mac';
        if (/Linux/.test(ua)) return 'Linux';
        
        return 'Navegador';
    }

    /**
     * Exibe mensagem de sucesso
     */
    showSuccessMessage(message) {
        // Se você usar Bootstrap toasts
        if (typeof bootstrap !== 'undefined') {
            this.showToast(message, 'success');
        } else {
            alert(message);
        }
    }

    /**
     * Exibe mensagem de erro
     */
    showErrorMessage(message) {
        if (typeof bootstrap !== 'undefined') {
            this.showToast(message, 'danger');
        } else {
            alert(message);
        }
    }

    /**
     * Exibe mensagem quando permissão é negada
     */
    showPermissionDeniedMessage() {
        const message = 'Para receber alertas importantes, permita notificações nas configurações do navegador.';
        this.showErrorMessage(message);
    }

    /**
     * Helper para mostrar Bootstrap toast
     */
    showToast(message, type = 'info') {
        // Cria toast se não existir container
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        const toastId = 'toast-' + Date.now();
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
        toast.show();

        // Remove do DOM após esconder
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Instância global
const pushManager = new PushNotificationManager();

// Inicializa quando página carrega
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => pushManager.init());
} else {
    pushManager.init();
}

// Exporta para uso global
window.pushManager = pushManager;
