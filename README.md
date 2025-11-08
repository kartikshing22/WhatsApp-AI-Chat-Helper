# WhatsApp AI Chat Helper

An intelligent desktop automation application that uses AI to generate and send natural, context-aware replies on WhatsApp Web.

## 🎯 Features

- **Automated WhatsApp Web Integration**: Uses Playwright for reliable browser automation
- **AI-Powered Replies**: Generates natural, romantic, and respectful responses using LangChain
- **Multiple LLM Support**: Works with OpenAI, Anthropic Claude, or Google Gemini
- **Session Persistence**: Saves login session so you don't need to scan QR code every time
- **Human Approval Mode**: Optional approval before sending AI-generated replies
- **Safety Filtering**: Built-in content filtering to prevent inappropriate responses
- **Real-time Message Detection**: Automatically detects and responds to new incoming messages

## 📋 Requirements

- Python 3.10 or higher
- A WhatsApp account (for WhatsApp Web)
- API key for at least one LLM provider (OpenAI, Claude, or Gemini)

## 🚀 Quick Start

### 1. Clone or Navigate to Project

```bash
cd WhatsApp-AI-Chat-Helper
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Configure Environment

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_actual_api_key_here
```

### 5. Run the Application

```bash
python main.py
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` file to configure the application:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider: `openai`, `claude`, or `gemini` | `openai` |
| `OPENAI_API_KEY` | Your OpenAI API key | Required if using OpenAI |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required if using Claude |
| `CLAUDE_MODEL` | Claude model name | `claude-3-5-sonnet-20241022` |
| `GEMINI_API_KEY` | Your Google API key | Required if using Gemini |
| `GEMINI_MODEL` | Gemini model name | `gemini-pro` |
| `BROWSER_HEADLESS` | Run browser in headless mode | `false` |
| `HUMAN_APPROVAL` | Require approval before sending | `true` |
| `MAX_MESSAGES_TO_READ` | Number of messages to analyze | `30` |
| `RESPONSE_TONE` | Desired response tone | `romantic, respectful, natural` |
| `MAX_RESPONSE_LENGTH` | Maximum reply length | `500` |
| `ENABLE_SAFETY_FILTER` | Enable content safety filtering | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 📁 Project Structure

```
Whatsapp-Helper/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── whatsapp_bot.py    # Playwright automation
│   ├── pipeline.py        # LangChain LLM pipeline
│   ├── utils.py           # Utilities and safety filters
│   └── main.py            # Main entry point
├── session/               # Browser session data (auto-created)
├── logs/                  # Application logs (auto-created)
├── .env                   # Environment variables (create from .env.example)
├── .env.example           # Example environment file
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎮 Usage

### Starting the Application

1. Run the application:
   ```bash
   python app/main.py
   ```

2. A browser window will open with WhatsApp Web
3. If not already logged in, scan the QR code with your phone
4. Once logged in, open a chat in WhatsApp Web
5. The application will monitor for new messages

### Enabling AI Helper

The AI helper starts in **disabled** mode. To enable it:

- type enable in CLI (Command line)
- The application will check for new messages periodically
- When a new incoming message is detected, it will generate a reply
- If `HUMAN_APPROVAL=true`, you'll be prompted to approve the reply
- If approved, the reply will be sent automatically

### Commands

While the application is running, you can interact via command line:

- Press `Enter` to manually check for new messages
- Type `t` + Enter to toggle AI Helper on/off
- Type `q` + Enter to quit

## 🔧 How It Works

1. **Browser Automation**: Playwright opens WhatsApp Web and maintains a persistent session
2. **Message Detection**: The bot monitors the currently open chat for new incoming messages
3. **Context Analysis**: When a new message arrives, it reads the last 30 messages for context
4. **AI Generation**: LangChain formats the chat history and sends it to the configured LLM
5. **Safety Filtering**: Generated replies are checked for inappropriate content
6. **Human Approval** (optional): If enabled, you review the reply before sending
7. **Auto-Send**: The reply is typed and sent automatically in WhatsApp Web

## 🛡️ Safety Features

- **Content Filtering**: Built-in safety filter prevents explicit or abusive content
- **Response Validation**: All generated replies are validated before sending
- **Human Override**: Optional approval mode gives you full control
- **Error Handling**: Robust error handling prevents crashes and data loss

## 🐛 Troubleshooting

### Browser Not Opening

- Ensure Playwright browsers are installed: `playwright install chromium`
- Check if another browser instance is already running
- Try setting `BROWSER_HEADLESS=false` to see what's happening

### Login Issues

- Clear the `session/` directory and try again
- Make sure WhatsApp Web is accessible in your browser
- Check your internet connection

### API Key Errors

- Verify your API key is correct in `.env`
- Ensure you have sufficient API credits/quota
- Check that the `LLM_PROVIDER` matches your API key

### Message Detection Not Working

- Make sure a chat is open in WhatsApp Web
- Check that messages are visible in the chat
- Review logs in `logs/app.log` for detailed error messages

### Reply Not Sending

- Verify the input box is visible in WhatsApp Web
- Check if WhatsApp Web is in focus
- Review browser console for errors

## 📝 Logging

Logs are written to:
- Console (stdout)
- File: `logs/app.log`

Set `LOG_LEVEL` in `.env` to control verbosity:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only

## 🔒 Privacy & Security

- **Local Processing**: All automation runs locally on your machine
- **Session Data**: Browser session is stored locally in `session/` directory
- **API Keys**: Store API keys securely in `.env` (never commit to git)
- **No Data Storage**: Chat messages are not stored permanently
- **Open Source**: Review the code to ensure it meets your security requirements

## 🤝 Contributing

This is a standalone application. Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Customize for your needs

## 📄 License

This project is provided as-is for educational and personal use.

## ⚠️ Disclaimer

- This tool is for personal use and automation
- Use responsibly and in accordance with WhatsApp's Terms of Service
- The AI-generated replies are suggestions - use your judgment
- Always review replies before sending in important conversations
- The authors are not responsible for any misuse of this tool

## 🆘 Support

For issues or questions:
1. Check the logs in `logs/app.log`
2. Review the troubleshooting section
3. Ensure all dependencies are installed correctly
4. Verify your configuration in `.env`

---

**Built with ❤️ using Playwright, LangChain, and Python**



Flow =>

main()
 └── WhatsAppAIChatHelper()
       └── run()
             ├── initialize()
             │     ├── Config.validate()
             │     ├── bot.start()
             │     │      ├── launch browser (Playwright)
             │     │      ├── open WhatsApp Web
             │     │      ├── wait for QR login
             │     │      └── load persistent session
             │     └── pipeline.is_ready()

             ├── start background tasks
             │     ├── handle_cli()        (Task 1 - waits for commands)
             │     └── monitor_messages()   (Task 2 - runs every 2 sec)

             ├── wait for any task to stop
             └── cleanup()
                   └── bot.close()
