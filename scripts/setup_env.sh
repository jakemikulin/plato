#!/bin/bash

echo "🚀 Setting up Virtual Environment..."

# Create Virtual Environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created!"
fi

# Activate Virtual Environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Fix for pypika issue
pip install --no-cache-dir pypika

# Start Ollama using your existing start_ollama.py script
echo "🚀 Ensuring Ollama is running..."
python3 start_ollama.py

echo "✅ Setup Complete! You can now run the chatbot."
