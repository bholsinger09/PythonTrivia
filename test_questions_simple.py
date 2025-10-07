#!/usr/bin/env python3
"""
Simple test to verify the questions API works with the new database
"""
from flask import Flask, jsonify, request
from models import db, Question, Difficulty, Category
import json
import random

# Create simple Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/benh/Documents/PythonTrivia/instance/trivia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

# Initialize database
db.init_app(app)

@app.route('/test-questions')
def test_questions():
    """Simple test endpoint for questions"""
    try:
        # Get parameters
        difficulty_input = request.args.get('difficulty', 'easy')
        limit = int(request.args.get('limit', '3'))
        
        # Security check
        dangerous_patterns = ["'", '"', ';', '--', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION', 'SELECT']
        if any(pattern in difficulty_input.upper() for pattern in dangerous_patterns):
            return jsonify({'error': 'Invalid characters in difficulty parameter'}), 400
        
        # Convert to enum
        difficulty_enum = None
        for d in Difficulty:
            if d.value.lower() == difficulty_input.lower():
                difficulty_enum = d
                break
        
        if not difficulty_enum:
            return jsonify({'error': f'Invalid difficulty: {difficulty_input}'}), 400
        
        # Query questions
        questions = Question.query.filter_by(
            difficulty=difficulty_enum, 
            is_active=True
        ).all()
        
        if not questions:
            return jsonify({'error': 'No questions found'}), 404
        
        # Randomize and limit
        random.shuffle(questions)
        selected = questions[:limit]
        
        # Format response
        questions_data = []
        for q in selected:
            questions_data.append({
                'id': q.id,
                'question': q.question_text,
                'choices': json.loads(q.choices),
                'category': q.category.value,
                'difficulty': q.difficulty.value
            })
        
        return jsonify({
            'questions': questions_data,
            'count': len(questions_data),
            'difficulty': difficulty_input
        })
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        # Test the endpoint
        with app.test_client() as client:
            print("🧪 Testing simple questions endpoint...")
            
            # Test each difficulty
            for difficulty in ['easy', 'medium', 'hard']:
                print(f"\n📝 Testing {difficulty} questions:")
                response = client.get(f'/test-questions?difficulty={difficulty}&limit=3')
                
                if response.status_code == 200:
                    data = response.get_json()
                    questions = data.get('questions', [])
                    print(f"  ✅ Retrieved {len(questions)} questions")
                    
                    for i, q in enumerate(questions):
                        print(f"  Q{i+1}: {q['question'][:50]}...")
                        print(f"       Difficulty: {q['difficulty']}, Choices: {len(q['choices'])}")
                else:
                    print(f"  ❌ Error: {response.status_code} - {response.get_data(as_text=True)}")
            
            # Test security
            print(f"\n🔒 Testing security (SQL injection):")
            response = client.get("/test-questions?difficulty='; DROP TABLE users; --")
            print(f"  Status: {response.status_code} (should be 400)")
            if response.status_code == 400:
                print("  ✅ Security check passed")
            else:
                print("  ❌ Security check failed")