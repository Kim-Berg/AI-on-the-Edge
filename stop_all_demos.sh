#!/bin/bash
set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Stop All AI on the Edge Demos (Cross-platform)

echo "🛑 Stopping all AI on the Edge demos..."

# Detect OS and use appropriate method
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash, Cygwin, MSYS) - More specific targeting
    # Kill only Python processes running the specific demo scripts
    taskkill //F //FI "WINDOWTITLE eq edge-ai*" 2>/dev/null || true
    taskkill //F //FI "IMAGENAME eq python.exe" //FI "WINDOWTITLE eq *foundry_app*" 2>/dev/null || true
    taskkill //F //FI "IMAGENAME eq python.exe" //FI "WINDOWTITLE eq *iot_sensor*" 2>/dev/null || true
    taskkill //F //FI "IMAGENAME eq python.exe" //FI "WINDOWTITLE eq *quality_control*" 2>/dev/null || true
    taskkill //F //FI "IMAGENAME eq python.exe" //FI "WINDOWTITLE eq *smart_camera*" 2>/dev/null || true
    taskkill //F //FI "IMAGENAME eq python.exe" //FI "WINDOWTITLE eq *windows_ai_foundry*" 2>/dev/null || true
else
    # Linux/macOS - More specific process matching
    pkill -f "foundry_app.py" || true
    pkill -f "iot_sensor_app.py" || true
    pkill -f "azure_ai_quality_control.py" || true
    pkill -f "smart_camera_app.py" || true
    pkill -f "windows_ai_foundry_app.py" || true
fi

echo "✅ All demos stopped successfully"
