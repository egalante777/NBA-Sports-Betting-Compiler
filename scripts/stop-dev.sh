#!/bin/bash

# NBA Sports Betting Compiler - Stop Development Servers Script

echo "🛑 Stopping NBA Betting Compiler Development Environment..."

# Function to gracefully stop a process
stop_process() {
    local process_name=$1
    local pattern=$2

    echo "📋 Stopping $process_name..."

    # Find processes
    pids=$(pgrep -f "$pattern" 2>/dev/null)

    if [ -z "$pids" ]; then
        echo "   ℹ️  No $process_name processes running"
        return 0
    fi

    # Try graceful termination first (SIGTERM)
    echo "   🔄 Sending graceful stop signal to $process_name..."
    for pid in $pids; do
        kill -TERM "$pid" 2>/dev/null
    done

    # Wait up to 10 seconds for graceful shutdown
    local count=0
    while [ $count -lt 10 ]; do
        sleep 1
        remaining_pids=$(pgrep -f "$pattern" 2>/dev/null)
        if [ -z "$remaining_pids" ]; then
            echo "   ✅ $process_name stopped gracefully"
            return 0
        fi
        count=$((count + 1))
        echo "   ⏳ Waiting for $process_name to stop... ($count/10)"
    done

    # If still running, try SIGINT (Ctrl+C equivalent)
    remaining_pids=$(pgrep -f "$pattern" 2>/dev/null)
    if [ ! -z "$remaining_pids" ]; then
        echo "   🔄 Sending interrupt signal to $process_name..."
        for pid in $remaining_pids; do
            kill -INT "$pid" 2>/dev/null
        done

        # Wait another 5 seconds
        sleep 5
        remaining_pids=$(pgrep -f "$pattern" 2>/dev/null)
    fi

    # Final check - force kill only if absolutely necessary
    remaining_pids=$(pgrep -f "$pattern" 2>/dev/null)
    if [ ! -z "$remaining_pids" ]; then
        echo "   ⚠️  Force stopping $process_name (process not responding to graceful shutdown)..."
        for pid in $remaining_pids; do
            kill -KILL "$pid" 2>/dev/null
        done
        echo "   ✅ $process_name force stopped"
    else
        echo "   ✅ $process_name stopped successfully"
    fi
}

# Stop backend (FastAPI/uvicorn)
stop_process "Backend API" "uvicorn app.main:app"

# Stop frontend (React dev server)
stop_process "Frontend React" "react-scripts start"

# Stop any remaining npm processes for this project
stop_process "Frontend npm" "npm start.*frontend"

# Additional cleanup for any node processes running React scripts
stop_process "Node React processes" "node.*react-scripts"

echo ""
echo "✅ All NBA Betting Compiler servers stopped successfully!"

# Verify nothing is running on the expected ports
if command -v lsof >/dev/null 2>&1; then
    echo ""
    echo "🔍 Verifying ports are free..."

    backend_port=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$backend_port" ]; then
        echo "   ⚠️  Port 8000 still in use by PID $backend_port"
    else
        echo "   ✅ Port 8000 (backend) is free"
    fi

    frontend_port=$(lsof -ti:3000 2>/dev/null)
    if [ ! -z "$frontend_port" ]; then
        echo "   ⚠️  Port 3000 still in use by PID $frontend_port"
    else
        echo "   ✅ Port 3000 (frontend) is free"
    fi
fi

echo ""
echo "🚀 Ready to restart with: make dev"