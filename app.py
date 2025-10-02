"""
Flask application for Python Trivia Flip Card Game
"""
from flask import Flask, render_template, request, jsonify, session
import json
import os
from src.models import TriviaGame, TriviaQuestion, Category, Difficulty


app = Flask(__name__)
app.secret_key = 'python_trivia_secret_key_2024'

# Global game instance (in production, this would be stored in a database)
game = TriviaGame()


def load_sample_questions():
    """Load sample trivia questions into the game"""
    sample_questions = [
        TriviaQuestion(
            "What is the output of print(type([]))?",
            "<class 'list'>",
            Category.BASICS,
            Difficulty.EASY,
            "The type() function returns the type of an object. An empty list [] is of type 'list'."
        ),
        TriviaQuestion(
            "Which Python keyword is used to define a function?",
            "def",
            Category.FUNCTIONS,
            Difficulty.EASY,
            "The 'def' keyword is used to define functions in Python."
        ),
        TriviaQuestion(
            "What does PEP stand for in Python?",
            "Python Enhancement Proposal",
            Category.BASICS,
            Difficulty.MEDIUM,
            "PEP stands for Python Enhancement Proposal, which are design documents for Python."
        ),
        TriviaQuestion(
            "What is the difference between a list and a tuple in Python?",
            "Lists are mutable, tuples are immutable",
            Category.DATA_STRUCTURES,
            Difficulty.MEDIUM,
            "Lists can be modified after creation (mutable), while tuples cannot be changed (immutable)."
        ),
        TriviaQuestion(
            "What is a decorator in Python?",
            "A function that modifies another function",
            Category.ADVANCED,
            Difficulty.HARD,
            "Decorators are a way to modify or enhance functions without permanently modifying their code."
        ),
        TriviaQuestion(
            "What does the __init__ method do in a Python class?",
            "Initializes a new instance of the class",
            Category.OOP,
            Difficulty.MEDIUM,
            "The __init__ method is the constructor that initializes new objects when they are created."
        ),
        TriviaQuestion(
            "Which library is commonly used for data analysis in Python?",
            "pandas",
            Category.LIBRARIES,
            Difficulty.EASY,
            "Pandas is the most popular library for data manipulation and analysis in Python."
        ),
        TriviaQuestion(
            "What is the Global Interpreter Lock (GIL) in Python?",
            "A mutex that prevents multiple threads from executing Python code simultaneously",
            Category.ADVANCED,
            Difficulty.HARD,
            "The GIL ensures that only one thread executes Python bytecode at a time, affecting multi-threading performance."
        )
    ]
    
    for question in sample_questions:
        game.add_question(question)
    
    game.shuffle_cards()


@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')


@app.route('/game')
def game_page():
    """Main game page route"""
    if not game.cards:
        load_sample_questions()
    
    current_card = game.get_current_card()
    return render_template('game.html', 
                         current_card=current_card,
                         game_stats={
                             'current_index': game.current_card_index,
                             'total_cards': len(game.cards),
                             'score': game.score,
                             'percentage': round(game.get_score_percentage(), 1)
                         })


@app.route('/api/current-card')
def get_current_card():
    """API endpoint to get current card data"""
    current_card = game.get_current_card()
    if current_card:
        return jsonify({
            'success': True,
            'card': current_card.to_dict(),
            'game_stats': {
                'current_index': game.current_card_index,
                'total_cards': len(game.cards),
                'score': game.score,
                'percentage': round(game.get_score_percentage(), 1)
            }
        })
    return jsonify({'success': False, 'message': 'No current card available'})


@app.route('/api/flip-card', methods=['POST'])
def flip_card():
    """API endpoint to flip the current card"""
    current_card = game.get_current_card()
    if current_card:
        current_card.flip_card()
        return jsonify({
            'success': True,
            'card': current_card.to_dict()
        })
    return jsonify({'success': False, 'message': 'No card to flip'})


@app.route('/api/answer-card', methods=['POST'])
def answer_card():
    """API endpoint to mark current card as correct or incorrect"""
    data = request.get_json()
    is_correct = data.get('correct', False)
    
    game.answer_current_card(is_correct)
    current_card = game.get_current_card()
    
    return jsonify({
        'success': True,
        'card': current_card.to_dict() if current_card else None,
        'game_stats': {
            'current_index': game.current_card_index,
            'total_cards': len(game.cards),
            'score': game.score,
            'percentage': round(game.get_score_percentage(), 1)
        }
    })


@app.route('/api/next-card', methods=['POST'])
def next_card():
    """API endpoint to move to next card"""
    next_card = game.next_card()
    if next_card:
        return jsonify({
            'success': True,
            'card': next_card.to_dict(),
            'game_stats': {
                'current_index': game.current_card_index,
                'total_cards': len(game.cards),
                'score': game.score,
                'percentage': round(game.get_score_percentage(), 1)
            }
        })
    return jsonify({'success': False, 'message': 'No more cards available'})


@app.route('/api/previous-card', methods=['POST'])
def previous_card():
    """API endpoint to move to previous card"""
    prev_card = game.previous_card()
    if prev_card:
        return jsonify({
            'success': True,
            'card': prev_card.to_dict(),
            'game_stats': {
                'current_index': game.current_card_index,
                'total_cards': len(game.cards),
                'score': game.score,
                'percentage': round(game.get_score_percentage(), 1)
            }
        })
    return jsonify({'success': False, 'message': 'No previous card available'})


@app.route('/api/reset-game', methods=['POST'])
def reset_game():
    """API endpoint to reset the game"""
    game.reset_game()
    game.shuffle_cards()
    current_card = game.get_current_card()
    
    return jsonify({
        'success': True,
        'card': current_card.to_dict() if current_card else None,
        'game_stats': {
            'current_index': game.current_card_index,
            'total_cards': len(game.cards),
            'score': game.score,
            'percentage': round(game.get_score_percentage(), 1)
        }
    })


@app.route('/api/game-stats')
def get_game_stats():
    """API endpoint to get current game statistics"""
    return jsonify({
        'current_index': game.current_card_index,
        'total_cards': len(game.cards),
        'score': game.score,
        'percentage': round(game.get_score_percentage(), 1),
        'answered_cards': sum(1 for card in game.cards if card.is_answered_correctly is not None)
    })


@app.route('/categories')
def categories():
    """Categories filter page"""
    categories_data = {}
    for category in Category:
        category_cards = game.filter_by_category(category)
        categories_data[category.value] = {
            'name': category.value.replace('_', ' ').title(),
            'count': len(category_cards)
        }
    return render_template('categories.html', categories=categories_data)


@app.route('/difficulty')
def difficulty():
    """Difficulty filter page"""
    difficulty_data = {}
    for diff in Difficulty:
        diff_cards = game.filter_by_difficulty(diff)
        difficulty_data[diff.value] = {
            'name': diff.value.title(),
            'count': len(diff_cards)
        }
    return render_template('difficulty.html', difficulties=difficulty_data)


if __name__ == '__main__':
    # Load sample questions on startup
    load_sample_questions()
    app.run(debug=True, host='0.0.0.0', port=5001)