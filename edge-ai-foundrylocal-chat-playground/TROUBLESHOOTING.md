# Troubleshooting Guide

## Common Issues and Solutions

### 1. Installation Problems

#### "foundry command not found"
**Problem**: Azure Foundry Local is not installed or not in PATH.

**Solutions**:
```bash
# Windows
winget install Microsoft.FoundryLocal

# macOS
brew tap microsoft/foundrylocal
brew install foundrylocal

# Verify installation
foundry --version
```

#### "Python not found"
**Problem**: Python is not installed or not accessible.

**Solutions**:
- Install Python 3.8+ from [python.org](https://python.org)
- Ensure Python is added to PATH
- Use `python3` instead of `python` on some systems

### 2. Service Issues

#### "Foundry service failed to start"
**Problem**: Azure Foundry Local service won't start.

**Solutions**:
```bash
# Check service status
foundry service status

# Restart service
foundry service restart

# Check for conflicting processes
foundry service stop
foundry service start

# Check system requirements
foundry service check
```

#### "Request to local service failed"
**Problem**: Service connection issues after installation.

**Solutions**:
```bash
# Restart the service
foundry service restart

# Check if port is available
netstat -an | grep 8080  # Default Foundry port

# Reset service configuration
foundry service reset
```

### 3. Model Issues

#### "Model failed to download"
**Problem**: Model download fails or times out.

**Solutions**:
- Check internet connection
- Verify sufficient disk space (models are 0.5GB - 7GB)
- Try downloading manually:
  ```bash
  foundry model run qwen2.5-0.5b --download-only
  ```
- Use a different model if one fails

#### "Model initialization timeout"
**Problem**: Model takes too long to initialize.

**Solutions**:
- Wait longer (first load can take several minutes)
- Check system resources (RAM, CPU)
- Try a smaller model first (qwen2.5-0.5b)
- Restart the Foundry service

#### "Out of memory error"
**Problem**: System doesn't have enough RAM for model.

**Solutions**:
- Close other applications
- Use smaller models
- Check model requirements:
  ```bash
  foundry model info <model-name>
  ```

### 4. Web Application Issues

#### "Port 5000 already in use"
**Problem**: Another application is using port 5000.

**Solutions**:
- Stop the conflicting application
- Change port in `app.py`:
  ```python
  app.run(debug=True, port=5001)  # Use different port
  ```
- Kill existing Python processes:
  ```bash
  pkill -f "python app.py"
  ```

#### "Module not found errors"
**Problem**: Python dependencies not installed.

**Solutions**:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Update pip if needed
pip install --upgrade pip
```

#### "Static files not loading"
**Problem**: CSS/JS files not found (404 errors).

**Solutions**:
- Verify file structure matches the project layout
- Check Flask static folder configuration
- Clear browser cache
- Restart the application

### 5. Performance Issues

#### "Slow response times"
**Problem**: Models respond very slowly.

**Solutions**:
- Check system resources (Task Manager/Activity Monitor)
- Use hardware acceleration if available:
  ```bash
  # Check GPU support
  foundry system info
  ```
- Reduce model complexity or size
- Lower max_tokens in configuration

#### "Browser freezing"
**Problem**: Web interface becomes unresponsive.

**Solutions**:
- Refresh the browser page
- Clear browser cache and cookies
- Try a different browser
- Check for JavaScript errors in developer console

### 6. Configuration Issues

#### "Environment variables not loaded"
**Problem**: Settings from `.env` file not applied.

**Solutions**:
- Verify `.env` file exists in project root
- Check file syntax (no spaces around `=`)
- Restart the application after changes
- Use absolute paths for file locations

#### "Models not showing in UI"
**Problem**: Model list appears empty.

**Solutions**:
- Check network connection to load model list
- Verify Foundry service is running
- Check browser console for JavaScript errors
- Restart both Foundry service and web app

### 7. Development Issues

#### "Hot reload not working"
**Problem**: Changes not reflected in browser.

**Solutions**:
- Use development mode:
  ```bash
  export FLASK_ENV=development
  export FLASK_DEBUG=True
  python app.py
  ```
- Hard refresh browser (Ctrl+F5 / Cmd+Shift+R)
- Check for syntax errors in Python code

#### "Database/history errors"
**Problem**: Chat history not saving.

**Solutions**:
- Check file permissions in project directory
- Verify sufficient disk space
- Clear history and restart:
  ```bash
  curl -X POST http://localhost:5000/api/history/clear
  ```

### 8. System-Specific Issues

#### Windows Issues
- **Antivirus blocking**: Add project folder to antivirus exceptions
- **PowerShell execution policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Long path issues**: Enable long paths in Windows settings

#### macOS Issues
- **Permission denied**: Use `chmod +x` on shell scripts
- **Homebrew issues**: Update Homebrew: `brew update && brew upgrade`
- **Python version conflicts**: Use `python3` explicitly

#### Linux Issues
- **Package dependencies**: Install build tools: `sudo apt-get install build-essential python3-dev`
- **Permission issues**: Check file ownership and permissions
- **Display issues**: Ensure proper display server (X11/Wayland) setup

## Diagnostic Commands

### Quick Health Check
```bash
# Check all services
foundry service status
foundry model list
foundry cache list

# Check Python environment  
python --version
pip list | grep -E "(flask|openai|foundry)"

# Check network connectivity
curl -I http://localhost:5000
```

### Detailed Diagnostics
```bash
# System information
foundry system info

# Service logs (if available)
foundry service logs

# Model cache location
foundry cache info

# Port usage
netstat -tulpn | grep :5000
```

## Getting Help

### Log Files
- Application logs: Check terminal output
- Foundry logs: `foundry service logs` (if available)
- Browser console: F12 → Console tab

### Useful Commands
```bash
# Reset everything
foundry service stop
foundry cache clear
rm -rf venv
./setup.sh

# Check versions
foundry --version
python --version
pip --version

# Test basic functionality
foundry model run qwen2.5-0.5b --test
```

### Support Resources
1. [Azure Foundry Local Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
2. [GitHub Issues](https://github.com/microsoft/Foundry-Local/issues)
3. [Microsoft Learn Q&A](https://docs.microsoft.com/en-us/answers/)
4. Project README.md for basic usage

### Reporting Issues
When reporting issues, include:
- Operating system and version
- Python version
- Azure Foundry Local version
- Complete error messages
- Steps to reproduce
- System specifications (RAM, CPU, GPU)