// Game-specific JavaScript for trivia functionality
class TriviaGame {
    constructor() {
        this.currentCard = null;
        this.gameStats = null;
        this.isFlipped = false;
        this.isLoading = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCurrentCard();
        this.setupKeyboardControls();
    }

    setupEventListeners() {
        // Flip card button
        const flipBtn = document.getElementById('flip-btn');
        if (flipBtn) {
            flipBtn.addEventListener('click', () => this.flipCard());
        }

        // Answer buttons
        const correctBtn = document.getElementById('correct-btn');
        const incorrectBtn = document.getElementById('incorrect-btn');

        if (correctBtn) {
            correctBtn.addEventListener('click', () => this.answerCard(true));
        }

        if (incorrectBtn) {
            incorrectBtn.addEventListener('click', () => this.answerCard(false));
        }

        // Navigation buttons
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousCard());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextCard());
        }

        // Reset game button
        const resetBtn = document.getElementById('reset-game-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetGame());
        }

        // Card click to flip (optional UX enhancement)
        const flipCard = document.getElementById('flip-card');
        if (flipCard) {
            flipCard.addEventListener('click', (e) => {
                // Only flip if clicking on the card itself, not buttons
                if (!e.target.closest('.btn') && !this.isFlipped) {
                    this.flipCard();
                }
            });
        }
    }

    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            // Prevent keyboard actions if loading
            if (this.isLoading) return;

            switch (e.key) {
                case ' ':
                case 'Enter':
                    e.preventDefault();
                    if (!this.isFlipped) {
                        this.flipCard();
                    }
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousCard();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextCard();
                    break;
                case '1':
                    e.preventDefault();
                    if (this.isFlipped) {
                        this.answerCard(true);
                    }
                    break;
                case '2':
                    e.preventDefault();
                    if (this.isFlipped) {
                        this.answerCard(false);
                    }
                    break;
                case 'r':
                    e.preventDefault();
                    this.resetGame();
                    break;
            }
        });
    }

    async loadCurrentCard() {
        if (this.isLoading) return;

        try {
            this.setLoadingState(true);
            const response = await this.makeApiCall('/api/current-card');

            if (response.success) {
                this.currentCard = response.card;
                this.gameStats = response.game_stats;
                this.updateUI();
            } else {
                this.showNotification('Failed to load card', 'error');
            }
        } catch (error) {
            console.error('Error loading card:', error);
            this.showNotification('Error loading card', 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    async flipCard() {
        if (this.isLoading || this.isFlipped) return;

        try {
            this.setLoadingState(true);
            const response = await this.makeApiCall('/api/flip-card', {
                method: 'POST'
            });

            if (response.success) {
                this.currentCard = response.card;
                this.isFlipped = true;
                this.animateFlip();
                this.updateUI();
            }
        } catch (error) {
            console.error('Error flipping card:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    async answerCard(isCorrect) {
        if (this.isLoading) return;

        try {
            this.setLoadingState(true);
            const response = await this.makeApiCall('/api/answer-card', {
                method: 'POST',
                body: JSON.stringify({ correct: isCorrect })
            });

            if (response.success) {
                this.currentCard = response.card;
                this.gameStats = response.game_stats;
                this.updateUI();

                // Show feedback
                const message = isCorrect ? 'Correct! 🎉' : 'Incorrect 😔';
                const type = isCorrect ? 'success' : 'error';
                this.showNotification(message, type);

                // Auto-advance after a short delay
                setTimeout(() => {
                    if (this.gameStats.current_index < this.gameStats.total_cards - 1) {
                        this.nextCard();
                    }
                }, 1500);
            }
        } catch (error) {
            console.error('Error answering card:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    async nextCard() {
        if (this.isLoading) return;

        try {
            this.setLoadingState(true);
            const response = await this.makeApiCall('/api/next-card', {
                method: 'POST'
            });

            if (response.success) {
                this.currentCard = response.card;
                this.gameStats = response.game_stats;
                this.isFlipped = false;
                this.resetCardAnimation();
                this.updateUI();
            } else {
                this.showNotification('No more cards available', 'info');
            }
        } catch (error) {
            console.error('Error loading next card:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    async previousCard() {
        if (this.isLoading) return;

        try {
            this.setLoadingState(true);
            const response = await this.makeApiCall('/api/previous-card', {
                method: 'POST'
            });

            if (response.success) {
                this.currentCard = response.card;
                this.gameStats = response.game_stats;
                this.isFlipped = false;
                this.resetCardAnimation();
                this.updateUI();
            } else {
                this.showNotification('No previous card available', 'info');
            }
        } catch (error) {
            console.error('Error loading previous card:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    async resetGame() {
        if (this.isLoading) return;

        if (confirm('Are you sure you want to reset the game? All progress will be lost.')) {
            try {
                this.setLoadingState(true);
                const response = await this.makeApiCall('/api/reset-game', {
                    method: 'POST'
                });

                if (response.success) {
                    this.currentCard = response.card;
                    this.gameStats = response.game_stats;
                    this.isFlipped = false;
                    this.resetCardAnimation();
                    this.updateUI();
                    this.showNotification('Game reset successfully!', 'success');
                }
            } catch (error) {
                console.error('Error resetting game:', error);
            } finally {
                this.setLoadingState(false);
            }
        }
    }

    updateUI() {
        if (!this.currentCard || !this.gameStats) return;

        // Update game stats
        this.updateElement('current-card', this.gameStats.current_index + 1);
        this.updateElement('current-score', this.gameStats.score);
        this.updateElement('accuracy-percentage', `${this.gameStats.percentage}%`);

        // Update progress bar
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            const percentage = ((this.gameStats.current_index + 1) / this.gameStats.total_cards) * 100;
            progressFill.style.width = `${percentage}%`;
        }

        // Update card content
        this.updateElement('category-badge',
            this.currentCard.trivia_question.category.replace('_', ' ').toUpperCase());
        this.updateElement('difficulty-badge',
            this.currentCard.trivia_question.difficulty.toUpperCase());
        this.updateElement('question-text', this.currentCard.trivia_question.question);
        this.updateElement('answer-text', this.currentCard.trivia_question.answer);

        // Update explanation if it exists
        const explanation = document.getElementById('explanation');
        if (explanation && this.currentCard.trivia_question.explanation) {
            explanation.innerHTML = `<p><strong>Explanation:</strong> ${this.currentCard.trivia_question.explanation}</p>`;
        }

        // Update navigation button states
        this.updateNavigationButtons();

        // Update card flip state
        if (this.currentCard.is_flipped && !this.isFlipped) {
            this.isFlipped = true;
            this.animateFlip();
        }
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        if (prevBtn) {
            prevBtn.disabled = this.gameStats.current_index === 0;
        }

        if (nextBtn) {
            nextBtn.disabled = this.gameStats.current_index >= this.gameStats.total_cards - 1;
        }
    }

    animateFlip() {
        const flipCard = document.getElementById('flip-card');
        if (flipCard) {
            flipCard.classList.add('flipped');
        }
    }

    resetCardAnimation() {
        const flipCard = document.getElementById('flip-card');
        if (flipCard) {
            flipCard.classList.remove('flipped');
        }
    }

    setLoadingState(isLoading) {
        this.isLoading = isLoading;
        const spinner = document.getElementById('loading-spinner');

        if (spinner) {
            spinner.style.display = isLoading ? 'block' : 'none';
        }

        // Disable all interactive elements during loading
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            if (isLoading) {
                btn.disabled = true;
                btn.classList.add('loading');
            } else {
                btn.classList.remove('loading');
                // Re-enable based on current state
                this.updateNavigationButtons();
            }
        });
    }

    async makeApiCall(url, options = {}) {
        if (window.triviaApp) {
            return await window.triviaApp.makeApiCall(url, options);
        } else {
            // Fallback if main app is not available
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            return await response.json();
        }
    }

    showNotification(message, type) {
        if (window.triviaApp) {
            window.triviaApp.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize the game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('flip-card')) {
        window.triviaGame = new TriviaGame();
    }
});

// Export for use in tests
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TriviaGame;
}