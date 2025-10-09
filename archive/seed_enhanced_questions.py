#!/usr/bin/env python3
"""
Enhanced Question Seeder for Python Trivia Game
Adds 20 questions each for Easy, Medium, and Hard difficulty levels
Questions are properly categorized and will be randomized during gameplay
"""
import json
from app import app
from models import db, Question, Difficulty, Category

def create_question(question_text, choices, correct_index, category, difficulty, explanation=""):
    """Helper function to create a question"""
    return Question(
        question_text=question_text,
        correct_answer=choices[correct_index],
        choices=json.dumps(choices),
        correct_choice_index=correct_index,
        explanation=explanation,
        category=category,
        difficulty=difficulty,
        is_active=True
    )

def seed_easy_questions():
    """Add 20 Easy difficulty questions"""
    easy_questions = [
        {
            "question": "What is the correct way to create a comment in Python?",
            "choices": ["// This is a comment", "<!-- This is a comment -->", "# This is a comment", "/* This is a comment */"],
            "correct": 2,
            "category": Category.BASICS,
            "explanation": "Python uses the # symbol for single-line comments"
        },
        {
            "question": "Which of the following is the correct way to create a variable in Python?",
            "choices": ["int x = 5", "var x = 5", "x = 5", "declare x = 5"],
            "correct": 2,
            "category": Category.BASICS,
            "explanation": "Python uses dynamic typing, so you just assign a value to a variable name"
        },
        {
            "question": "What data type is the result of: len('Hello')?",
            "choices": ["string", "float", "integer", "boolean"],
            "correct": 2,
            "category": Category.BASICS,
            "explanation": "The len() function returns an integer representing the length"
        },
        {
            "question": "Which keyword is used to create a function in Python?",
            "choices": ["function", "def", "func", "define"],
            "correct": 1,
            "category": Category.FUNCTIONS,
            "explanation": "The 'def' keyword is used to define functions in Python"
        },
        {
            "question": "What is the output of: print(type(5.0))?",
            "choices": ["<class 'int'>", "<class 'float'>", "<class 'number'>", "<class 'decimal'>"],
            "correct": 1,
            "category": Category.BASICS,
            "explanation": "5.0 is a floating-point number, so type() returns <class 'float'>"
        },
        {
            "question": "Which operator is used for exponentiation in Python?",
            "choices": ["^", "**", "exp", "pow"],
            "correct": 1,
            "category": Category.BASICS,
            "explanation": "Python uses ** for exponentiation (e.g., 2**3 = 8)"
        },
        {
            "question": "How do you create an empty list in Python?",
            "choices": ["list = empty", "list = []", "list = new List()", "list = null"],
            "correct": 1,
            "category": Category.DATA_STRUCTURES,
            "explanation": "Empty lists are created using square brackets: []"
        },
        {
            "question": "What is the correct way to import the math module?",
            "choices": ["include math", "import math", "using math", "require math"],
            "correct": 1,
            "category": Category.LIBRARIES,
            "explanation": "Python uses the 'import' keyword to import modules"
        },
        {
            "question": "Which method is used to add an element to the end of a list?",
            "choices": ["add()", "insert()", "append()", "push()"],
            "correct": 2,
            "category": Category.DATA_STRUCTURES,
            "explanation": "The append() method adds an element to the end of a list"
        },
        {
            "question": "What is the result of: 'Hello' + 'World'?",
            "choices": ["HelloWorld", "Hello World", "Hello+World", "Error"],
            "correct": 0,
            "category": Category.BASICS,
            "explanation": "String concatenation with + joins strings directly without spaces"
        },
        {
            "question": "Which of these is NOT a valid Python variable name?",
            "choices": ["my_var", "_private", "2variable", "Variable"],
            "correct": 2,
            "category": Category.BASICS,
            "explanation": "Variable names cannot start with a number"
        },
        {
            "question": "What does the range(5) function return?",
            "choices": ["[1, 2, 3, 4, 5]", "[0, 1, 2, 3, 4]", "[0, 1, 2, 3, 4, 5]", "5"],
            "correct": 1,
            "category": Category.FUNCTIONS,
            "explanation": "range(5) returns numbers from 0 to 4 (5 numbers total)"
        },
        {
            "question": "How do you get user input in Python?",
            "choices": ["get()", "input()", "read()", "scan()"],
            "correct": 1,
            "category": Category.FUNCTIONS,
            "explanation": "The input() function is used to get user input"
        },
        {
            "question": "What is the correct syntax for an if statement in Python?",
            "choices": ["if x == 5:", "if (x == 5):", "if x = 5:", "if x == 5 then:"],
            "correct": 0,
            "category": Category.BASICS,
            "explanation": "Python if statements use 'if condition:' syntax with a colon"
        },
        {
            "question": "Which of these creates a dictionary in Python?",
            "choices": ["{key: value}", "[key: value]", "(key: value)", "key: value"],
            "correct": 0,
            "category": Category.DATA_STRUCTURES,
            "explanation": "Dictionaries are created using curly braces with key:value pairs"
        },
        {
            "question": "What is the output of: len([1, 2, 3])?",
            "choices": ["2", "3", "4", "Error"],
            "correct": 1,
            "category": Category.DATA_STRUCTURES,
            "explanation": "The list has 3 elements, so len() returns 3"
        },
        {
            "question": "Which loop is used to iterate over a sequence in Python?",
            "choices": ["while", "for", "do-while", "foreach"],
            "correct": 1,
            "category": Category.BASICS,
            "explanation": "The 'for' loop is commonly used to iterate over sequences"
        },
        {
            "question": "What is the correct way to define a string in Python?",
            "choices": ["'Hello'", "\"Hello\"", "Both 'Hello' and \"Hello\"", "String('Hello')"],
            "correct": 2,
            "category": Category.BASICS,
            "explanation": "Python accepts both single and double quotes for strings"
        },
        {
            "question": "What does the print() function do?",
            "choices": ["Returns a value", "Displays output to console", "Creates a variable", "Imports a module"],
            "correct": 1,
            "category": Category.FUNCTIONS,
            "explanation": "print() displays output to the console/terminal"
        },
        {
            "question": "Which symbol is used for indentation in Python?",
            "choices": ["Tabs only", "Spaces only", "Both tabs and spaces", "Curly braces"],
            "correct": 2,
            "category": Category.BASICS,
            "explanation": "Python accepts both tabs and spaces for indentation (but be consistent!)"
        }
    ]
    
    questions = []
    for q in easy_questions:
        questions.append(create_question(
            q["question"], q["choices"], q["correct"], 
            q["category"], Difficulty.EASY, q["explanation"]
        ))
    return questions

