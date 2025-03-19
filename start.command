#!/bin/bash

# 1. Move into the directory where this script is located
cd "$(dirname "$0")"

# 3. Make sure run_ollama_app.sh is executable
chmod +x scripts/run_ollama_app.sh

# 4. Execute the main script
./scripts/run_ollama_app.sh

# 5. Keep the terminal window open until user presses Enter (optional)
echo ""
echo "Press [Enter] to close this window..."
read
