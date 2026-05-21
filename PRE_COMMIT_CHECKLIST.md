# 🔒 Pre-Commit Security Checklist

**MANDATORY**: Complete this checklist before every commit to prevent security issues.

## ✅ Security Validation Steps

### 1. Environment Files Check
```bash
# ✅ Verify .env files are NOT committed
git status | grep -E "\.env$"
# Result should be empty (no .env files in git staging)

# ✅ Verify .env has placeholder values only
cat backend/.env | grep -E "your_.*_here|example|placeholder"
# Should see placeholder values, NOT real API keys
```

### 2. Secrets Scanning
```bash
# ✅ Run automated secrets scan
make test-security
# Should show: "✅ No critical security issues found!"

# ✅ Manual check for common secrets
grep -r -i "sk_\|pk_\|api.*key.*=" . --exclude-dir=node_modules --exclude-dir=venv --exclude="*.example"
# Should return no results or only placeholder examples
```

### 3. File Permissions
```bash
# ✅ Verify .env has secure permissions
ls -la backend/.env
# Should show: -rw------- (600 permissions)

# ✅ Check for any world-readable sensitive files
find . -name "*.key" -o -name "*.pem" -o -name "*secret*" -perm +004
# Should return no results
```

### 4. Git Configuration
```bash
# ✅ Verify .gitignore includes .env
grep -E "\.env$" .gitignore
# Should show: .env and backend/.env

# ✅ Check what's being committed
git diff --cached --name-only
# Review each file - should NOT include any .env files
```

### 5. Code Quality
```bash
# ✅ Run all tests
make test-all
# Should show: All tests passing

# ✅ Build successfully
make build
# Should complete without errors
```

## 🚨 RED FLAGS - DO NOT COMMIT IF YOU SEE:

- ❌ Real API keys (format: `ODDS_API_KEY=65781d4a...`)
- ❌ `.env` files in `git status` or `git diff --cached`
- ❌ Hardcoded passwords or tokens in source code
- ❌ Database connection strings with real credentials
- ❌ Private keys or certificates
- ❌ Console logs with sensitive data

## ✅ GREEN LIGHT - SAFE TO COMMIT:

- ✅ `.env.example` with placeholder values
- ✅ Source code with no hardcoded secrets
- ✅ All tests passing
- ✅ Security scan shows "No critical issues"
- ✅ `.env` files properly ignored by git

## 🛠️ If You Find Issues:

### Found real API key in code?
```bash
# 1. Remove the real key
sed -i 's/ODDS_API_KEY=.*/ODDS_API_KEY=your_api_key_here/' backend/.env

# 2. Re-run security scan
make test-security

# 3. Verify placeholder is in place
grep "your_api_key_here" backend/.env
```

### Found .env in git staging?
```bash
# 1. Remove from staging
git reset HEAD backend/.env

# 2. Verify it's ignored
git status | grep .env
# Should show nothing or "nothing to commit"
```

### Found hardcoded secrets in source code?
```bash
# 1. Replace with environment variable reference
# Example: Replace "api_key = 'abc123'" with "api_key = os.getenv('API_KEY')"

# 2. Add to .env.example as placeholder
echo "API_KEY=your_api_key_here" >> backend/.env.example

# 3. Re-run security scan
make test-security
```

## 📋 Quick Pre-Commit Command Sequence

Copy and paste this sequence before every commit:

```bash
# Security validation sequence
make test-security && \
git status | grep -E "\.env$" || echo "✅ No .env files staged" && \
grep -r "65781d4a\|your_real_\|sk_\|pk_" . --exclude-dir=node_modules --exclude-dir=venv || echo "✅ No hardcoded secrets found" && \
ls -la backend/.env | grep "^-rw-------" && echo "✅ .env permissions secure" && \
echo "🚀 Ready to commit!"
```

## 🎯 Remember:

> **"Better safe than sorry"** - Always run the security checks, even for small commits. It only takes a few seconds and prevents potentially expensive security incidents.

---

**Follow this checklist religiously - your future self will thank you! 🔒**