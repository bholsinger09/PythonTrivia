// Enhanced Game JavaScript for Multiple Choice Trivia
class TriviaGame {
    constructor() {
        this.currentCard = null;
        this.gameStats = null;
        this.isFlipped = false;
        this.isLoading = false;
        this.selectedChoice = null;
        this.hasAnswered = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeFromDOM(); // Get initial state from server-rendered HTML
        this.setupKeyboardControls();
    }

    initializeFromDOM() {
        // Extract game state from the server-rendered HTML instead of making API call
        const questionElement = document.getElementById('question-text');
        const currentCardSpan = document.getElementById('current-card');
        const scoreSpan = document.getElementById('current-score');
        const accuracySpan = document.getElementById('accuracy-percentage');

        // Initialize game stats from DOM
        if (currentCardSpan && scoreSpan && accuracySpan) {
            const currentIndex = parseInt(currentCardSpan.textContent) - 1; // Convert to 0-based
            const score = parseInt(scoreSpan.textContent);
            const percentage = parseFloat(accuracySpan.textContent.replace('%', ''));

            this.gameStats = {
                current_index: currentIndex,
                score: score,
                percentage: percentage,
                total_cards: 8 // We know we have 8 questions
            };
        }

        // Don't overwrite the question - it's already correctly rendered by the server
        console.log('Initialized from DOM - question preserved');
    }

    setupEventListeners() {
        // Choice buttons
        this.setupChoiceButtons();

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

        // Next card button (on back of card)
        const nextCardBtn = document.getElementById('next-card-btn');
        if (nextCardBtn) {
            nextCardBtn.addEventListener('click', () => this.nextCard());
        }

        // Flip back button
        const flipBackBtn = document.getElementById('flip-back-btn');
        if (flipBackBtn) {
            flipBackBtn.addEventListener('click', () => this.flipBack());
        }
    }

