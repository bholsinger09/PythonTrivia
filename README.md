# Python Trivia Flip Card Game

A comprehensive Python trivia game built with Flask, featuring database-backed user authentication, persistent game sessions, interactive leaderboards, and extensive test coverage.

## ✨ Features

### 🎮 Core Game Features
- **Interactive Flip Cards**: Smooth CSS animations for card flipping
- **Multiple Choice Questions**: A/B answer selection with instant feedback
- **Multiple Categories**: Basics, Data Structures, Functions, OOP, Libraries, Advanced
- **Difficulty Levels**: Easy, Medium, Hard questions with adaptive scoring
- **Real-time Progress**: Live score tracking and accuracy calculation

### 👤 User Management
- **User Authentication**: Secure registration and login with bcrypt password hashing
- **User Profiles**: Comprehensive dashboards with statistics and achievements
- **Session Persistence**: Game progress saved across browser sessions
- **Anonymous Play**: Play without registration with session tracking

### 🏆 Competitive Features
- **Interactive Leaderboards**: Real-time rankings with filtering by category/difficulty
- **Achievement System**: Unlock badges for various milestones
- **Game History**: Track all past games and performance trends
- **Score Statistics**: Detailed analytics on accuracy, streaks, and improvement

### 🛠️ Technical Features
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **RESTful API**: Complete API for all game operations
- **Responsive Design**: Mobile-first design that works on all devices
- **Test Automation**: Comprehensive Selenium test suite
- **Production Ready**: Configured for deployment on Render and Heroku

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Chrome browser (for Selenium tests)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bholsinger09/PythonTrivia.git
   cd PythonTrivia
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_db.py init
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5001`

### Demo Account
- **Username**: `admin`
- **Password**: `admin123`

## 🎮 How to Play

1. **Start the Game**: Click "Start Playing" on the home page
2. **Read the Question**: Each card shows a Python trivia question
3. **Flip the Card**: Click "Show Answer" or press Spacebar
4. **Mark Your Answer**: Click "Correct" or "Incorrect" based on your knowledge
5. **Navigate**: Use arrow keys or navigation buttons to move between cards
6. **Track Progress**: Monitor your score and accuracy in real-time

### Keyboard Controls

- **Space/Enter**: Flip current card
- **Left Arrow**: Previous card
- **Right Arrow**: Next card
- **1**: Mark as correct (when card is flipped)
- **2**: Mark as incorrect (when card is flipped)
- **R**: Reset game

## 🚀 Deployment

Ready to deploy your trivia game? We've got you covered with multiple deployment options:

### Quick Deploy (One-Click Options)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/bholsinger09/PythonTrivia)

### Manual Deployment

Choose your preferred platform:

- **🔥 Heroku** - Perfect for beginners, free tier available
- **🎨 Render** - Free tier with built-in CI/CD (Currently deployed)
- **🐳 Docker** - Deploy anywhere with container support

**Detailed instructions:** See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

### Production Environment Variables

```bash
PORT=5001                    # Port number
FLASK_ENV=production        # Flask environment
FLASK_DEBUG=False          # Disable debug mode
```

## 🧪 Testing

This project includes comprehensive test automation with Selenium.

### Running Tests

**Run all tests:**
```bash
./run_tests.sh
```

**Run specific test types:**
```bash
./run_tests.sh smoke      # Quick validation tests
./run_tests.sh ui         # User interface tests
./run_tests.sh api        # API endpoint tests
./run_tests.sh integration # Full integration tests
```

**Run tests in headless mode:**
```bash
HEADLESS=true ./run_tests.sh
```

### Test Categories

- **Smoke Tests**: Basic functionality validation
- **UI Tests**: User interface and interaction testing
- **API Tests**: Backend API endpoint testing
- **Integration Tests**: End-to-end workflow testing

### Test Reports

After running tests, reports are generated in the `reports/` directory:
- `reports/test-report.html` - Detailed test results
- `reports/coverage/` - Code coverage reports
- `reports/screenshots/` - Screenshots of test failures

## 📁 Project Structure

```
PythonTrivia/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── pyproject.toml        # pytest configuration
├── run_tests.sh          # Test automation script
├── src/
│   └── models.py         # Game logic and data models
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── game.html         # Game interface
│   ├── categories.html   # Categories page
│   └── difficulty.html   # Difficulty levels page
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       ├── app.js        # Core application JavaScript
│       └── game.js       # Game-specific JavaScript
└── tests/
    ├── conftest.py       # Test configuration and fixtures
    ├── test_home_page.py # Home page tests
    ├── test_game_functionality.py # Game logic tests
    └── test_api_endpoints.py # API tests
```

## 🔧 API Endpoints

The game provides a RESTful API for all operations:

### Game State
- `GET /api/current-card` - Get current card data
- `GET /api/game-stats` - Get game statistics

### Game Actions
- `POST /api/flip-card` - Flip the current card
- `POST /api/answer-card` - Mark answer as correct/incorrect
- `POST /api/next-card` - Move to next card
- `POST /api/previous-card` - Move to previous card
- `POST /api/reset-game` - Reset the game

### Example API Usage

```javascript
// Flip current card
fetch('/api/flip-card', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log(data));

// Answer correctly
fetch('/api/answer-card', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ correct: true })
});
```

## 🎨 Customization

### Adding New Questions

Edit the `load_sample_questions()` function in `app.py`:

```python
sample_questions.append(
    TriviaQuestion(
        "Your question here?",
        "Your answer here",
        Category.BASICS,  # Choose appropriate category
        Difficulty.EASY,  # Choose difficulty level
        "Optional explanation here"
    )
)
```

### Categories and Difficulties

Categories are defined in `src/models.py`:
- `BASICS` - Python fundamentals
- `DATA_STRUCTURES` - Lists, dicts, sets, etc.
- `FUNCTIONS` - Function-related concepts
- `OOP` - Object-oriented programming
- `LIBRARIES` - Python libraries and frameworks
- `ADVANCED` - Advanced Python concepts

Difficulty levels:
- `EASY` - Beginner level
- `MEDIUM` - Intermediate level
- `HARD` - Advanced level

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add your changes and tests
4. Run the test suite (`./run_tests.sh`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Add tests for new features
- Maintain test coverage above 80%
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update documentation for new features

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill existing Flask processes
pkill -f "python app.py"
# Or use a different port
python app.py --port 5001
```

**Chrome driver issues:**
```bash
# Update Chrome driver
pip install --upgrade webdriver-manager
```

**Test failures:**
```bash
# Run tests with verbose output
./run_tests.sh -v

# Check Flask logs
tail -f flask.log
```

**Permission denied on run_tests.sh:**
```bash
chmod +x run_tests.sh
```

## 📈 Performance

- **Page Load Time**: < 2 seconds
- **API Response Time**: < 100ms average
- **Test Suite Runtime**: ~2-5 minutes (depending on browser startup)
- **Memory Usage**: ~50MB for Flask app

## 🔒 Security

- Input validation on all API endpoints
- CSRF protection with Flask's built-in features
- No sensitive data storage
- Safe HTML rendering with Jinja2 auto-escaping

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have questions or need help:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the test reports for error details
3. Open an issue on GitHub
4. Contact the development team

## 🚀 Future Enhancements

- [ ] User authentication and progress tracking
- [ ] Multiplayer mode
- [ ] Question difficulty adaptation based on performance
- [ ] More question categories (Django, Data Science, etc.)
- [ ] Mobile app version
- [ ] Question submission by users
- [ ] Leaderboards and achievements
- [ ] Timer-based challenges

---

**Happy Learning! 🐍📚**