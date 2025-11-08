# Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### Step 1: Install Dependencies

```bash
# Make setup script executable (if not already)
chmod +x setup.sh

# Run setup script
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Configure API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-api-key-here
HUMAN_APPROVAL=true
```

**Get API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic Claude**: https://console.anthropic.com/
- **Google Gemini**: https://makersuite.google.com/app/apikey

### Step 3: Run the Application

```bash
python app/main.py
```

### Step 4: First Run

1. A browser window will open with WhatsApp Web
2. If not logged in, scan the QR code with your phone
3. Once logged in, open a chat in WhatsApp Web
4. The application will monitor for new messages

### Step 5: Enable AI Helper

The AI helper starts **disabled** by default. To enable:

- The application will automatically check for new messages
- When a new incoming message is detected, it will generate a reply
- If `HUMAN_APPROVAL=true`, you'll be prompted to approve the reply
- If approved, the reply will be sent automatically

## ⚙️ Configuration Options

### Enable/Disable Human Approval

Edit `.env`:

```env
HUMAN_APPROVAL=false  # Auto-send without approval
HUMAN_APPROVAL=true   # Require approval (default)
```

### Change LLM Provider

Edit `.env`:

```env
LLM_PROVIDER=openai   # or claude, gemini
```

### Adjust Response Tone

Edit `.env`:

```env
RESPONSE_TONE=romantic, respectful, natural
```

### Change Number of Messages Analyzed

Edit `.env`:

```env
MAX_MESSAGES_TO_READ=30  # Analyze last 30 messages
```

## 🎯 Usage Tips

1. **First Time Setup**: 
   - Run the app and scan QR code
   - Session will be saved for future runs

2. **Testing**:
   - Start with `HUMAN_APPROVAL=true` to review replies
   - Once comfortable, set to `false` for auto-send

3. **Monitoring**:
   - Check `logs/app.log` for detailed logs
   - Watch console output for status updates

4. **Troubleshooting**:
   - If browser doesn't open, set `BROWSER_HEADLESS=false`
   - If messages not detected, check that a chat is open
   - Review logs for detailed error messages

## 🔧 Common Issues

### "API Key not configured"
- Make sure `.env` file exists and has correct API key
- Check that `LLM_PROVIDER` matches your API key

### "Browser not found"
- Run: `playwright install chromium`
- Check Playwright installation: `playwright --version`

### "Messages not detected"
- Ensure a chat is open in WhatsApp Web
- Check that messages are visible in the chat
- Review logs for selector issues

### "Reply not sending"
- Verify input box is visible in WhatsApp Web
- Check if WhatsApp Web is in focus
- Try manually typing in the input box first

## 📝 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize prompts in `app/pipeline.py`
- Adjust safety filters in `app/utils.py`
- Modify message detection in `app/whatsapp_bot.py`

---

**Happy automating! 🎉**

