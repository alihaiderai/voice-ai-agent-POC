# 🚀 Deployment Guide

## Backend Deployment (Render)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Update for production deployment"
git push origin main
```

### Step 2: Deploy on Render

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

**Settings:**
- **Name**: `voice-ai-backend`
- **Root Directory**: `backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

**Environment Variables** (Add these):
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
ENVIRONMENT=production
```

5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment
7. Copy your backend URL: `https://your-app-name.onrender.com`

---

## Frontend Deployment (Vercel)

### Step 1: Update Backend URL

Edit `frontend/.env.production`:
```
VITE_API_URL=https://your-backend-name.onrender.com
VITE_WS_URL=wss://your-backend-name.onrender.com
```

### Step 2: Deploy on Vercel

1. Go to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:

**Settings:**
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

**Environment Variables:**
```
VITE_API_URL=https://your-backend-name.onrender.com
VITE_WS_URL=wss://your-backend-name.onrender.com
```

5. Click **"Deploy"**
6. Wait 2-3 minutes
7. Your app is live! `https://your-app.vercel.app`

---

## Twilio Configuration

Update Twilio webhook URL:

1. Go to Twilio Console → Phone Numbers
2. Click your number
3. Under "A call comes in":
   - URL: `https://your-backend-name.onrender.com/api/phone/voice`
   - Method: `HTTP POST`
4. Save

---

## Testing Deployment

### Test Backend:
```
https://your-backend-name.onrender.com/
```
Should return: `{"message": "Voice AI Agent Platform API"}`

### Test Frontend:
```
https://your-app.vercel.app
```
Should load the voice chat interface

### Test Phone:
Call your Twilio number - AI should answer!

---

## Troubleshooting

### Backend Issues:
- Check Render logs: Dashboard → Logs
- Verify environment variables are set
- Check Python version (3.10+)

### Frontend Issues:
- Check Vercel logs: Deployment → Function Logs
- Verify VITE_API_URL is correct
- Check browser console for errors

### CORS Issues:
- Make sure backend ENVIRONMENT=production is set
- Backend should allow all origins in production

---

## Cost Estimate

**Render (Backend):**
- Free tier: 750 hours/month
- Paid: $7/month (if needed)

**Vercel (Frontend):**
- Free tier: Unlimited
- Bandwidth: 100GB/month free

**Twilio:**
- ~$0.06/minute for calls
- ~$1/month for phone number

**OpenAI:**
- ~$0.01 per conversation
- ~$10-20/month for moderate usage

**Total: ~$20-30/month** (vs Retell.ai $200+/month)

---

## Production Checklist

- [ ] Backend deployed on Render
- [ ] Frontend deployed on Vercel
- [ ] Environment variables configured
- [ ] Twilio webhook updated
- [ ] Test inbound call
- [ ] Test outbound call
- [ ] Test web voice chat
- [ ] Analytics dashboard working
- [ ] HTTPS enabled (automatic)
- [ ] Custom domain (optional)

---

## Monitoring

**Render:**
- Dashboard → Metrics
- View CPU, memory, requests

**Vercel:**
- Analytics → Overview
- View page views, performance

**Twilio:**
- Console → Monitor → Logs
- View call logs, errors

---

## Scaling

**If you get more traffic:**

1. **Render**: Upgrade to paid plan ($7/month)
2. **Add Redis**: For session management
3. **Add Database**: PostgreSQL for analytics
4. **CDN**: Cloudflare for frontend
5. **Load Balancer**: Multiple backend instances

---

## Support

Issues? Check:
1. Render logs
2. Vercel logs
3. Browser console
4. GitHub Issues

---

**Your app is now live and production-ready!** 🎉
