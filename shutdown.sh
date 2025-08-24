#!/bin/bash

# AI Questionnaire Prototype - Shutdown Script
echo "🛑 Shutting down AI Questionnaire Prototype..."

PID_FILE="/tmp/ai_questionnaire_backend.pid"

# Stop backend server
if [ -f "$PID_FILE" ]; then
    BACKEND_PID=$(cat $PID_FILE)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "🔻 Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        
        # Force kill if still running
        if ps -p $BACKEND_PID > /dev/null; then
            echo "🔥 Force stopping backend server..."
            kill -9 $BACKEND_PID
        fi
        
        echo "✅ Backend server stopped"
    else
        echo "⚠️  Backend server not running"
    fi
    
    # Remove PID file
    rm $PID_FILE
else
    echo "⚠️  No PID file found, checking for any Python processes..."
    
    # Look for our specific main.py process
    PYTHON_PID=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$PYTHON_PID" ]; then
        echo "🔻 Found Python process (PID: $PYTHON_PID), stopping..."
        kill $PYTHON_PID
        sleep 2
        echo "✅ Python process stopped"
    fi
fi

# Stop any Flutter processes
echo "📱 Stopping Flutter processes..."
pkill -f "flutter run" 2>/dev/null || true
pkill -f "dart" 2>/dev/null || true

# Clean up any remaining processes on port 8000
echo "🔌 Cleaning up port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Clean up log file
if [ -f "backend.log" ]; then
    echo "📋 Clearing backend.log..."
    > backend.log
fi

echo "🧹 Cleanup completed!"
echo "✅ All services stopped successfully"
