#!/bin/bash

# WhatsApp AI Chat Helper - Setup Script

echo "🚀 Setting up WhatsApp AI Chat Helper..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Check if Python 3.10+
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python 3.10 or higher is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it and add your API keys."
    else
        echo "⚠️  .env.example not found. Please create .env manually."
    fi
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p session logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file and add your API keys"
echo "   2. Run: python app/main.py"
echo ""

