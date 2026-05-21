# Security Policy

## 🔒 Security Overview

The NBA Sports Betting Compiler follows security best practices for handling API keys, user data, and external integrations.

## 🚨 Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it by:

1. **Do NOT open a public issue** 
2. Email the maintainers directly (contact info in package.json)
3. Include detailed steps to reproduce the vulnerability
4. Allow time for assessment and patching before public disclosure

## 🛡️ Security Measures Implemented

### API Key Protection
- ✅ Environment variables in `.env` files (not committed to git)
- ✅ `.env` files have restricted permissions (600)
- ✅ `.env.example` template with safe placeholders
- ✅ Comprehensive `.gitignore` to prevent accidental commits

### Input Validation
- ✅ Pydantic models for API request/response validation
- ✅ TypeScript interfaces for frontend type safety
- ✅ CORS configuration for allowed origins

### Testing Security
- ✅ Automated secrets scanning in test suite
- ✅ No hardcoded credentials in codebase
- ✅ HTTP mocking for tests (no real API calls during testing)

### Dependencies
- ✅ Regular dependency auditing with `npm audit` and `safety`
- ⚠️ Some development dependency vulnerabilities exist (low risk for production)

## 🔧 Security Setup Instructions

### 1. Environment Configuration
```bash
# Copy the example file and add your API keys
cp backend/.env.example backend/.env

# Set secure permissions
chmod 600 backend/.env

# Add your real API key (get from https://the-odds-api.com/)
# Edit backend/.env:
ODDS_API_KEY=your_real_api_key_here
```

### 2. Run Security Audit
```bash
# Run comprehensive security scan
make test-security

# Check Node.js dependencies
cd frontend && npm audit

# Check Python dependencies (install safety first)
cd backend && pip install safety && safety check
```

### 3. Pre-commit Security Checks
Before committing code:
```bash
# 1. Ensure no secrets in code
grep -r "api.key\|password\|secret" . --exclude-dir=node_modules --exclude-dir=venv

# 2. Check .env is in .gitignore
git check-ignore backend/.env  # Should return the path

# 3. Run security tests
make test-security
```

## 🚫 What NOT to Commit

Never commit these files/patterns:
- `backend/.env` (real environment variables)
- API keys, passwords, or tokens
- Database connection strings
- Private keys or certificates
- User data or PII

## ✅ Safe to Commit

These are safe for public repositories:
- `backend/.env.example` (template with placeholders)
- Source code without hardcoded secrets
- Configuration files with placeholder values
- Documentation and README files

## 🔍 Known Security Considerations

### Development Dependencies
- Some `npm audit` vulnerabilities exist in development dependencies
- These affect testing/build tools, not production runtime
- Monitor regularly and update when stable fixes are available

### API Rate Limiting
- The Odds API has monthly credit limits (500/month default)
- Caching implemented to prevent excessive API calls
- Consider rate limiting in production deployments

### CORS Configuration
- Currently allows all origins for development
- Restrict to specific domains for production deployment
- Update `FRONTEND_URL` environment variable accordingly

## 🚀 Production Security Recommendations

For production deployments:

1. **Environment Variables**
   - Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
   - Never store secrets in container images or version control

2. **Network Security**
   - Deploy behind HTTPS/TLS
   - Use proper CORS configuration
   - Consider API rate limiting and authentication

3. **Monitoring**
   - Enable logging for security events
   - Monitor for unusual API usage patterns
   - Set up alerts for security scanning results

4. **Updates**
   - Regularly update dependencies
   - Monitor security advisories
   - Test security patches in staging first

## 📞 Contact

For security-related questions or reports:
- Check the contact information in `package.json`
- Use responsible disclosure practices
- Allow reasonable time for patches before public disclosure

---

**Last Updated:** May 21, 2026  
**Next Security Review:** Recommended quarterly or after major updates