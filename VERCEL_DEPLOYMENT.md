# 🚀 Vercel Deployment Guide

## Overview

This guide will help you deploy both frontend and backend to Vercel using serverless functions.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Groq API Key**: Get from [console.groq.com](https://console.groq.com)

## Step 1: Configure Environment Variables

### In Vercel Dashboard

1. Go to your Vercel project settings
2. Add these environment variables:

**Backend Environment Variables:**
```
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=production
PYTHONPATH=/vercel/path0/backend
```

**Frontend Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://your-app-name.vercel.app
NODE_ENV=production
```

## Step 2: Deploy to Vercel

### Option A: Through Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel --prod
```

### Option B: Through GitHub Integration

1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the configuration
3. Configure environment variables in Vercel dashboard
4. Deploy on push to main branch

## Step 3: Testing the Deployment

### Using Chrome DevTools

1. **Open your deployed application**
2. **Open Chrome DevTools** (F12)
3. **Go to Network tab**
4. **Test Document Upload**:
   - Upload a PDF file
   - Check network requests in DevTools
   - Verify: `POST /api/documents/upload` returns 200

5. **Test Chat Functionality**:
   - Ask a question about uploaded document
   - Check: `POST /api/chat/ask` returns response
   - Verify response contains AI answer and sources

6. **Test Session Management**:
   - Visit: `GET /api/session/test`
   - Verify session ID and temp directory info
   - Test: `POST /api/session/new` creates new session

### Expected Network Requests

```
✅ GET /api/session/test - Session info
✅ POST /api/documents/upload - Document upload
✅ POST /api/chat/ask - Question answering
✅ POST /api/session/new - New session creation
```

### Console Logs to Check

```javascript
// In browser console, these should work:
fetch('/api/session/test').then(r => r.json()).then(console.log)
fetch('/api/health').then(r => r.json()).then(console.log)
```

## Step 4: Troubleshooting

### Common Issues

#### 1. **500 Server Error**
**Check**: Vercel Function Logs
- Go to Vercel dashboard → Functions tab
- Look for error messages in function logs
- Common causes: Missing environment variables, import errors

#### 2. **CORS Errors**
**Check**: API URL configuration
- Ensure `NEXT_PUBLIC_API_URL` is set correctly
- Verify CORS middleware in backend

#### 3. **Upload Failures**
**Check**: File size limits
- Vercel functions have 4.5MB payload limit
- For larger files, consider Vercel Blob storage

#### 4. **Session Storage Issues**
**Check**: Temporary directory permissions
- Session storage uses `/tmp` in Vercel
- Verify cleanup functions work properly

### Debugging Commands

```bash
# Check Vercel function logs
vercel logs

# Test specific endpoint
curl https://your-app.vercel.app/api/session/test

# Check environment variables
vercel env ls
```

## Step 5: Production Optimization

### Performance Tips

1. **Enable Vercel Analytics**
2. **Configure Custom Domain**
3. **Set up Edge Functions for global deployment**
4. **Monitor function execution time**

### Security Checklist

- ✅ Environment variables configured
- ✅ API keys not exposed in frontend
- ✅ HTTPS enabled (automatic on Vercel)
- ✅ CORS properly configured
- ✅ Session storage working correctly

## Step 6: Monitoring

### Key Metrics to Monitor

1. **Function Response Time**
2. **Error Rates**
3. **Session Storage Usage**
4. **Document Upload Success Rate**

### Vercel Analytics

- Go to Vercel dashboard → Analytics tab
- Monitor page views, API calls, performance
- Set up alerts for high error rates

## Expected Deployment Structure

```
your-app.vercel.app/
├── (Frontend Next.js pages)
├── api/
│   ├── documents/upload (serverless function)
│   ├── documents/{id} (serverless function)
│   ├── chat/ask (serverless function)
│   └── session/* (serverless functions)
└── _next/static (static assets)
```

## Success Criteria

Your deployment is successful when:

- ✅ Frontend loads at your domain
- ✅ Document upload works (check Network tab)
- ✅ Chat responses include AI answers and sources
- ✅ Session management functions work
- ✅ No console errors
- ✅ Mobile responsive design works
- ✅ Glassmorphic UI renders correctly

## Support

For Vercel-specific issues:
1. Check Vercel documentation
2. Review function logs in Vercel dashboard
3. Test with smaller files first
4. Verify all environment variables are set

---

**Note**: Session-based storage works perfectly in Vercel's serverless environment. Each function invocation maintains session state, and data auto-clears after 30 minutes as configured.
