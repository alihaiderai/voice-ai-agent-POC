# 🤖 Voice AI Agent Platform

A production-ready voice AI platform with web chat and phone call capabilities (inbound/outbound). Built as an alternative to Retell.ai with 85% cost savings.

## ✨ Features

- 🎙️ **Web Voice Chat** - Real-time voice conversations in browser
- 📞 **Inbound Phone Calls** - AI answers customer calls 24/7
- 📤 **Outbound Phone Calls** - AI makes automated calls
- 🤖 **Multi-Agent System** - Specialized agents (Support, Booking, General)
- 🎯 **Smart Routing** - Orchestrator routes to appropriate agent
- 💬 **Real-time Transcription** - Speech-to-text with OpenAI Whisper
- 🔊 **Natural Voice** - Text-to-speech with OpenAI TTS
- 😊 **Emotion Detection** - Detects customer sentiment
- 🧠 **Conversation Memory** - Maintains context throughout conversation
- 📊 **Analytics Dashboard** - Track calls, costs, and performance

## 🏗️ Architecture

```
┌─────────────┐
│   Customer  │
│ (Web/Phone) │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│   Frontend      │ ← React + Vite + TailwindCSS
│  (Port 3000)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Backend       │ ← FastAPI + WebSocket
│  (Port 8000)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐ ┌──────────┐
│ OpenAI │ │  Twilio  │
│  APIs  │ │  Phone   │
└────────┘ └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key
- Twilio account (for phone calls)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your API keys to .env

python main.py
```

Backend runs on: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:3000`

### Phone Setup (Twilio)

1. Sign up at [Twilio](https://www.twilio.com)
2. Get phone number
3. Configure webhook: `https://your-domain/api/phone/voice`
4. Add credentials to `.env`

## 📋 Environment Variables

Create `backend/.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
```

## 💰 Cost Comparison

| Feature | Retell.ai | Our Platform |
|---------|-----------|--------------|
| Monthly Base | $200-500 | $0 |
| Per Minute | $0.10 | $0.06 |
| Setup Fee | $0 | $0 |
| Customization | Limited | Full Control |

**Savings: 85% cheaper than Retell.ai**

## 📊 Analytics

View real-time analytics at: `http://localhost:3000/analytics.html`

Tracks:
- Total calls (inbound/outbound)
- Average duration
- Cost per call
- Success rate
- Top queries
- Emotion distribution

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- OpenAI GPT-4o-mini (LLM)
- OpenAI Whisper (Speech-to-text)
- OpenAI TTS (Text-to-speech)
- Twilio (Phone calls)

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Lucide Icons

## 📱 Use Cases

1. **Customer Support** - 24/7 automated support
2. **Appointment Booking** - Schedule appointments automatically
3. **Lead Qualification** - Call and qualify leads
4. **Payment Reminders** - Automated payment reminders
5. **Surveys** - Collect customer feedback

## 🔒 Security

- API keys stored in environment variables
- CORS configured for production
- Input validation on all endpoints
- Rate limiting (production)

## 📈 Roadmap

- [ ] Call transfer to human agents
- [ ] Multi-language support (50+ languages)
- [ ] Real-time streaming (OpenAI Realtime API)
- [ ] CRM integration
- [ ] Advanced analytics
- [ ] Call recording
- [ ] Custom voice training

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📄 License

MIT License

## 🙏 Acknowledgments

- OpenAI for GPT-4, Whisper, and TTS
- Twilio for phone infrastructure
- FastAPI for excellent Python framework

## 📞 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ as an open-source alternative to Retell.ai**