    setupChoiceButtons() {
        const choiceButtons = document.querySelectorAll('.btn-choice');
        choiceButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const choiceIndex = parseInt(e.target.dataset.choice);
                this.selectAnswer(choiceIndex);
            });
        });
    }

    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            // Prevent keyboard actions if loading
            if (this.isLoading) return;

            switch (e.key) {
                case '1':
                case 'a':
                case 'A':
                    e.preventDefault();
                    if (!this.hasAnswered && !this.isFlipped) {
                        this.selectAnswer(0);
                    }
                    break;
                case '2':
                case 'b':
                case 'B':
                    e.preventDefault();
                    if (!this.hasAnswered && !this.isFlipped) {
                        this.selectAnswer(1);
                    }
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousCard();
                    break;
                case 'ArrowRight':
                case ' ':
                case 'Enter':
                    e.preventDefault();
                    if (this.isFlipped) {
                        this.nextCard();
                    }
                    break;
                case 'r':
                    e.preventDefault();
                    this.resetGame();
                    break;
                case 'Escape':
                    e.preventDefault();
                    if (this.isFlipped) {
                        this.flipBack();
                    }
                    break;
            }
        });
    }

    async selectAnswer(choiceIndex) {
        if (this.hasAnswered || this.isLoading || this.isFlipped) return;

        try {
            this.setLoadingState(true);
            this.selectedChoice = choiceIndex;
            this.hasAnswered = true;

            // Update UI to show selection
            this.highlightChoice(choiceIndex);

            // Make API call to submit answer
            const response = await this.makeApiCall('/api/answer-card', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    choice_index: choiceIndex
                })
            });

            if (response.success) {
                this.currentCard = response.card;
                this.gameStats = response.game_stats;

                // Show immediate feedback
                this.showAnswerFeedback(response.correct, response.correct_answer);

                // Auto-flip to show answer after a delay
                setTimeout(() => {
                    if (response.correct) {
                        // If correct, show success message briefly then auto-advance
                        setTimeout(() => {
                            this.nextCard();
                        }, 1500);
                    } else {
                        // If incorrect, flip to show correct answer
                        this.flipToAnswer();
                    }
                }, 1000);

            } else {
                this.showNotification('Failed to submit answer', 'error');
                this.hasAnswered = false;
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
            this.showNotification('Error submitting answer', 'error');
            this.hasAnswered = false;
        } finally {
            this.setLoadingState(false);
        }
    }

    highlightChoice(selectedIndex) {
        const choiceButtons = document.querySelectorAll('.btn-choice');
        const correctIndex = this.currentCard?.trivia_question?.correct_choice_index || 0;

        choiceButtons.forEach((button, index) => {
            button.classList.add('disabled');

            if (index === selectedIndex) {
                if (index === correctIndex) {
                    button.classList.add('correct');
                } else {
                    button.classList.add('incorrect');
                }
            } else if (index === correctIndex && selectedIndex !== correctIndex) {
                // Show correct answer if user selected wrong
                button.classList.add('correct');
            }
        });
    }

    showAnswerFeedback(isCorrect, correctAnswer) {
        const feedbackElement = document.getElementById('feedback-message');
        const feedbackText = document.getElementById('feedback-text');

        if (feedbackElement && feedbackText) {
            feedbackElement.style.display = 'block';
            feedbackElement.className = `feedback-message ${isCorrect ? 'correct' : 'incorrect'}`;
            feedbackText.textContent = isCorrect ?
                '🎉 Correct!' :
                `❌ Incorrect. The answer is: ${correctAnswer}`;
        }
    }

    flipToAnswer() {
        this.isFlipped = true;
        this.animateFlip();
        this.updateAnswerDisplay();
    }

    flipBack() {
        this.isFlipped = false;
        this.hasAnswered = false;
        this.selectedChoice = null;
        this.animateFlipBack();
        this.resetChoiceButtons();
        this.hideFeedback();
    }

    resetChoiceButtons() {
        const choiceButtons = document.querySelectorAll('.btn-choice');
        choiceButtons.forEach(button => {
            button.classList.remove('disabled', 'correct', 'incorrect');
        });
    }

    hideFeedback() {
        const feedbackElement = document.getElementById('feedback-message');
        if (feedbackElement) {
            feedbackElement.style.display = 'none';
        }
    }

    async loadCurrentCard() {
        if (this.isLoading) return;

        try {
            this.setLoadingState(true);
            const response = await this.makeApiCall('/api/current-card');

            if (response.success) {
                this.currentCard = response.card;
                this.gameStats = response.game_stats;
                this.isFlipped = false;
                this.hasAnswered = false;
                this.selectedChoice = null;
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
                this.hasAnswered = false;
                this.selectedChoice = null;
                this.updateUI();
            } else if (response.message === 'No more cards') {
                this.showGameComplete();
            }
        } catch (error) {
            console.error('Error moving to next card:', error);
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
                this.hasAnswered = false;
                this.selectedChoice = null;
                this.updateUI();
            }
        } catch (error) {
            console.error('Error moving to previous card:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    updateUI() {
        if (!this.currentCard) return;

        // Update question and choices
        this.updateQuestionText();
        this.updateChoices();
        this.updateGameStats();
        this.updateProgressBar();
        this.updateNavigationButtons();
        this.resetChoiceButtons();
        this.hideFeedback();

        // Reset flip state
        if (this.isFlipped) {
            this.updateAnswerDisplay();
        } else {
            this.animateFlipBack();
        }
    }

    updateQuestionText() {
        const questionElement = document.getElementById('question-text');
        console.log('updateQuestionText called');
        console.log('questionElement:', questionElement);
        console.log('this.currentCard:', this.currentCard);

        if (questionElement && this.currentCard) {
            const questionText = this.currentCard.trivia_question.question;
            console.log('Setting question text to:', questionText);
            questionElement.textContent = questionText;
        } else {
            console.log('Cannot update question text - missing element or card');
        }
    }

    updateChoices() {
        if (!this.currentCard?.trivia_question?.choices) return;

        const choice0 = document.getElementById('choice-0');
        const choice1 = document.getElementById('choice-1');

        if (choice0 && this.currentCard.trivia_question.choices[0]) {
            choice0.innerHTML = `A) ${this.currentCard.trivia_question.choices[0]}`;
        }

        if (choice1 && this.currentCard.trivia_question.choices[1]) {
            choice1.innerHTML = `B) ${this.currentCard.trivia_question.choices[1]}`;
        }
    }

    updateAnswerDisplay() {
        const answerElement = document.getElementById('answer-text');
        const explanationElement = document.getElementById('explanation');
        const resultIndicator = document.getElementById('result-indicator');
        const resultText = document.getElementById('result-text');

        if (answerElement && this.currentCard) {
            answerElement.textContent = this.currentCard.trivia_question.answer;
        }

        if (explanationElement && this.currentCard?.trivia_question?.explanation) {
            explanationElement.innerHTML = `<p><strong>Explanation:</strong> ${this.currentCard.trivia_question.explanation}</p>`;
            explanationElement.style.display = 'block';
        } else if (explanationElement) {
            explanationElement.style.display = 'none';
        }

        // Show result indicator
        if (resultIndicator && resultText && this.hasAnswered) {
            const isCorrect = this.selectedChoice === this.currentCard.trivia_question.correct_choice_index;
            resultIndicator.className = `result-indicator ${isCorrect ? 'correct' : 'incorrect'}`;
            resultText.textContent = isCorrect ? '✓ Correct' : '✗ Incorrect';
            resultIndicator.style.display = 'inline-block';
        } else if (resultIndicator) {
            resultIndicator.style.display = 'none';
        }
    }

    updateGameStats() {
        if (!this.gameStats) return;

        const currentCardElement = document.getElementById('current-card');
        const currentScoreElement = document.getElementById('current-score');
        const accuracyElement = document.getElementById('accuracy-percentage');

        if (currentCardElement) {
            currentCardElement.textContent = this.gameStats.current_index + 1;
        }

        if (currentScoreElement) {
            currentScoreElement.textContent = this.gameStats.score;
        }

        if (accuracyElement) {
            accuracyElement.textContent = `${this.gameStats.percentage}%`;
        }
    }

    updateProgressBar() {
        if (!this.gameStats) return;

        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            const percentage = ((this.gameStats.current_index + 1) / this.gameStats.total_cards) * 100;
            progressFill.style.width = `${percentage}%`;
        }
    }

    updateNavigationButtons() {
        if (!this.gameStats) return;

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
        const flipCardInner = document.getElementById('flip-card-inner');
        if (flipCardInner) {
            flipCardInner.style.transform = 'rotateY(180deg)';
        }
    }

    animateFlipBack() {
        const flipCardInner = document.getElementById('flip-card-inner');
        if (flipCardInner) {
            flipCardInner.style.transform = 'rotateY(0deg)';
        }
    }

    showGameComplete() {
        const accuracy = this.gameStats ? this.gameStats.percentage : 0;
        const score = this.gameStats ? this.gameStats.score : 0;
        const total = this.gameStats ? this.gameStats.total_cards : 0;

        const message = `🎉 Game Complete!\n\nFinal Score: ${score}/${total}\nAccuracy: ${accuracy}%\n\nWould you like to play again?`;

        if (confirm(message)) {
            this.resetGame();
        }
    }

    async resetGame() {
        if (this.isLoading) return;

        try {
            this.setLoadingState(true);
            const response = await this.makeApiCall('/api/reset-game', {
                method: 'POST'
            });

            if (response.success) {
                this.currentCard = response.card;
                this.gameStats = response.game_stats;
                this.isFlipped = false;
                this.hasAnswered = false;
                this.selectedChoice = null;
                this.updateUI();
                this.showNotification('Game reset successfully!', 'success');
            }
        } catch (error) {
            console.error('Error resetting game:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    setLoadingState(loading) {
        this.isLoading = loading;
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.style.display = loading ? 'flex' : 'none';
        }
    }

    async makeApiCall(url, options = {}) {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 1000;
                transform: translateX(100%);
                transition: transform 0.3s ease;
            `;
            document.body.appendChild(notification);
        }

        // Set notification style based on type
        const colors = {
            success: '#48bb78',
            error: '#f56565',
            info: '#4f46e5'
        };

        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;

        // Show notification
        notification.style.transform = 'translateX(0)';

        // Hide after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
        }, 3000);
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.triviaGame = new TriviaGame();
});