def seed_medium_questions():
    """Add 20 Medium difficulty questions"""
    medium_questions = [
        {
            "question": "What is the difference between '==' and 'is' in Python?",
            "choices": ["No difference", "'==' compares values, 'is' compares identity", "'is' compares values, '==' compares identity", "Both compare identity"],
            "correct": 1,
            "category": Category.BASICS,
            "explanation": "'==' compares values for equality, 'is' checks if objects are the same instance"
        },
        {
            "question": "What is the output of: [1, 2, 3] + [4, 5, 6]?",
            "choices": ["[1, 2, 3, 4, 5, 6]", "[5, 7, 9]", "Error", "[1, 2, 3] [4, 5, 6]"],
            "correct": 0,
            "category": Category.DATA_STRUCTURES,
            "explanation": "The + operator concatenates lists in Python"
        },
        {
            "question": "Which method is used to remove the last element from a list?",
            "choices": ["remove()", "delete()", "pop()", "clear()"],
            "correct": 2,
            "category": Category.DATA_STRUCTURES,
            "explanation": "pop() removes and returns the last element of a list"
        },
        {
            "question": "What is a lambda function in Python?",
            "choices": ["A named function", "An anonymous function", "A class method", "A built-in function"],
            "correct": 1,
            "category": Category.FUNCTIONS,
            "explanation": "Lambda functions are anonymous functions defined inline"
        },
        {
            "question": "What does the enumerate() function return?",
            "choices": ["Only indices", "Only values", "Tuples of (index, value)", "A dictionary"],
            "correct": 2,
            "category": Category.FUNCTIONS,
            "explanation": "enumerate() returns tuples containing index and value pairs"
        },
        {
            "question": "What is the purpose of the __init__ method in a Python class?",
            "choices": ["To delete objects", "To initialize objects", "To define static methods", "To inherit from parent"],
            "correct": 1,
            "category": Category.OOP,
            "explanation": "__init__ is the constructor method used to initialize new objects"
        },
        {
            "question": "What is the output of: {'a': 1, 'b': 2}.get('c', 0)?",
            "choices": ["Error", "None", "0", "'c'"],
            "correct": 2,
            "category": Category.DATA_STRUCTURES,
            "explanation": "dict.get() returns the default value (0) when the key doesn't exist"
        },
        {
            "question": "Which of these is a mutable data type in Python?",
            "choices": ["tuple", "string", "list", "int"],
            "correct": 2,
            "category": Category.DATA_STRUCTURES,
            "explanation": "Lists are mutable (can be changed), while tuples and strings are immutable"
        },
        {
            "question": "What does the zip() function do?",
            "choices": ["Compresses files", "Combines multiple iterables", "Sorts lists", "Filters elements"],
            "correct": 1,
            "category": Category.FUNCTIONS,
            "explanation": "zip() combines multiple iterables element-wise into tuples"
        },
        {
            "question": "What is the correct way to handle exceptions in Python?",
            "choices": ["catch/finally", "try/except", "handle/error", "attempt/rescue"],
            "correct": 1,
            "category": Category.BASICS,
            "explanation": "Python uses try/except blocks for exception handling"
        },
        {
            "question": "What does list comprehension [x**2 for x in range(3)] produce?",
            "choices": ["[0, 1, 4]", "[1, 4, 9]", "[0, 1, 2]", "[1, 2, 3]"],
            "correct": 0,
            "category": Category.DATA_STRUCTURES,
            "explanation": "This squares each number: 0²=0, 1²=1, 2²=4"
        },
        {
            "question": "What is the difference between append() and extend() for lists?",
            "choices": ["No difference", "append() adds one element, extend() adds multiple", "extend() adds one element, append() adds multiple", "Both add multiple elements"],
            "correct": 1,
            "category": Category.DATA_STRUCTURES,
            "explanation": "append() adds a single element, extend() adds all elements from an iterable"
        },
        {
            "question": "What is the purpose of the 'self' parameter in Python class methods?",
            "choices": ["It's optional", "It refers to the class", "It refers to the instance", "It's a keyword"],
            "correct": 2,
            "category": Category.OOP,
            "explanation": "'self' refers to the instance of the class calling the method"
        },
        {
            "question": "What does the map() function do?",
            "choices": ["Creates dictionaries", "Applies a function to all items in an iterable", "Sorts sequences", "Filters elements"],
            "correct": 1,
            "category": Category.FUNCTIONS,
            "explanation": "map() applies a given function to each item in an iterable"
        },
        {
            "question": "What is the output of: 'hello'.capitalize()?",
            "choices": ["'HELLO'", "'Hello'", "'hello'", "'HeLLo'"],
            "correct": 1,
            "category": Category.BASICS,
            "explanation": "capitalize() makes the first character uppercase and the rest lowercase"
        },
        {
            "question": "Which keyword is used to create a class in Python?",
            "choices": ["class", "def", "object", "new"],
            "correct": 0,
            "category": Category.OOP,
            "explanation": "The 'class' keyword is used to define classes in Python"
        },
        {
            "question": "What does the filter() function do?",
            "choices": ["Sorts elements", "Removes all elements", "Returns elements that satisfy a condition", "Modifies elements"],
            "correct": 2,
            "category": Category.FUNCTIONS,
            "explanation": "filter() returns elements from an iterable that satisfy a given condition"
        },
        {
            "question": "What is the difference between a list and a tuple in Python?",
            "choices": ["No difference", "Lists are mutable, tuples are immutable", "Tuples are mutable, lists are immutable", "Lists use [], tuples use ()"],
            "correct": 1,
            "category": Category.DATA_STRUCTURES,
            "explanation": "Lists can be modified (mutable), tuples cannot be modified (immutable)"
        },
        {
            "question": "What does the len() function return for a dictionary?",
            "choices": ["Number of keys", "Number of values", "Number of key-value pairs", "Total characters"],
            "correct": 2,
            "category": Category.DATA_STRUCTURES,
            "explanation": "len() returns the number of key-value pairs in a dictionary"
        },
        {
            "question": "What is the purpose of the pass statement in Python?",
            "choices": ["To skip execution", "To create a placeholder", "To return None", "To raise an error"],
            "correct": 1,
            "category": Category.BASICS,
            "explanation": "pass is a null operation used as a placeholder where syntax requires a statement"
        }
    ]
    
    questions = []
    for q in medium_questions:
        questions.append(create_question(
            q["question"], q["choices"], q["correct"], 
            q["category"], Difficulty.MEDIUM, q["explanation"]
        ))
    return questions

