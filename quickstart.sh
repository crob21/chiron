#!/bin/bash
# Chiron Quick Start Script

set -e

echo "🏛️  Chiron Quick Start"
echo "===================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION detected"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found - you'll need it to run Chiron"
    echo "   Install: brew install postgresql (macOS) or apt install postgresql (Linux)"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found"
    echo ""
    read -p "Would you like to create one now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Let's set up your environment..."
        echo ""

        read -p "Enter your PostgreSQL database URL (or press Enter for default): " db_url
        db_url=${db_url:-"postgresql://localhost:5432/chiron"}

        read -p "Enter your Gemini API key: " gemini_key

        # Generate random secret
        api_secret=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

        # Create .env file
        cat > .env << EOF
# Database
DATABASE_URL=$db_url

# API Keys
GEMINI_API_KEY=$gemini_key
API_SECRET_KEY=$api_secret

# TrueCoach OAuth (add later)
TRUECOACH_CLIENT_ID=
TRUECOACH_CLIENT_SECRET=
TRUECOACH_REDIRECT_URI=http://localhost:8000/auth/truecoach/callback

# MyFitnessPal (add later)
MFP_USERNAME=
MFP_PASSWORD=

# App Settings
SYNC_INTERVAL_MINUTES=30
LOG_LEVEL=INFO
EOF
        echo "✅ .env file created"
    else
        echo "❌ Cannot continue without .env file"
        echo "   Copy .env.template to .env and fill in your credentials"
        exit 1
    fi
fi

# Initialize database
echo ""
read -p "Initialize database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗄️  Initializing database..."
    python scripts/init_db.py
fi

# Create user
echo ""
read -p "Create a user account? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter email address: " email
    python scripts/create_user.py "$email"
fi

# Start server
echo ""
echo "================================"
echo "✅ Setup complete!"
echo "================================"
echo ""
read -p "Start the server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting Chiron server..."
    echo "   Visit: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    python main.py
else
    echo ""
    echo "To start the server later, run:"
    echo "  source venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo "Train like a hero! 🏛️"
fi
