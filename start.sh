#!/bin/bash

# AI Questionnaire Prototype - Startup Script
echo "🚀 Starting AI Questionnaire Prototype..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one based on .env.example"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "agent/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd agent
    python -m venv venv
    echo "✅ Virtual environment created"
    cd ..
fi

# Install dependencies if requirements.txt is newer than venv
if [ "agent/requirements.txt" -nt "agent/venv" ]; then
    echo "📥 Installing/updating dependencies..."
    cd agent
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
    cd ..
fi

# Store the PID file location
PID_FILE="/tmp/ai_questionnaire_backend.pid"

echo "📡 Starting backend server in background..."
cd agent
source venv/bin/activate
nohup python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > $PID_FILE
cd ..

# Wait a moment for server to start
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

echo "📱 Building and launching Flutter app..."
cd mobile

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not found. Please install Flutter first."
    exit 1
fi

# Get Flutter dependencies
flutter pub get

# Build and run the app
flutter run

echo "🎉 AI Questionnaire Prototype is running!"
echo "📝 Backend PID stored in $PID_FILE"
echo "🛑 Use ./shutdown.sh to stop all services"
