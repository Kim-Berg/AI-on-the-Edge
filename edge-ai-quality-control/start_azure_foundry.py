"""
Azure AI Foundry Local Startup Script
Checks connection and launches quality control demo
"""

import requests
import json
import time
import os
import sys
import subprocess
import re

def get_foundry_port():
    """Get the port that Foundry Local is running on"""
    try:
        result = subprocess.run(['foundry', 'service', 'status'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # Look for port in output - Foundry Local shows URL like http://127.0.0.1:PORT/
            lines = result.stdout.split('\n')
            for line in lines:
                if 'http://127.0.0.1:' in line or 'http://localhost:' in line:
                    # Extract port number from URL
                    port_match = re.search(r':(\d+)', line)
                    if port_match:
                        return int(port_match.group(1))
        
        return None
    except Exception as e:
        return None

def check_azure_foundry_local():
    """Check if Azure AI Foundry Local is running"""
    # First, try to get the dynamic port from foundry service status
    foundry_port = get_foundry_port()
    endpoints = []
    
    if foundry_port:
        endpoints.append({
            "url": f"http://localhost:{foundry_port}",
            "name": f"Azure AI Foundry Local (detected port {foundry_port})"
        })
        print(f"🔍 Detected Foundry Local running on port {foundry_port}")
    
    # Add fallback endpoints
    endpoints.extend([
        {"url": "http://localhost:3928", "name": "Azure AI Foundry Local (default port)"},
        {"url": "http://localhost:1234", "name": "Azure AI Foundry Local (alt port)"},
        {"url": "http://localhost:60632", "name": "Azure AI Foundry Local (dynamic port 60632)"},
        {"url": "http://localhost:52009", "name": "Azure AI Foundry Local (dynamic port 52009)"},
        {"url": "http://127.0.0.1:3928", "name": "Azure AI Foundry Local (127.0.0.1)"},
        {"url": "http://localhost:11434", "name": "Ollama (compatibility mode)"}
    ])
    
    print("🔍 Checking for Azure AI Foundry Local...")
    
    for endpoint in endpoints:
        try:
            print(f"   Testing {endpoint['name']}...")
            
            # Try multiple API paths
            api_paths = ["/v1/models", "/models", "/api/models", "/"]
            
            for path in api_paths:
                try:
                    response = requests.get(f"{endpoint['url']}{path}", timeout=3)
                    if response.status_code == 200:
                        print(f"✅ Found service at: {endpoint['url']}")
                        
                        # Try to get models
                        if "models" in path:
                            try:
                                models = response.json()
                                if isinstance(models, dict) and 'data' in models:
                                    model_list = [model['id'] for model in models['data']]
                                elif isinstance(models, list):
                                    model_list = [model.get('id', model.get('name', str(model))) for model in models]
                                else:
                                    model_list = []
                                    
                                print(f"📋 Available models: {', '.join(model_list) if model_list else 'Service running, models list unavailable'}")
                                
                                # Check for vision-capable models
                                vision_models = [m for m in model_list if any(term in str(m).lower() 
                                    for term in ['vision', 'multimodal', 'gpt-4', 'phi-4', 'llava'])]
                                
                                if vision_models:
                                    print(f"👁️ Vision models found: {', '.join(vision_models)}")
                                else:
                                    print("⚠️ No vision models detected. Text analysis will be used.")
                                
                                return endpoint['url'], model_list
                            except:
                                print(f"✅ Service running at {endpoint['url']} (models list unavailable)")
                                return endpoint['url'], []
                        else:
                            print(f"✅ Service responding at {endpoint['url']}")
                            return endpoint['url'], []
                except requests.exceptions.RequestException:
                    continue
                    
        except requests.exceptions.RequestException:
            continue
    
    return None, []

def setup_instructions():
    """Display detailed setup instructions for Azure AI Foundry Local"""
    print("\n📋 Azure AI Foundry Local Setup Instructions:")
    print("=" * 60)
    print("1️⃣ Download and Install:")
    print("   • Visit: https://azure.microsoft.com/products/ai-foundry/")
    print("   • Or use: winget install Microsoft.AzureAIFoundryLocal")
    print("   • Or download from Microsoft Store")
    
    print("\n2️⃣ Start the Service:")
    print("   • Launch from Start Menu: 'Azure AI Foundry Local'")
    print("   • Or run in terminal: azure-ai-foundry-local")
    print("   • Service runs on port 3928 by default")
    
    print("\n3️⃣ Load a Model (Choose one):")
    print("   🎯 For Best Results (Vision-capable):")
    print("      • phi-4-multimodal-instruct")
    print("      • llama-3.2-11b-vision-instruct") 
    print("      • gpt-4-vision-preview")
    print("   📝 Text-only Models:")
    print("      • phi-4")
    print("      • llama-3.2-3b-instruct")
    
    print("\n4️⃣ Verify Installation:")
    print("   • Open browser to: http://localhost:3928")
    print("   • Should see Azure AI Foundry Local interface")
    
    print("\n5️⃣ Alternative Ports (if default doesn't work):")
    print("   • Port 1234 (LM Studio compatibility)")
    print("   • Port 11434 (Ollama compatibility)")

def main():
    """Main function to start the quality control demo"""
    print("🚀 Azure AI Quality Control Demo")
    print("🤖 With Azure AI Foundry Local Integration")
    print("=" * 60)
    
    # Check Azure AI Foundry Local
    endpoint, models = check_azure_foundry_local()
    
    if not endpoint:
        print("❌ Azure AI Foundry Local not detected!")
        setup_instructions()
        print("\n" + "⚠️" * 20)
        print("⚠️ IMPORTANT: Demo will run in SIMULATION mode without AI")
        print("⚠️" * 20)
        
        choice = input("\n🤔 Continue with simulation mode? (y/N): ").lower()
        if choice != 'y':
            print("� Set up Azure AI Foundry Local first, then re-run this script!")
            return
            
        print("�🔄 Starting simulation mode...")
        app_file = "quality_control_app.py"
    else:
        print(f"✅ Connected to Azure AI Foundry Local: {endpoint}")
        
        if models:
            vision_models = [m for m in models if any(term in str(m).lower() 
                for term in ['vision', 'multimodal', 'gpt-4', 'phi-4', 'llava'])]
            
            if vision_models:
                print(f"👁️ Vision Analysis Available! Models: {', '.join(vision_models[:2])}")
                print("🎯 Demo will use AI-powered image defect detection!")
            else:
                print("📝 Text-based AI analysis will be used")
                print("💡 For best results, load a vision-capable model")
        
        print("🚀 Starting enhanced demo with Azure AI Foundry Local...")
        app_file = "azure_ai_quality_control.py"
    
    print(f"\n🎯 Launching Application...")
    print("🌐 Open browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Use subprocess for better error handling
        import subprocess
        result = subprocess.run([sys.executable, app_file], cwd=os.path.dirname(__file__))
        if result.returncode != 0:
            print(f"\n❌ Application exited with error code: {result.returncode}")
    except FileNotFoundError:
        print(f"❌ Could not find {app_file}")
        print("💡 Make sure you're running this script from the correct directory")
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()