def seed_hard_questions():
    """Add 20 Hard difficulty questions"""
    hard_questions = [
        {
            "question": "What is the output of: print(*[1, 2, 3], sep='-')?",
            "choices": ["1-2-3", "[1, 2, 3]", "1 2 3", "Error"],
            "correct": 0,
            "category": Category.ADVANCED,
            "explanation": "The * operator unpacks the list, and sep='-' sets the separator"
        },
        {
            "question": "What is a decorator in Python?",
            "choices": ["A design pattern", "A function that modifies another function", "A class method", "A built-in type"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "Decorators are functions that modify or enhance other functions"
        },
        {
            "question": "What does the __name__ == '__main__' check do?",
            "choices": ["Checks if file is imported", "Checks if file is run directly", "Checks for syntax errors", "Checks Python version"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "This checks if the script is being run directly (not imported)"
        },
        {
            "question": "What is the difference between __str__ and __repr__ methods?",
            "choices": ["No difference", "__str__ for users, __repr__ for developers", "__repr__ for users, __str__ for developers", "Both are the same"],
            "correct": 1,
            "category": Category.OOP,
            "explanation": "__str__ is for end-users, __repr__ is for developers and debugging"
        },
        {
            "question": "What does the yield keyword do in Python?",
            "choices": ["Returns a value", "Creates a generator", "Defines a variable", "Imports a module"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "yield creates a generator function that can pause and resume execution"
        },
        {
            "question": "What is the Global Interpreter Lock (GIL) in Python?",
            "choices": ["A security feature", "A mechanism that prevents true parallelism", "A memory manager", "A syntax checker"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "GIL allows only one thread to execute Python bytecode at a time"
        },
        {
            "question": "What does the @property decorator do?",
            "choices": ["Creates a class", "Makes a method behave like an attribute", "Defines a static method", "Creates a private variable"],
            "correct": 1,
            "category": Category.OOP,
            "explanation": "@property allows method access like an attribute with dot notation"
        },
        {
            "question": "What is the difference between deep copy and shallow copy?",
            "choices": ["No difference", "Deep copy copies all levels, shallow copy copies one level", "Shallow copy copies all levels, deep copy copies one level", "Both copy everything"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "Deep copy creates independent copies at all levels, shallow copy only at the first level"
        },
        {
            "question": "What does the __slots__ attribute do in a Python class?",
            "choices": ["Defines methods", "Restricts attributes and saves memory", "Creates inheritance", "Defines constructors"],
            "correct": 1,
            "category": Category.OOP,
            "explanation": "__slots__ restricts instance attributes and can save memory"
        },
        {
            "question": "What is the purpose of the with statement in Python?",
            "choices": ["Loop control", "Context management", "Exception handling", "Function definition"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "with statement provides context management for resource handling"
        },
        {
            "question": "What does the collections.defaultdict do?",
            "choices": ["Creates empty dictionaries", "Provides default values for missing keys", "Sorts dictionary keys", "Validates dictionary values"],
            "correct": 1,
            "category": Category.LIBRARIES,
            "explanation": "defaultdict automatically creates default values for missing keys"
        },
        {
            "question": "What is the difference between @staticmethod and @classmethod?",
            "choices": ["No difference", "@staticmethod gets class, @classmethod gets instance", "@classmethod gets class, @staticmethod gets neither", "Both get instance"],
            "correct": 2,
            "category": Category.OOP,
            "explanation": "@classmethod receives the class as first argument, @staticmethod receives neither class nor instance"
        },
        {
            "question": "What does functools.wraps do in decorator functions?",
            "choices": ["Creates functions", "Preserves original function metadata", "Adds parameters", "Handles exceptions"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "functools.wraps preserves the original function's metadata like __name__ and __doc__"
        },
        {
            "question": "What is the purpose of the __call__ method in Python classes?",
            "choices": ["Calls other methods", "Makes instances callable like functions", "Inherits from parent", "Defines constructors"],
            "correct": 1,
            "category": Category.OOP,
            "explanation": "__call__ allows class instances to be called like functions"
        },
        {
            "question": "What does the itertools.chain function do?",
            "choices": ["Creates chains", "Flattens iterables into a single iterator", "Sorts iterables", "Filters iterables"],
            "correct": 1,
            "category": Category.LIBRARIES,
            "explanation": "itertools.chain creates an iterator that returns elements from multiple iterables sequentially"
        },
        {
            "question": "What is the difference between __new__ and __init__ methods?",
            "choices": ["No difference", "__new__ creates instance, __init__ initializes it", "__init__ creates instance, __new__ initializes it", "Both do the same"],
            "correct": 1,
            "category": Category.OOP,
            "explanation": "__new__ creates the instance, __init__ initializes it after creation"
        },
        {
            "question": "What does the asyncio library provide in Python?",
            "choices": ["Synchronous programming", "Asynchronous programming support", "File operations", "Math functions"],
            "correct": 1,
            "category": Category.LIBRARIES,
            "explanation": "asyncio provides infrastructure for asynchronous programming using async/await"
        },
        {
            "question": "What is a metaclass in Python?",
            "choices": ["A parent class", "A class that creates classes", "A method type", "A variable type"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "A metaclass is a class whose instances are classes themselves"
        },
        {
            "question": "What does the weakref module provide?",
            "choices": ["Strong references", "Weak references that don't prevent garbage collection", "Reference counting", "Memory allocation"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "weakref creates references that don't prevent objects from being garbage collected"
        },
        {
            "question": "What is the purpose of the __enter__ and __exit__ methods?",
            "choices": ["Loop control", "Context manager protocol", "Exception handling", "Inheritance"],
            "correct": 1,
            "category": Category.ADVANCED,
            "explanation": "__enter__ and __exit__ implement the context manager protocol for use with 'with' statements"
        }
    ]
    
    questions = []
    for q in hard_questions:
        questions.append(create_question(
            q["question"], q["choices"], q["correct"], 
            q["category"], Difficulty.HARD, q["explanation"]
        ))
    return questions

def main():
    """Seed the database with comprehensive questions"""
    with app.app_context():
        print("🌱 Starting enhanced question seeding...")
        
        # Check if questions already exist
        existing_count = Question.query.count()
        if existing_count > 0:
            print(f"Found {existing_count} existing questions.")
            response = input("Do you want to clear existing questions and reseed? (y/n): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
            
            print("Clearing existing questions...")
            Question.query.delete()
            db.session.commit()
        
        # Seed questions by difficulty
        print("\n📚 Adding Easy questions (20)...")
        easy_questions = seed_easy_questions()
        for q in easy_questions:
            db.session.add(q)
        
        print("📖 Adding Medium questions (20)...")
        medium_questions = seed_medium_questions()
        for q in medium_questions:
            db.session.add(q)
        
        print("📕 Adding Hard questions (20)...")
        hard_questions = seed_hard_questions()
        for q in hard_questions:
            db.session.add(q)
        
        # Commit all changes
        print("\n💾 Saving to database...")
        db.session.commit()
        
        # Verify seeding
        print("\n✅ Seeding complete! Summary:")
        for difficulty in Difficulty:
            if difficulty != Difficulty.EXPERT:  # Skip expert for now
                count = Question.query.filter_by(difficulty=difficulty).count()
                print(f"  {difficulty.value.title()}: {count} questions")
        
        total = Question.query.count()
        print(f"  Total: {total} questions")
        
        print("\n🎯 Questions are now properly categorized and will be randomized during gameplay!")

if __name__ == "__main__":
    main()