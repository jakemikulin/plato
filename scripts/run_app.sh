#!/bin/bash

# Navigate to backend and activate virtual environment
cd backend
source .venv/bin/activate

# Start backend in background
python3 main.py &  

# Navigate to frontend and run Flutter
cd ../frontend
flutter run -d chrome  