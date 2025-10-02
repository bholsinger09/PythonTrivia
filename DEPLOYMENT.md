# Deployment Guide for Python Trivia Game

This document provides step-by-step instructions for deploying the Python Trivia Game to various platforms.

## 🚀 Quick Deploy Options

### Option 1: Heroku (Recommended for beginners)

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-trivia-game-name
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

4. **Open your app**
   ```bash
   heroku open
   ```

### Option 2: Railway (Modern alternative)

1. **Connect to Railway**
   - Visit [railway.app](https://railway.app)
   - Connect your GitHub account
   - Select your PythonTrivia repository

2. **Deploy**
   - Railway will automatically detect the `railway.json` config
   - Click "Deploy" and wait for build completion
   - Your app will be live at the provided URL

### Option 3: Render (Free tier available)

1. **Connect to Render**
   - Visit [render.com](https://render.com)
   - Connect your GitHub account
   - Create a new Web Service

2. **Configure**
   - Repository: `bholsinger09/PythonTrivia`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
   - Environment: `Production`

### Option 4: Docker Deployment

1. **Build and run locally**
   ```bash
   docker build -t python-trivia .
   docker run -p 5001:5001 python-trivia
   ```

2. **Or use Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Deploy to any cloud provider that supports Docker**
   - AWS ECS/Fargate
   - Google Cloud Run
   - Azure Container Instances
   - DigitalOcean App Platform

## 🔧 Environment Variables

Set these environment variables in your deployment platform:

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `5001` | Port number (Heroku sets this automatically) |
| `FLASK_ENV` | `production` | Flask environment |
| `FLASK_DEBUG` | `False` | Disable debug mode in production |

## 🧪 Testing Deployed Application

After deployment, verify your app works by:

1. **Manual Testing**
   - Visit your deployed URL
   - Test card flipping functionality
   - Try navigation between cards
   - Test score tracking

2. **API Testing**
   ```bash
   # Replace YOUR_DEPLOYED_URL with your actual URL
   curl https://YOUR_DEPLOYED_URL/api/current-card
   curl -X POST https://YOUR_DEPLOYED_URL/api/flip-card
   ```

## 🔒 Production Considerations

### Security
- The app uses Flask's built-in security features
- No sensitive data is stored or transmitted
- All user interactions are client-side or stateless API calls

### Performance
- Gunicorn serves the app with multiple workers
- Static files are served efficiently
- API responses are optimized for speed

### Monitoring
- Check application logs for errors
- Monitor response times
- Set up health checks (all platforms support `/` endpoint)

## 🐛 Troubleshooting

### Common Issues

**Port binding errors:**
- Make sure your platform uses the `PORT` environment variable
- Heroku automatically sets this

**Import errors:**
- Verify all dependencies are in `requirements.txt`
- Check Python version compatibility

**Static files not loading:**
- Ensure Flask's static file serving is working
- Check that CSS/JS files are in the correct directories

### Platform-Specific Tips

**Heroku:**
- Free tier sleeps after 30 minutes of inactivity
- Use `heroku logs --tail` to view real-time logs
- Restart with `heroku restart`

**Railway:**
- Automatic HTTPS is provided
- Custom domains available on paid plans
- Built-in metrics and monitoring

**Render:**
- Free tier has limitations but includes HTTPS
- Automatic deploys on git push
- Built-in monitoring dashboard

## 📈 Scaling

For high traffic, consider:

1. **Database Integration**
   - Add PostgreSQL for question storage
   - Implement user accounts and progress tracking

2. **Caching**
   - Add Redis for session management
   - Cache frequently accessed questions

3. **CDN**
   - Use a CDN for static assets
   - Enable compression

4. **Load Balancing**
   - Multiple application instances
   - Database connection pooling

## 🎯 Next Steps

After successful deployment:
- Add monitoring and analytics
- Implement user feedback system
- Add more question categories
- Consider mobile app development
- Set up automated testing in CI/CD

---

**Happy Deploying! 🚀**