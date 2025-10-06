#!/bin/bash
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

# Start Azure Foundry Chat Playground (Port 5000)
echo "📱 Starting Azure Foundry Chat Playground on port 5000..."
cd "$SCRIPT_DIR/edge-ai-foundrylocal-chat-playground"
python foundry_app.py &
FOUNDRY_PID=$!

# Start IoT Sensor Simulator (Port 5001)
echo "📡 Starting IoT Sensor Simulator on port 5001..."
cd "$SCRIPT_DIR/edge-ai-iot-sensor"
source venv/Scripts/activate
python iot_sensor_app.py &
IOT_PID=$!

# Start Quality Control System (Port 5002)
echo "🔍 Starting Quality Control System on port 5002..."
cd "$SCRIPT_DIR/edge-ai-quality-control"
source venv/Scripts/activate
python azure_ai_quality_control.py &
QC_PID=$!

# Start Smart Camera System (Port 5003)
echo "📹 Starting Smart Camera System on port 5003..."
cd "$SCRIPT_DIR/edge-ai-smart-camera"
source venv/Scripts/activate
python smart_camera_app.py &
CAMERA_PID=$!

# Start Windows AI Foundry Demo (Port 5004)
echo "🪟 Starting Windows AI Foundry Demo on port 5004..."
cd "$SCRIPT_DIR/edge-ai-windows-foundry"
source venv/Scripts/activate
python windows_ai_foundry_app.py &
WINDOWS_PID=$!

echo ""
echo "========================================="
echo "✅ All Demos Started Successfully!"
echo "========================================="
echo ""
echo "📋 Demo URLs:"
echo "   🤖 Azure Foundry Chat Playground: http://localhost:5000"
echo "   📡 IoT Sensor Simulator:          http://localhost:5001"
echo "   🔍 Quality Control System:        http://localhost:5002"
echo "   📹 Smart Camera System:           http://localhost:5003"
echo "   🪟 Windows AI Foundry Demo:       http://localhost:5004"
echo ""
echo "💡 Tip: If Foundry Local is not running, some demos will operate in limited mode"
echo ""
echo "🛑 To stop all demos, press Ctrl+C or run: ./stop_all_demos.sh"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping all demos...'; kill $FOUNDRY_PID $IOT_PID $QC_PID $CAMERA_PID $WINDOWS_PID 2>/dev/null; echo '✅ All demos stopped'; exit 0" INT

# Keep script running
wait
