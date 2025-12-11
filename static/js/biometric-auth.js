/**
 * Sistema de Autenticação Biométrica (WebAuthn)
 * Permite login usando impressão digital, reconhecimento facial, etc.
 */

class BiometricAuth {
    constructor() {
        this.isAvailable = false;
        this.isRegistered = false;
        this.checkAvailability();
    }

    /**
     * Verifica se WebAuthn está disponível no navegador
     */
    async checkAvailability() {
        if (!window.PublicKeyCredential) {
            console.warn('WebAuthn não suportado neste navegador');
            this.isAvailable = false;
            return false;
        }

        try {
            // Verificar se há autenticadores disponíveis
            const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
            this.isAvailable = available;
            console.log('WebAuthn disponível:', available);
            return available;
        } catch (error) {
            console.error('Erro ao verificar disponibilidade WebAuthn:', error);
            this.isAvailable = false;
            return false;
        }
    }

    /**
     * Verifica se o usuário já tem credencial registrada
     */
    async checkRegistration() {
        try {
            const response = await fetch('/api/webauthn/authenticate/options/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });

            if (response.ok) {
                this.isRegistered = true;
                return true;
            } else {
                this.isRegistered = false;
                return false;
            }
        } catch (error) {
            console.error('Erro ao verificar registro:', error);
            this.isRegistered = false;
            return false;
        }
    }

    /**
     * Registra uma nova credencial biométrica
     */
    async register() {
        try {
            if (!this.isAvailable) {
                throw new Error('Autenticação biométrica não disponível neste dispositivo');
            }

            // Obter opções de registro do servidor
            const optionsResponse = await fetch('/api/webauthn/register/options/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });

            if (!optionsResponse.ok) {
                const error = await optionsResponse.json();
                throw new Error(error.error || 'Erro ao obter opções de registro');
            }

            const options = await optionsResponse.json();

            // Criar credencial
            const credential = await navigator.credentials.create({
                publicKey: options
            });

            // Enviar credencial para verificação no servidor
            const verifyResponse = await fetch('/api/webauthn/register/verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({
                    ...credential.toJSON(),
                    device_name: this.getDeviceName(),
                    transports: credential.response.getTransports ? credential.response.getTransports() : []
                })
            });

            if (!verifyResponse.ok) {
                const error = await verifyResponse.json();
                throw new Error(error.error || 'Erro ao verificar credencial');
            }

            const result = await verifyResponse.json();
            this.isRegistered = true;

            return result;

        } catch (error) {
            console.error('Erro no registro biométrico:', error);
            throw error;
        }
    }

    /**
     * Realiza autenticação biométrica
     */
    async authenticate() {
        try {
            if (!this.isAvailable) {
                throw new Error('Autenticação biométrica não disponível');
            }

            if (!this.isRegistered) {
                throw new Error('Nenhuma credencial biométrica registrada');
            }

            // Obter opções de autenticação do servidor
            const optionsResponse = await fetch('/api/webauthn/authenticate/options/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });

            if (!optionsResponse.ok) {
                const error = await optionsResponse.json();
                throw new Error(error.error || 'Erro ao obter opções de autenticação');
            }

            const options = await optionsResponse.json();

            // Obter credencial
            const credential = await navigator.credentials.get({
                publicKey: options
            });

            // Enviar para verificação no servidor
            const verifyResponse = await fetch('/api/webauthn/authenticate/verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify(credential.toJSON())
            });

            if (!verifyResponse.ok) {
                const error = await verifyResponse.json();
                throw new Error(error.error || 'Erro na autenticação biométrica');
            }

            const result = await verifyResponse.json();
            return result;

        } catch (error) {
            console.error('Erro na autenticação biométrica:', error);
            throw error;
        }
    }

    /**
     * Remove a credencial biométrica
     */
    async remove() {
        try {
            const response = await fetch('/api/webauthn/remove/', {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Erro ao remover credencial');
            }

            const result = await response.json();
            this.isRegistered = false;

            return result;

        } catch (error) {
            console.error('Erro ao remover credencial biométrica:', error);
            throw error;
        }
    }

    /**
     * Detecta nome do dispositivo
     */
    getDeviceName() {
        const ua = navigator.userAgent;

        if (/iPhone/.test(ua)) return 'iPhone';
        if (/iPad/.test(ua)) return 'iPad';
        if (/Android/.test(ua)) return 'Android Device';
        if (/Windows/.test(ua)) return 'Windows PC';
        if (/Mac/.test(ua)) return 'Mac';
        if (/Linux/.test(ua)) return 'Linux PC';

        return 'Dispositivo Desconhecido';
    }

    /**
     * Obtém token CSRF
     */
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    /**
     * Mostra mensagem de sucesso
     */
    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    /**
     * Mostra mensagem de erro
     */
    showError(message) {
        this.showMessage(message, 'error');
    }

    /**
     * Mostra mensagem genérica
     */
    showMessage(message, type = 'info') {
        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Instância global
const biometricAuth = new BiometricAuth();