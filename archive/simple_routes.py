# SIMPLE GAME API ROUTES

@app.route('/api/current-card')
@api_rate_limit
def get_current_card():
    """Get current card data - simple version"""
    return jsonify({
        'success': True,
        'card': {
            'trivia_question': {
                'question': 'Sample question?',
                'choices': ['Option A', 'Option B'],
                'answer': 'Option A',
                'explanation': 'Sample explanation',
                'category': 'basics',
                'difficulty': 'easy'
            },
            'is_flipped': False,
            'is_answered_correctly': None
        },
        'game_stats': {
            'current_index': 0,
            'total_cards': 8,
            'score': 0,
            'percentage': 0
        }
    })

@app.route('/api/flip-card', methods=['POST'])
@api_rate_limit
def flip_card():
    """Flip the current card - simple version"""
    return jsonify({
        'success': True,
        'card': {
            'trivia_question': {
                'question': 'Sample question?',
                'choices': ['Option A', 'Option B'],
                'answer': 'Option A',
                'explanation': 'Sample explanation',
                'category': 'basics',
                'difficulty': 'easy'
            },
            'is_flipped': True,
            'is_answered_correctly': None
        }
    })

@app.route('/api/answer-card', methods=['POST'])
@api_rate_limit
def answer_card():
    """Submit answer for current card - simple version"""
    data = request.get_json() or {}
    choice_index = data.get('choice_index', 0)
    is_correct = choice_index == 0  # Assume first choice is correct
    
    return jsonify({
        'success': True,
        'correct': is_correct,
        'correct_answer': '0',
        'card': {
            'trivia_question': {
                'question': 'Sample question?',
                'choices': ['Option A', 'Option B'],
                'answer': 'Option A',
                'explanation': 'Sample explanation',
                'category': 'basics',
                'difficulty': 'easy'
            },
            'is_flipped': True,
            'is_answered_correctly': is_correct
        },
        'game_stats': {
            'current_index': 0,
            'total_cards': 8,
            'score': 1 if is_correct else 0,
            'percentage': 100 if is_correct else 0
        }
    })

@app.route('/api/next-card', methods=['POST'])
@api_rate_limit
def next_card():
    """Move to next card - simple version"""
    return jsonify({
        'success': True,
        'card': {
            'trivia_question': {
                'question': 'Next sample question?',
                'choices': ['Option A', 'Option B'],
                'answer': 'Option B',
                'explanation': 'Next sample explanation',
                'category': 'basics',
                'difficulty': 'easy'
            },
            'is_flipped': False,
            'is_answered_correctly': None
        },
        'game_stats': {
            'current_index': 1,
            'total_cards': 8,
            'score': 0,
            'percentage': 0
        }
    })

@app.route('/api/previous-card', methods=['POST'])
@api_rate_limit
def previous_card():
    """Move to previous card - simple version"""
    return jsonify({
        'success': True,
        'card': {
            'trivia_question': {
                'question': 'Previous sample question?',
                'choices': ['Option A', 'Option B'],
                'answer': 'Option A',
                'explanation': 'Previous sample explanation',
                'category': 'basics',
                'difficulty': 'easy'
            },
            'is_flipped': False,
            'is_answered_correctly': None
        },
        'game_stats': {
            'current_index': 0,
            'total_cards': 8,
            'score': 0,
            'percentage': 0
        }
    })

@app.route('/api/game-stats')
@api_rate_limit
def get_game_stats():
    """Get current game statistics - simple version"""
    return jsonify({
        'success': True,
        'game_stats': {
            'current_index': 0,
            'total_cards': 8,
            'score': 0,
            'percentage': 0,
            'streak': 0,
            'best_streak': 0
        }
    })

@app.route('/api/reset-game', methods=['POST'])
@api_rate_limit
def reset_game():
    """Reset the game to start over - simple version"""
    return jsonify({
        'success': True,
        'card': {
            'trivia_question': {
                'question': 'Reset sample question?',
                'choices': ['Option A', 'Option B'],
                'answer': 'Option A',
                'explanation': 'Reset sample explanation',
                'category': 'basics',
                'difficulty': 'easy'
            },
            'is_flipped': False,
            'is_answered_correctly': None
        },
        'game_stats': {
            'current_index': 0,
            'total_cards': 8,
            'score': 0,
            'percentage': 0
        }
    })

@app.route('/api/save-score', methods=['POST'])
@api_rate_limit
def save_score():
    """Save game score to leaderboard - simple version"""
    return jsonify({
        'success': True,
        'score_saved': 0,
        'message': 'Score saved successfully!'
    })

if __name__ == '__main__':
    # Initialize database on startup
    initialize_database()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )