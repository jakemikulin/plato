#!/bin/bash

# Navigate to backend
cd backend

# Activate virtual environment
source .venv/bin/activate

# Ensure no previous Ollama process is running
pkill -f ollama 2>/dev/null 

# Start local Ollama (ensure repo models are used)
cd ollama
export OLLAMA_MODELS=$(pwd)/models
./ollama serve &  
cd ..

# Give Ollama extra time to start (ensures models are loaded properly)
sleep 5

# Start backend in background and log output
python3 main.py > ../backend.log 2>&1 &  

# Navigate to frontend and run Flutter
cd ../frontend
flutter run -d chrome
