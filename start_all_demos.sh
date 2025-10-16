#!/bin/bash
set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Start All AI on the Edge Demos
# This script starts all demos in separate terminals with their virtual environments

echo "========================================="
echo "🚀 Starting All AI on the Edge Demos"
echo "========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check and start Foundry Local service if needed
echo "🔍 Checking Foundry Local service status..."
if command -v foundry &> /dev/null; then
    # Check if service is already running (check multiple possible ports)
    if curl -s http://localhost:60632/v1/models > /dev/null 2>&1 || curl -s http://localhost:52009/v1/models > /dev/null 2>&1; then
        echo "✅ Foundry Local service is already running"
    else
        echo "🚀 Starting Foundry Local service..."
        foundry service start
        echo "⏳ Waiting for Foundry Local service to initialize (30 seconds)..."
        sleep 30
        echo "✅ Foundry Local service started"
    fi
else
    echo "⚠️  Foundry CLI not found. Windows AI Foundry demo will run in limited mode."
    echo "💡 To enable full features, install: winget install Microsoft.AIFoundry"
fi
echo ""

# Function to setup venv for a demo and return the python path
setup_demo_venv() {
    local demo_dir="$1"
    local demo_name="$2"
    
    cd "$SCRIPT_DIR/$demo_dir"
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "   📦 Creating virtual environment for $demo_name..."
        python -m venv venv
        
        if [ ! -d "venv" ]; then
            echo "   ❌ Error: Failed to create venv"
            echo "python"
            return 1
        fi
        
        echo "   📥 Installing dependencies for $demo_name..."
        # Use python -m pip instead of pip.exe
        if [ -f "venv/Scripts/python.exe" ]; then
            venv/Scripts/python.exe -m pip install --upgrade pip || true
            venv/Scripts/python.exe -m pip install -r requirements.txt || echo "   ⚠️  Warning: Some dependencies may have failed to install"
        elif [ -f "venv/bin/python" ]; then
            venv/bin/python -m pip install --upgrade pip || true
            venv/bin/python -m pip install -r requirements.txt || echo "   ⚠️  Warning: Some dependencies may have failed to install"
        else
            echo "   ❌ Error: Could not find python in venv"
            echo "python"
            return 1
        fi
        echo "   ✅ Setup complete for $demo_name"
    fi
    
    # Return the path to venv's python
    if [ -f "venv/Scripts/python.exe" ]; then
        echo "venv/Scripts/python.exe"
    elif [ -f "venv/bin/python" ]; then
        echo "venv/bin/python"
    else
        echo "python"
    fi
}

# Start Azure Foundry Chat Playground (Port 5001)
echo "📱 Starting Azure Foundry Chat Playground on port 5001..."
PYTHON_CMD=$(setup_demo_venv "edge-ai-foundrylocal-chat-playground" "Azure Foundry Chat Playground")
cd "$SCRIPT_DIR/edge-ai-foundrylocal-chat-playground"
$PYTHON_CMD foundry_app.py &
FOUNDRY_PID=$!

# Start IoT Sensor Simulator (Port 5003)
echo "📡 Starting IoT Sensor Simulator on port 5003..."
PYTHON_CMD=$(setup_demo_venv "edge-ai-iot-sensor" "IoT Sensor Simulator")
cd "$SCRIPT_DIR/edge-ai-iot-sensor"
$PYTHON_CMD iot_sensor_app.py &
IOT_PID=$!

# Start Quality Control System (Port 5000)
echo "🔍 Starting Quality Control System on port 5000..."
PYTHON_CMD=$(setup_demo_venv "edge-ai-quality-control" "Quality Control System")
cd "$SCRIPT_DIR/edge-ai-quality-control"
$PYTHON_CMD azure_ai_quality_control.py &
QC_PID=$!

# Start Smart Camera System (Port 5002)
echo "📹 Starting Smart Camera System on port 5002..."
PYTHON_CMD=$(setup_demo_venv "edge-ai-smart-camera" "Smart Camera System")
cd "$SCRIPT_DIR/edge-ai-smart-camera"
$PYTHON_CMD smart_camera_app.py &
CAMERA_PID=$!

# Start Windows AI Foundry Demo (Port 5004)
echo "🪟 Starting Windows AI Foundry Demo on port 5004..."
PYTHON_CMD=$(setup_demo_venv "edge-ai-windows-foundry" "Windows AI Foundry Demo")
cd "$SCRIPT_DIR/edge-ai-windows-foundry"
$PYTHON_CMD windows_ai_foundry_app.py &
WINDOWS_PID=$!

# Start RAG Document Search (Port 5005)
echo "📚 Starting RAG Document Search on port 5005..."
PYTHON_CMD=$(setup_demo_venv "edge-ai-rag-document-search" "RAG Document Search")
cd "$SCRIPT_DIR/edge-ai-rag-document-search"
$PYTHON_CMD rag_document_app.py &
RAG_PID=$!

echo ""
echo "========================================="
echo "✅ All Demos Started Successfully!"
echo "========================================="
echo ""
echo "📋 Demo URLs:"
echo "   🔍 Quality Control System:        http://localhost:5000"
echo "   🤖 Azure Foundry Chat Playground: http://localhost:5001"
echo "   📹 Smart Camera System:           http://localhost:5002"
echo "   📡 IoT Sensor Simulator:          http://localhost:5003"
echo "   🪟 Windows AI Foundry Demo:       http://localhost:5004"
echo "   📚 RAG Document Search:           http://localhost:5005"
echo ""
echo "💡 Tip: If Foundry Local is not running, some demos will operate in limited mode"
echo ""
echo "🛑 To stop all demos, press Ctrl+C or run: ./stop_all_demos.sh"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping all demos...'; kill $FOUNDRY_PID $IOT_PID $QC_PID $CAMERA_PID $WINDOWS_PID $RAG_PID 2>/dev/null; echo '✅ All demos stopped'; exit 0" INT

# Keep script running
wait
