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

# Stop Ollama if it's running
if pgrep -x "ollama" > /dev/null; then
    echo "Stopping Ollama..."
    pkill -f "ollama serve"
    sleep 2  # Give it time to shut down
fi

# Stop any process using port 8080
PORT=8080
if lsof -i :$PORT | grep LISTEN > /dev/null 2>&1; then
    echo "Stopping process using port $PORT..."
    lsof -ti :$PORT | xargs kill -9
    sleep 2  # Give it time to shut down
    echo "✅ Port $PORT is now free."
else
    echo "⚠️ No process found using port $PORT."
fi

# Remove the custom model from Ollama
MODEL_NAME="plato"
if ollama list | grep -q "$MODEL_NAME"; then
    echo "Removing Ollama model: $MODEL_NAME..."
    ollama rm "$MODEL_NAME"
    echo "✅ Model '$MODEL_NAME' removed successfully."
else
    echo "⚠️ Model '$MODEL_NAME' not found in Ollama."
fi

# Remove Modelfile if it exists
MODELFILE_PATH="backend/Modelfile"
if [ -f "$MODELFILE_PATH" ]; then
    echo "Deleting Modelfile..."
    rm "$MODELFILE_PATH"
    echo "✅ Modelfile deleted."
else
    echo "⚠️ No Modelfile found."
fi

# Confirm cleanup
echo "🚀 Ollama model cleanup complete! Your environment is now reset."
