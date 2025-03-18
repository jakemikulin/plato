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
    echo "✅ Model downloaded successfully!"
fi

# Navigate to backend
cd backend

# Activate virtual environment
source .venv/bin/activate

# Start Ollama (system-wide)
ollama serve &  

# Give Ollama time to start
sleep 5

# Start backend in background
python3 main.py &  

# Navigate to frontend and run Flutter
cd ../frontend
flutter run -d chrome
