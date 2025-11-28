/**
 * PWA Install Banner - Detecta possibilidade de instalação e mostra instruções
 */

class PWAInstallPrompt {
    constructor() {
        this.deferredPrompt = null;
        this.isIOS = false;
        this.isAndroid = false;
        this.isStandalone = false;
        this.detectPlatform();
    }

    detectPlatform() {
        const userAgent = window.navigator.userAgent.toLowerCase();
        const standalone = window.navigator.standalone;
        
        // Detecta iOS
        this.isIOS = /iphone|ipad|ipod/.test(userAgent);
        
        // Detecta Android
        this.isAndroid = /android/.test(userAgent);
        
        // Verifica se já está instalado (modo standalone)
        this.isStandalone = standalone || 
                           window.matchMedia('(display-mode: standalone)').matches ||
                           window.matchMedia('(display-mode: fullscreen)').matches;
    }

    init() {
        // Se já está instalado, não mostra nada
        if (this.isStandalone) {
            console.log('PWA já instalado');
            return;
        }

        // Listener para Android/Desktop
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallBanner('android');
        });

        // Para iOS, mostra banner após alguns segundos
        if (this.isIOS) {
            // Verifica se já foi fechado antes
            const dismissed = localStorage.getItem('pwa-install-dismissed');
            const dismissedDate = dismissed ? new Date(dismissed) : null;
            
            // Se foi fechado há menos de 7 dias, não mostra
            if (dismissedDate && (new Date() - dismissedDate) < 7 * 24 * 60 * 60 * 1000) {
                return;
            }
            
            // Aguarda 5 segundos e mostra banner
            setTimeout(() => this.showInstallBanner('ios'), 5000);
        }
    }

    showInstallBanner(platform) {
        // Não mostra se já existe
        if (document.getElementById('pwa-install-banner')) {
            return;
        }

        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.className = 'pwa-install-banner';
        
        if (platform === 'ios') {
            banner.innerHTML = `
                <div class="pwa-banner-content">
                    <button class="pwa-banner-close" onclick="pwaInstallPrompt.dismiss()">&times;</button>
                    <div class="pwa-banner-icon">
                        <img src="/static/icons/icon-192x192.png" alt="CashFlow">
                    </div>
                    <div class="pwa-banner-text">
                        <strong>Instalar CashFlow</strong>
                        <p>Adicione à sua tela inicial para acesso rápido</p>
                    </div>
                    <div class="pwa-banner-steps">
                        <p>
                            <span class="step-number">1</span>
                            Toque em 
                            <svg width="18" height="24" viewBox="0 0 18 24" fill="currentColor" style="vertical-align: middle;">
                                <path d="M9 0L9 16M9 16L4 11M9 16L14 11" stroke="currentColor" stroke-width="2" fill="none"/>
                                <rect y="20" width="18" height="4" rx="1"/>
                            </svg>
                            (Compartilhar)
                        </p>
                        <p>
                            <span class="step-number">2</span>
                            Role e toque em "Adicionar à Tela de Início"
                        </p>
                        <p>
                            <span class="step-number">3</span>
                            Toque em "Adicionar"
                        </p>
                    </div>
                </div>
            `;
        } else {
            banner.innerHTML = `
                <div class="pwa-banner-content">
                    <button class="pwa-banner-close" onclick="pwaInstallPrompt.dismiss()">&times;</button>
                    <div class="pwa-banner-icon">
                        <img src="/static/icons/icon-192x192.png" alt="CashFlow">
                    </div>
                    <div class="pwa-banner-text">
                        <strong>Instalar CashFlow</strong>
                        <p>Acesse mais rápido e receba notificações</p>
                    </div>
                    <button class="pwa-banner-install-btn" onclick="pwaInstallPrompt.install()">
                        Instalar App
                    </button>
                </div>
            `;
        }

        // Adiciona estilos
        this.addStyles();
        
        // Adiciona ao body
        document.body.appendChild(banner);
        
        // Anima entrada
        setTimeout(() => banner.classList.add('show'), 100);
    }

    async install() {
        if (!this.deferredPrompt) {
            return;
        }

        // Mostra prompt nativo
        this.deferredPrompt.prompt();
        
        // Aguarda resposta do usuário
        const { outcome } = await this.deferredPrompt.userChoice;
        
        console.log(`Usuário ${outcome === 'accepted' ? 'aceitou' : 'recusou'} instalar`);
        
        // Limpa o prompt
        this.deferredPrompt = null;
        
        // Remove banner
        this.dismiss();
    }

    dismiss() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.classList.remove('show');
            setTimeout(() => banner.remove(), 300);
        }
        
        // Salva data de dismissal
        localStorage.setItem('pwa-install-dismissed', new Date().toISOString());
    }

    addStyles() {
        // Não adiciona se já existe
        if (document.getElementById('pwa-install-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'pwa-install-styles';
        style.textContent = `
            .pwa-install-banner {
                position: fixed;
                bottom: -100%;
                left: 0;
                right: 0;
                background: white;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
                padding: 16px;
                z-index: 9999;
                transition: bottom 0.3s ease;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }

            .pwa-install-banner.show {
                bottom: 0;
            }

            .pwa-banner-content {
                max-width: 600px;
                margin: 0 auto;
                position: relative;
            }

            .pwa-banner-close {
                position: absolute;
                top: -8px;
                right: -8px;
                background: #f0f0f0;
                border: none;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                font-size: 24px;
                line-height: 1;
                cursor: pointer;
                color: #666;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1;
            }

            .pwa-banner-close:hover {
                background: #e0e0e0;
            }

            .pwa-banner-icon {
                float: left;
                margin-right: 12px;
            }

            .pwa-banner-icon img {
                width: 60px;
                height: 60px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }

            .pwa-banner-text {
                overflow: hidden;
            }

            .pwa-banner-text strong {
                display: block;
                font-size: 18px;
                color: #333;
                margin-bottom: 4px;
            }

            .pwa-banner-text p {
                margin: 0;
                color: #666;
                font-size: 14px;
            }

            .pwa-banner-steps {
                clear: both;
                margin-top: 16px;
                padding: 12px;
                background: #f8f9fa;
                border-radius: 8px;
                font-size: 13px;
            }

            .pwa-banner-steps p {
                margin: 8px 0;
                color: #333;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .step-number {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                background: #fbbf24;
                color: white;
                border-radius: 50%;
                font-weight: bold;
                font-size: 12px;
                flex-shrink: 0;
            }

            .pwa-banner-install-btn {
                margin-top: 12px;
                width: 100%;
                padding: 12px;
                background: #fbbf24;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.2s;
            }

            .pwa-banner-install-btn:hover {
                background: #f59e0b;
            }

            .pwa-banner-install-btn:active {
                background: #d97706;
            }

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .pwa-install-banner {
                    background: #1f2937;
                }

                .pwa-banner-text strong {
                    color: #f3f4f6;
                }

                .pwa-banner-text p {
                    color: #d1d5db;
                }

                .pwa-banner-steps {
                    background: #374151;
                }

                .pwa-banner-steps p {
                    color: #f3f4f6;
                }

                .pwa-banner-close {
                    background: #374151;
                    color: #d1d5db;
                }

                .pwa-banner-close:hover {
                    background: #4b5563;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
}

// Instância global
const pwaInstallPrompt = new PWAInstallPrompt();

// Inicializa quando página carrega
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => pwaInstallPrompt.init());
} else {
    pwaInstallPrompt.init();
}

// Exporta para uso global
window.pwaInstallPrompt = pwaInstallPrompt;
