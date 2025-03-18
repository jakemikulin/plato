#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Ensure Ollama is installed
if ! command_exists ollama; then
    echo "Ollama is not installed! Please install it from: https://ollama.ai"
    exit 1
fi

# Ensure the required model is available
MODEL_NAME="phi4-mini"
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "Pulling required model: $MODEL_NAME (this may take a while)..."
    
    # Show progress in real-time
    ollama pull "$MODEL_NAME" | tee download_progress.log
    
    if [ $? -ne 0 ]; then
        echo "Failed to download $MODEL_NAME. Please check your internet connection."
        exit 1
    fi
    echo "Model downloaded successfully!"
fi

# Navigate to backend
cd backend || { echo "Failed to enter backend directory!"; exit 1; }

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment (.venv) not found! Run setup_env.sh first."
    exit 1
fi

# Check if Ollama is already running
if ! curl -s http://127.0.0.1:11434/api/tags | grep -q "models"; then
    echo "Starting Ollama..."
    ollama serve &  
else
    echo "Ollama is already running."
fi

# Wait for Ollama to start
echo "Giving Ollama time to initialise..."
# sleep 10  

# Start backend in background
echo "Starting FastAPI backend..."
python3 main.py &  

# Wait for FastAPI to start
sleep 5  

# Navigate to frontend and run Flutter
cd ../frontend || { echo "Failed to enter frontend directory!"; exit 1; }

echo "Running Flutter Web App..."
flutter run -d chrome
