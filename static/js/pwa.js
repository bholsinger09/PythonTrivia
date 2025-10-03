/**
 * PWA (Progressive Web App) initialization and management
 * Handles service worker registration, install prompts, and offline detection
 */

class PWAManager {
    constructor() {
        this.installPrompt = null;
        this.isOnline = navigator.onLine;
        this.serviceWorkerRegistration = null;
        
        this.init();
    }

    async init() {
        try {
            // Register service worker
            await this.regis// Initialize PWA when DOM is ready (prevent duplicate initialization)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.pwaManager) {
            window.pwaManager = new PWAManager();
        }
    });
} else {
    if (!window.pwaManager) {
        window.pwaManager = new PWAManager();
    }
}ceWorker();
            
            // Setup install prompt
            this.setupInstallPrompt();
            
            // Setup offline detection
            this.setupOfflineDetection();
            
            // Setup update checking
            this.setupUpdateDetection();
            
            // Add PWA-specific UI elements
            this.addPWAUI();
            
            console.log('📱 PWA Manager initialized successfully');
        } catch (error) {
            console.error('❌ PWA Manager initialization failed:', error);
            // PWA features will be disabled but app will still work
        }
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                // Try registering from root first, then fallback to static folder
                let registration;
                try {
                    registration = await navigator.serviceWorker.register('/sw.js');
                } catch (error) {
                    console.log('Fallback: Registering service worker from /static/');
                    registration = await navigator.serviceWorker.register('/static/sw.js');
                }
                
                this.serviceWorkerRegistration = registration;
                
                console.log('✅ Service Worker registered successfully');
                
                // Listen for updates
                registration.addEventListener('updatefound', () => {
                    console.log('🔄 Service Worker update found');
                    this.handleServiceWorkerUpdate(registration);
                });
                
                // Check for updates immediately
                registration.update();
                
            } catch (error) {
                console.error('❌ Service Worker registration failed:', error);
                // Don't throw error, just continue without service worker
            }
        }
    }

    setupInstallPrompt() {
        // Listen for install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('📱 Install prompt available');
            e.preventDefault();
            this.installPrompt = e;
            this.showInstallButton();
        });

        // Handle successful installation
        window.addEventListener('appinstalled', () => {
            console.log('🎉 App installed successfully');
            this.hideInstallButton();
            this.showNotification('App installed! You can now use Python Trivia offline.', 'success');
        });
    }

    setupOfflineDetection() {
        // Update online status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateOnlineStatus();
            console.log('🌐 Back online');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateOnlineStatus();
            console.log('📡 Gone offline');
        });

        // Initial status
        this.updateOnlineStatus();
    }

    setupUpdateDetection() {
        // Check for app updates
        if (this.serviceWorkerRegistration) {
            setInterval(() => {
                this.serviceWorkerRegistration.update();
            }, 60000); // Check every minute
        }
    }

    handleServiceWorkerUpdate(registration) {
        const newWorker = registration.installing;
        
        newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New version available
                this.showUpdatePrompt();
            }
        });
    }

    showInstallButton() {
        // Create or show install button
        let installBtn = document.getElementById('install-app-btn');
        
        if (!installBtn) {
            installBtn = document.createElement('button');
            installBtn.id = 'install-app-btn';
            installBtn.className = 'btn btn-primary install-btn';
            installBtn.innerHTML = '📱 Install App';
            installBtn.title = 'Install Python Trivia as an app';
            
            // Add to navigation or create floating button
            const navbar = document.querySelector('.nav-links');
            if (navbar) {
                navbar.appendChild(installBtn);
            } else {
                installBtn.style.position = 'fixed';
                installBtn.style.bottom = '20px';
                installBtn.style.right = '20px';
                installBtn.style.zIndex = '1000';
                document.body.appendChild(installBtn);
            }
            
            installBtn.addEventListener('click', () => this.promptInstall());
        }
        
        installBtn.style.display = 'block';
    }

    hideInstallButton() {
        const installBtn = document.getElementById('install-app-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }

    async promptInstall() {
        if (!this.installPrompt) {
            this.showNotification('Installation not available on this device/browser.', 'info');
            return;
        }

        try {
            const result = await this.installPrompt.prompt();
            console.log('Install prompt result:', result.outcome);
            
            if (result.outcome === 'accepted') {
                this.showNotification('Installing app...', 'success');
            }
            
            this.installPrompt = null;
            this.hideInstallButton();
            
        } catch (error) {
            console.error('Install prompt failed:', error);
            this.showNotification('Installation failed. Please try again.', 'error');
        }
    }

    updateOnlineStatus() {
        // Update UI based on online status
        const statusIndicator = this.getOrCreateStatusIndicator();
        
        if (this.isOnline) {
            statusIndicator.className = 'online-status online';
            statusIndicator.innerHTML = '🌐 Online';
            statusIndicator.title = 'Connected to internet';
        } else {
            statusIndicator.className = 'online-status offline';
            statusIndicator.innerHTML = '📡 Offline';
            statusIndicator.title = 'Offline mode - cached content only';
        }
        
        // Update page elements based on online status
        this.updatePageForOfflineMode();
    }

    getOrCreateStatusIndicator() {
        let indicator = document.getElementById('online-status-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'online-status-indicator';
            indicator.className = 'online-status';
            
            // Add to navbar
            const navbar = document.querySelector('.nav-container');
            if (navbar) {
                navbar.appendChild(indicator);
            }
        }
        
        return indicator;
    }

    updatePageForOfflineMode() {
        const offlineElements = document.querySelectorAll('[data-requires-online]');
        
        offlineElements.forEach(element => {
            if (this.isOnline) {
                element.style.display = '';
                element.disabled = false;
            } else {
                element.style.display = 'none';
                element.disabled = true;
            }
        });

        // Show offline notice if needed
        if (!this.isOnline) {
            this.showOfflineNotice();
        } else {
            this.hideOfflineNotice();
        }
    }

    showUpdatePrompt() {
        const updateBtn = document.createElement('button');
        updateBtn.className = 'btn btn-secondary update-btn';
        updateBtn.innerHTML = '🔄 Update Available';
        updateBtn.title = 'Click to update the app';
        
        updateBtn.addEventListener('click', () => {
            if (this.serviceWorkerRegistration && this.serviceWorkerRegistration.waiting) {
                this.serviceWorkerRegistration.waiting.postMessage({ action: 'skipWaiting' });
                window.location.reload();
            }
        });
        
        // Add to page
        const navbar = document.querySelector('.nav-links');
        if (navbar) {
            navbar.appendChild(updateBtn);
        }
    }

    showOfflineNotice() {
        let notice = document.getElementById('offline-notice');
        
        if (!notice) {
            notice = document.createElement('div');
            notice.id = 'offline-notice';
            notice.className = 'offline-notice';
            notice.innerHTML = `
                <div class="offline-content">
                    📡 You're offline. Some features may be limited.
                    <button onclick="this.parentElement.parentElement.remove()" class="close-btn">×</button>
                </div>
            `;
            
            document.body.appendChild(notice);
        }
        
        notice.style.display = 'block';
    }

    hideOfflineNotice() {
        const notice = document.getElementById('offline-notice');
        if (notice) {
            notice.style.display = 'none';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `pwa-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    addPWAUI() {
        // Add PWA-specific styles
        const style = document.createElement('style');
        style.textContent = `
            .install-btn {
                background: linear-gradient(45deg, #4f46e5, #7c3aed) !important;
                color: white !important;
                border: none !important;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(79, 70, 229, 0); }
                100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }
            }
            
            .online-status {
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: 500;
                margin-left: 10px;
            }
            
            .online-status.online {
                background: rgba(34, 197, 94, 0.1);
                color: #22c55e;
            }
            
            .online-status.offline {
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
            }
            
            .offline-notice {
                position: fixed;
                top: 80px;
                left: 0;
                right: 0;
                background: rgba(239, 68, 68, 0.9);
                color: white;
                text-align: center;
                padding: 10px;
                z-index: 1001;
                display: none;
            }
            
            .offline-content {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
            }
            
            .close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                padding: 0 5px;
            }
            
            .pwa-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px;
                border-radius: 8px;
                color: white;
                z-index: 1002;
                max-width: 300px;
                animation: slideIn 0.3s ease;
            }
            
            .pwa-notification.success {
                background: rgba(34, 197, 94, 0.9);
            }
            
            .pwa-notification.error {
                background: rgba(239, 68, 68, 0.9);
            }
            
            .pwa-notification.info {
                background: rgba(59, 130, 246, 0.9);
            }
            
            .notification-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 16px;
                cursor: pointer;
                margin-left: 10px;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            .update-btn {
                background: #f59e0b !important;
                color: white !important;
                animation: bounce 1s infinite;
            }
            
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% {
                    transform: translateY(0);
                }
                40% {
                    transform: translateY(-5px);
                }
                60% {
                    transform: translateY(-3px);
                }
            }
        `;
        
        document.head.appendChild(style);
    }
}

// Initialize PWA when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new PWAManager();
    });
} else {
    new PWAManager();
}