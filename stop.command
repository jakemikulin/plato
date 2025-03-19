#!/bin/bash

# Move into the directory of this .command file
cd "$(dirname "$0")"

# Make sure reset_ollama_models.sh is executable
chmod +x scripts/reset_ollama_models.sh

# Run the reset script
./scripts/reset_ollama_models.sh

# Pause to keep the terminal window open
echo ""
echo "All processes have been stopped and reset. Press [Enter] to close..."
read
