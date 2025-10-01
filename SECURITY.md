# Security Notes

## Important Security Information

This repository contains demo applications for educational purposes. Before deploying to production, please review the following:

### 🔐 Secret Keys

Several demo applications contain hardcoded SECRET_KEY values for Flask sessions:
- `edge-ai-windows-foundry/windows_ai_foundry_app.py`
- `edge-ai-smart-camera/smart_camera_app.py`
- `edge-ai-quality-control/azure_ai_quality_control.py`

**⚠️ For Production Use:**
- Replace all SECRET_KEY values with strong, randomly generated keys
- Use environment variables to store secrets
- Never commit real credentials to version control

### 📝 Environment Variables

The `edge-ai-foundrylocal-chat-playground` demo uses a `.env` file for configuration.

**Setup:**
1. Copy `.env.example` to `.env`
2. Update values as needed
3. The `.env` file is already in `.gitignore` and will not be committed

### 🛡️ Best Practices

1. **Change Default Secrets**: All SECRET_KEY values should be changed before production deployment
2. **Use Environment Variables**: Store sensitive configuration in environment variables
3. **Review Dependencies**: Keep all Python packages up to date with security patches
4. **Network Security**: These demos run on localhost by default - configure firewalls appropriately for production

### 🚀 Generating Secure Keys

For Flask SECRET_KEY, you can generate a secure random key using Python:

```python
import secrets
print(secrets.token_hex(32))
```

Or in bash:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Reporting Security Issues

If you discover a security vulnerability, please email the repository maintainer rather than opening a public issue.
