# 🚀 Deployment Guide

## Environment Variables Setup

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Get your API key from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Paths (can be left as defaults)
UPLOAD_DIR=uploads
VECTOR_DB_PATH=vector_db

# Text Splitting Configuration (can be left as defaults)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Model Configuration (can be left as defaults)
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0.7

# Environment
ENVIRONMENT=production
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# Backend API URL (change to your deployed backend URL)
NEXT_PUBLIC_API_URL=https://your-backend-url.com

# Environment
NODE_ENV=production
```

## Deployment Options

### 1. Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Environment variables configured

#### Steps

1. **Clone and setup:**
```bash
git clone https://github.com/yourusername/ai-chatbot.git
cd ai-chatbot
```

2. **Configure environment variables:**
```bash
# Copy example files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit the files with your actual values
```

3. **Deploy with Docker Compose:**
```bash
docker-compose up -d
```

4. **Access your application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. Vercel + Railway/Render Deployment

#### Frontend (Vercel)

1. **Connect your GitHub repo to Vercel**
2. **Configure environment variables in Vercel dashboard:**
   - `NEXT_PUBLIC_API_URL`: Your backend URL
   - `NODE_ENV`: production

3. **Deploy** - Vercel will automatically deploy on push

#### Backend (Railway/Render)

1. **Connect your GitHub repo to Railway/Render**
2. **Configure environment variables:**
   - `GROQ_API_KEY`: Your Groq API key
   - `ENVIRONMENT`: production

3. **Deploy** - Platform will build and deploy

### 3. Traditional VPS Deployment

#### Backend Setup

```bash
# Clone repo
git clone https://github.com/yourusername/ai-chatbot.git
cd ai-chatbot/backend

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your values

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
# Edit .env.local with your backend URL

# Build for production
npm run build

# Start production server
npm start
```

## Production Considerations

### Security

1. **API Keys**: Never commit API keys to Git
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure CORS properly for your domain
4. **Rate Limiting**: Consider adding rate limiting to API endpoints

### Performance

1. **CDN**: Use CDN for frontend assets
2. **Database**: Consider using managed database for persistence
3. **Monitoring**: Add logging and monitoring
4. **Scaling**: Configure auto-scaling based on traffic

### Environment Variable Safety

- ✅ `.env` files are in `.gitignore` - won't be committed
- ✅ Use `.env.example` as template
- ✅ Configure environment variables in deployment platform
- ✅ Use different values for development/staging/production

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure GROQ_API_KEY is correctly set
   - Check for typos in environment variable names

2. **CORS Errors**:
   - Update CORS origins in backend to include your frontend URL
   - Ensure environment variables are properly loaded

3. **Build Failures**:
   - Check all required environment variables are set
   - Verify dependencies are compatible with production environment

4. **Session Storage Issues**:
   - Ensure temporary directories have proper permissions
   - Monitor disk usage for temporary files

### Monitoring

Add these endpoints for health checks:
- `GET /health` - Backend health check
- `GET /api/session/test` - Session status check

## Support

For deployment issues:
1. Check logs: `docker-compose logs backend` or `docker-compose logs frontend`
2. Verify environment variables: `docker-compose exec backend env`
3. Test API endpoints: Visit `/docs` for API documentation

---

**Note**: This application uses session-based storage, so uploaded documents are automatically cleared after 30 minutes or when the server restarts. This ensures privacy and prevents data accumulation.
