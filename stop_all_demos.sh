#!/bin/bash
# Stop All AI on the Edge Demos (Cross-platform)

echo "🛑 Stopping all AI on the Edge demos..."

# Detect OS and use appropriate method
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash, Cygwin, MSYS)
    taskkill //F //IM python.exe 2>/dev/null
else
    # Linux/macOS
    pkill -f "foundry_app.py"
    pkill -f "iot_sensor_app.py"
    pkill -f "azure_ai_quality_control.py"
    pkill -f "smart_camera_app.py"
    pkill -f "windows_ai_foundry_app.py"
fi

echo "✅ All demos stopped successfully"
