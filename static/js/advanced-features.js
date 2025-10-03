/**
 * Advanced Frontend Features Manager
 * Dark mode, achievements, accessibility, sound effects, and enhanced UX
 */

class AdvancedFeaturesManager {
    constructor() {
        this.darkMode = false;
        this.soundEnabled = true;
        this.achievements = [];
        this.gameStats = {
            totalGames: 0,
            correctAnswers: 0,
            streak: 0,
            maxStreak: 0
        };

        this.init();
    }

    async init() {
        // Load user preferences
        this.loadPreferences();

        // Setup dark mode
        this.setupDarkMode();

        // Setup achievements system
        this.setupAchievements();

        // Setup accessibility enhancements
        this.setupAccessibility();

        // Setup sound effects
        await this.setupSoundEffects();

        // Add advanced UI controls
        this.addAdvancedControls();

        // Setup performance monitoring
        this.setupPerformanceMonitoring();

        console.log('✨ Advanced features initialized');
    }

    // Dark Mode Implementation
    setupDarkMode() {
        // Check system preference
        const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)');

        // Apply initial theme
        this.applyDarkMode(this.darkMode || systemDarkMode.matches);

        // Listen for system changes
        systemDarkMode.addEventListener('change', (e) => {
            if (!localStorage.getItem('darkMode')) {
                this.applyDarkMode(e.matches);
            }
        });
    }

    applyDarkMode(enabled) {
        this.darkMode = enabled;

        if (enabled) {
            document.documentElement.classList.add('dark-mode');
        } else {
            document.documentElement.classList.remove('dark-mode');
        }

        // Update toggle button if exists
        const toggle = document.getElementById('dark-mode-toggle');
        if (toggle) {
            toggle.innerHTML = enabled ? '☀️' : '🌙';
            toggle.title = enabled ? 'Switch to Light Mode' : 'Switch to Dark Mode';
        }

        // Save preference
        localStorage.setItem('darkMode', enabled);
    }

    toggleDarkMode() {
        this.applyDarkMode(!this.darkMode);
        this.playSound('toggle');
        this.showNotification(`${this.darkMode ? 'Dark' : 'Light'} mode activated`, 'info');
    }

    // Achievement System
    setupAchievements() {
        this.achievementDefinitions = [
            {
                id: 'first_game',
                name: 'Getting Started',
                description: 'Play your first game',
                icon: '🎮',
                condition: (stats) => stats.totalGames >= 1
            },
            {
                id: 'perfect_game',
                name: 'Perfect Score',
                description: 'Answer all questions correctly in one game',
                icon: '🏆',
                condition: (stats, gameData) => gameData && gameData.percentage === 100
            },
            {
                id: 'streak_master',
                name: 'Streak Master',
                description: 'Get 10 correct answers in a row',
                icon: '🔥',
                condition: (stats) => stats.maxStreak >= 10
            },
            {
                id: 'speed_demon',
                name: 'Speed Demon',
                description: 'Answer a question in under 3 seconds',
                icon: '⚡',
                condition: (stats, gameData) => gameData && gameData.fastestAnswer < 3000
            },
            {
                id: 'dedicated_player',
                name: 'Dedicated Player',
                description: 'Play 25 games',
                icon: '🎯',
                condition: (stats) => stats.totalGames >= 25
            },
            {
                id: 'knowledge_seeker',
                name: 'Knowledge Seeker',
                description: 'Answer 100 questions correctly',
                icon: '📚',
                condition: (stats) => stats.correctAnswers >= 100
            }
        ];

        this.loadAchievements();
    }

    checkAchievements(gameData = null) {
        const newAchievements = [];

        this.achievementDefinitions.forEach(achievement => {
            if (!this.achievements.includes(achievement.id)) {
                if (achievement.condition(this.gameStats, gameData)) {
                    this.achievements.push(achievement.id);
                    newAchievements.push(achievement);
                }
            }
        });

        if (newAchievements.length > 0) {
            this.saveAchievements();
            newAchievements.forEach(achievement => {
                this.showAchievement(achievement);
            });
        }
    }

    showAchievement(achievement) {
        this.playSound('achievement');

        // Create achievement notification
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-content">
                <div class="achievement-icon">${achievement.icon}</div>
                <div class="achievement-text">
                    <div class="achievement-title">Achievement Unlocked!</div>
                    <div class="achievement-name">${achievement.name}</div>
                    <div class="achievement-description">${achievement.description}</div>
                </div>
            </div>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);

        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 500);
        }, 4000);
    }

    // Accessibility Enhancements
    setupAccessibility() {
        // High contrast mode
        const highContrast = localStorage.getItem('highContrast') === 'true';
        if (highContrast) {
            document.documentElement.classList.add('high-contrast');
        }

        // Reduced motion
        const reducedMotion = localStorage.getItem('reducedMotion') === 'true';
        if (reducedMotion) {
            document.documentElement.classList.add('reduced-motion');
        }

        // Font size adjustment
        const fontSize = localStorage.getItem('fontSize') || 'normal';
        document.documentElement.classList.add(`font-size-${fontSize}`);

        // Keyboard navigation enhancements
        this.enhanceKeyboardNavigation();

        // Screen reader improvements
        this.addScreenReaderSupport();
    }

    enhanceKeyboardNavigation() {
        // Add visible focus indicators
        const style = document.createElement('style');
        style.textContent = `
            .keyboard-user *:focus {
                outline: 3px solid var(--primary-color) !important;
                outline-offset: 2px !important;
            }
        `;
        document.head.appendChild(style);

        // Detect keyboard users
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-user');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-user');
        });

        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Alt + D: Toggle dark mode
            if (e.altKey && e.key.toLowerCase() === 'd') {
                e.preventDefault();
                this.toggleDarkMode();
            }

            // Alt + S: Toggle sound
            if (e.altKey && e.key.toLowerCase() === 's') {
                e.preventDefault();
                this.toggleSound();
            }
        });
    }

    addScreenReaderSupport() {
        // Add live region for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.id = 'live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(liveRegion);

        // Enhanced button labels
        document.querySelectorAll('.btn').forEach(btn => {
            if (!btn.getAttribute('aria-label') && btn.textContent.trim()) {
                btn.setAttribute('aria-label', btn.textContent.trim());
            }
        });
    }

    announceToScreenReader(message) {
        const liveRegion = document.getElementById('live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
        }
    }

    // Sound Effects System
    async setupSoundEffects() {
        this.sounds = {};

        // Create audio context if supported
        if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
            this.audioContext = new (AudioContext || webkitAudioContext)();
        }

        // Define sound effects (using Web Audio API for generated sounds)
        this.soundDefinitions = {
            correct: { frequency: 523.25, duration: 200, type: 'sine' }, // C5
            incorrect: { frequency: 220, duration: 400, type: 'sawtooth' }, // A3
            flip: { frequency: 440, duration: 150, type: 'square' }, // A4
            achievement: { frequency: 659.25, duration: 300, type: 'sine' }, // E5
            toggle: { frequency: 350, duration: 100, type: 'triangle' },
            navigation: { frequency: 300, duration: 80, type: 'sine' }
        };

        // Load sound preference
        this.soundEnabled = localStorage.getItem('soundEnabled') !== 'false';
    }

    generateSound(definition) {
        if (!this.audioContext || !this.soundEnabled) return null;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.frequency.value = definition.frequency;
        oscillator.type = definition.type;

        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + definition.duration / 1000);

        return { oscillator, gainNode, duration: definition.duration };
    }

    playSound(soundName) {
        if (!this.soundEnabled || !this.audioContext) return;

        const definition = this.soundDefinitions[soundName];
        if (!definition) return;

        try {
            // Resume audio context if needed (browser autoplay policy)
            if (this.audioContext.state === 'suspended') {
                this.audioContext.resume();
            }

            const sound = this.generateSound(definition);
            if (sound) {
                sound.oscillator.start();
                sound.oscillator.stop(this.audioContext.currentTime + sound.duration / 1000);
            }
        } catch (error) {
            console.warn('Sound playback failed:', error);
        }
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        localStorage.setItem('soundEnabled', this.soundEnabled);

        const toggle = document.getElementById('sound-toggle');
        if (toggle) {
            toggle.innerHTML = this.soundEnabled ? '🔊' : '🔇';
            toggle.title = this.soundEnabled ? 'Disable Sound' : 'Enable Sound';
        }

        if (this.soundEnabled) {
            this.playSound('toggle');
        }

        this.showNotification(`Sound ${this.soundEnabled ? 'enabled' : 'disabled'}`, 'info');
    }

    // Advanced UI Controls
    addAdvancedControls() {
        // Create controls container
        const controls = document.createElement('div');
        controls.className = 'advanced-controls';
        controls.innerHTML = `
            <button id="dark-mode-toggle" class="control-btn" title="Toggle Dark Mode">
                🌙
            </button>
            <button id="sound-toggle" class="control-btn" title="Toggle Sound">
                🔊
            </button>
            <button id="accessibility-menu-toggle" class="control-btn" title="Accessibility Options">
                ♿
            </button>
            <button id="achievements-toggle" class="control-btn" title="View Achievements">
                🏆
            </button>
        `;

        // Add to page
        const navbar = document.querySelector('.nav-container');
        if (navbar) {
            navbar.appendChild(controls);
        }

        // Setup event listeners
        document.getElementById('dark-mode-toggle').addEventListener('click', () => this.toggleDarkMode());
        document.getElementById('sound-toggle').addEventListener('click', () => this.toggleSound());
        document.getElementById('accessibility-menu-toggle').addEventListener('click', () => this.showAccessibilityMenu());
        document.getElementById('achievements-toggle').addEventListener('click', () => this.showAchievements());

        // Update initial states
        document.getElementById('dark-mode-toggle').innerHTML = this.darkMode ? '☀️' : '🌙';
        document.getElementById('sound-toggle').innerHTML = this.soundEnabled ? '🔊' : '🔇';
    }

    showAccessibilityMenu() {
        // Create accessibility menu modal
        const modal = this.createModal('Accessibility Options', `
            <div class="accessibility-options">
                <div class="option-group">
                    <h3>Visual</h3>
                    <label class="option-item">
                        <input type="checkbox" id="high-contrast-toggle" ${document.documentElement.classList.contains('high-contrast') ? 'checked' : ''}>
                        <span>High Contrast Mode</span>
                    </label>
                    <label class="option-item">
                        <span>Font Size:</span>
                        <select id="font-size-select">
                            <option value="small">Small</option>
                            <option value="normal" selected>Normal</option>
                            <option value="large">Large</option>
                            <option value="extra-large">Extra Large</option>
                        </select>
                    </label>
                </div>
                <div class="option-group">
                    <h3>Motion</h3>
                    <label class="option-item">
                        <input type="checkbox" id="reduced-motion-toggle" ${document.documentElement.classList.contains('reduced-motion') ? 'checked' : ''}>
                        <span>Reduce Motion</span>
                    </label>
                </div>
                <div class="option-group">
                    <h3>Keyboard Shortcuts</h3>
                    <div class="shortcuts-info">
                        <div>Alt + D: Toggle Dark Mode</div>
                        <div>Alt + S: Toggle Sound</div>
                        <div>Tab: Navigate elements</div>
                        <div>Space/Enter: Activate buttons</div>
                    </div>
                </div>
            </div>
        `);

        // Setup accessibility option listeners
        this.setupAccessibilityOptions(modal);
    }

    showAchievements() {
        const unlockedAchievements = this.achievementDefinitions.filter(a =>
            this.achievements.includes(a.id)
        );
        const lockedAchievements = this.achievementDefinitions.filter(a =>
            !this.achievements.includes(a.id)
        );

        const achievementsHTML = `
            <div class="achievements-container">
                <div class="achievements-stats">
                    <div class="stat">
                        <strong>${unlockedAchievements.length}</strong> / ${this.achievementDefinitions.length} Unlocked
                    </div>
                </div>
                <div class="achievements-grid">
                    ${unlockedAchievements.map(achievement => `
                        <div class="achievement-item unlocked">
                            <div class="achievement-icon">${achievement.icon}</div>
                            <div class="achievement-info">
                                <div class="achievement-name">${achievement.name}</div>
                                <div class="achievement-description">${achievement.description}</div>
                            </div>
                        </div>
                    `).join('')}
                    ${lockedAchievements.map(achievement => `
                        <div class="achievement-item locked">
                            <div class="achievement-icon">🔒</div>
                            <div class="achievement-info">
                                <div class="achievement-name">???</div>
                                <div class="achievement-description">${achievement.description}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        this.createModal('Achievements', achievementsHTML);
    }

    createModal(title, content) {
        // Remove existing modal
        const existingModal = document.querySelector('.modal-overlay');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" aria-label="Close modal">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Setup close handlers
        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        return modal;
    }

    setupAccessibilityOptions(modal) {
        const highContrastToggle = modal.querySelector('#high-contrast-toggle');
        const fontSizeSelect = modal.querySelector('#font-size-select');
        const reducedMotionToggle = modal.querySelector('#reduced-motion-toggle');

        // Set current values
        fontSizeSelect.value = localStorage.getItem('fontSize') || 'normal';

        // Event listeners
        highContrastToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.documentElement.classList.add('high-contrast');
            } else {
                document.documentElement.classList.remove('high-contrast');
            }
            localStorage.setItem('highContrast', e.target.checked);
        });

        fontSizeSelect.addEventListener('change', (e) => {
            document.documentElement.className = document.documentElement.className
                .replace(/font-size-\w+/g, '');
            document.documentElement.classList.add(`font-size-${e.target.value}`);
            localStorage.setItem('fontSize', e.target.value);
        });

        reducedMotionToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.documentElement.classList.add('reduced-motion');
            } else {
                document.documentElement.classList.remove('reduced-motion');
            }
            localStorage.setItem('reducedMotion', e.target.checked);
        });
    }

    // Performance Monitoring
    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            if (performance.getEntriesByType) {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    console.log(`⚡ Page loaded in ${Math.round(navigation.loadEventEnd)}ms`);
                }
            }
        });

        // Monitor frame rate
        let lastTime = performance.now();
        let frameCount = 0;

        const measureFrameRate = (currentTime) => {
            frameCount++;

            if (currentTime - lastTime >= 1000) {
                const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));

                // Log if FPS is below threshold
                if (fps < 30) {
                    console.warn(`⚠️ Low FPS detected: ${fps}fps`);
                }

                frameCount = 0;
                lastTime = currentTime;
            }

            requestAnimationFrame(measureFrameRate);
        };

        requestAnimationFrame(measureFrameRate);
    }

    // Utility Methods
    loadPreferences() {
        this.darkMode = localStorage.getItem('darkMode') === 'true';
        this.soundEnabled = localStorage.getItem('soundEnabled') !== 'false';
        this.loadGameStats();
    }

    loadGameStats() {
        const stored = localStorage.getItem('gameStats');
        if (stored) {
            this.gameStats = { ...this.gameStats, ...JSON.parse(stored) };
        }
    }

    saveGameStats() {
        localStorage.setItem('gameStats', JSON.stringify(this.gameStats));
    }

    loadAchievements() {
        const stored = localStorage.getItem('achievements');
        if (stored) {
            this.achievements = JSON.parse(stored);
        }
    }

    saveAchievements() {
        localStorage.setItem('achievements', JSON.stringify(this.achievements));
    }

    updateGameStats(gameData) {
        this.gameStats.totalGames++;
        this.gameStats.correctAnswers += gameData.correctCount || 0;

        if (gameData.isCorrect) {
            this.gameStats.streak++;
            this.gameStats.maxStreak = Math.max(this.gameStats.maxStreak, this.gameStats.streak);
        } else {
            this.gameStats.streak = 0;
        }

        this.saveGameStats();
        this.checkAchievements(gameData);
    }

    showNotification(message, type = 'info') {
        // Use existing notification system or create simple one
        const notification = document.createElement('div');
        notification.className = `advanced-notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize when ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.advancedFeatures) {
            window.advancedFeatures = new AdvancedFeaturesManager();
        }
    });
} else {
    if (!window.advancedFeatures) {
        window.advancedFeatures = new AdvancedFeaturesManager();
    }
}