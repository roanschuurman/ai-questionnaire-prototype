#!/bin/bash

# AI Questionnaire Prototype - Simple Startup Script
echo "🚀 Starting AI Questionnaire Prototype..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one based on .env.example"
    exit 1
fi

# Use existing .venv (which was already working)
echo "📡 Starting backend server in background..."
source .venv/bin/activate
cd agent
nohup python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/ai_questionnaire_backend.pid
cd ..

# Wait for server to start
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend server started (PID: $BACKEND_PID)"
    echo "📋 Logs available in backend.log"
    echo "🌐 Server running at http://localhost:8000"
else
    echo "❌ Failed to start backend server"
    exit 1
fi

echo "📱 Starting Flutter app..."
flutter run

echo "🎉 Done!"
