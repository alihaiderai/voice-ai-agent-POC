# Quick Fix for Installation

## What Changed

I've updated the project to use **OpenAI's APIs** for both speech-to-text and text-to-speech instead of local models. This is:
- ✅ Easier to install (no complex dependencies)
- ✅ Better quality
- ✅ Faster
- ✅ More reliable

**Cost:** ~$0.02-0.05 per conversation (still very cheap for POC)

## Install Now

In your PowerShell (with venv activated):

```powershell
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

This should complete without errors now!

## Then Run

```powershell
.\run.bat
```

## What's Using OpenAI API Now

1. **GPT-4** - Language model (already was)
2. **Whisper API** - Speech-to-text (NEW - was local model)
3. **TTS API** - Text-to-speech (NEW - was Coqui TTS)

All use the same API key you already added to `.env`!
