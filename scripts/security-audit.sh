#!/bin/bash

# NBA Sports Betting Compiler - Security Audit Script

echo "🔒 Running Security Audit..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ISSUES_FOUND=0

# Function to report issues
report_issue() {
    echo -e "${RED}❌ $1${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

report_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

report_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 1. Check for secrets in code
echo -e "${BLUE}🔍 Scanning for secrets in codebase...${NC}"

# Check for potential API keys (more specific patterns to avoid false positives)
if grep -r -E "(api[_-]?key\s*=\s*['\"][a-zA-Z0-9]{20,}['\"])" --include="*.py" --include="*.js" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v "node_modules" | grep -v "venv" | grep -v "test" | grep -v "@types" | head -5 | grep -q .; then
    report_issue "Found potential hardcoded API keys"
else
    report_success "No hardcoded API keys found"
fi

# Check for passwords (more specific patterns to avoid false positives)
if grep -r -E "(password\s*=\s*['\"][a-zA-Z0-9]{8,}['\"])" --include="*.py" --include="*.js" --include="*.ts" . 2>/dev/null | grep -v "node_modules" | grep -v "venv" | grep -v "test" | grep -v "@types" | head -5 | grep -q .; then
    report_issue "Found potential hardcoded passwords"
else
    report_success "No hardcoded passwords found"
fi

# Check for database URLs with credentials
if grep -r "://.*:.*@" --include="*.py" --include="*.js" --include="*.ts" . 2>/dev/null | grep -v "node_modules" | grep -v "venv" | grep -v ".git" | grep -v "user:password" | grep -v "example" | grep -v "test" | grep -v "@types" | head -5 | grep -q .; then
    report_issue "Found potential database credentials"
else
    report_success "No database credentials in application code"
fi

# 2. Check file permissions
echo -e "${BLUE}🔐 Checking file permissions...${NC}"

# Check for overly permissive files
if find . -type f -perm -o+w -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.pytest_cache/*" | head -5 | grep -q .; then
    report_warning "Found world-writable files"
else
    report_success "File permissions look good"
fi

# 3. Check environment files
echo -e "${BLUE}📁 Checking environment files...${NC}"

# Check if .env files exist and are properly protected
if [ -f "backend/.env" ]; then
    if [ "$(stat -f %A backend/.env 2>/dev/null || stat -c %a backend/.env 2>/dev/null)" != "600" ]; then
        report_warning ".env file should have 600 permissions"
    else
        report_success ".env file permissions are secure"
    fi
fi

# Check if .env files are in .gitignore
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore; then
        report_success ".env files are in .gitignore"
    else
        report_warning ".env files should be in .gitignore"
    fi
fi

# 4. Dependency security check
echo -e "${BLUE}📦 Checking dependencies...${NC}"

# Check Python dependencies
if [ -f "backend/requirements.txt" ]; then
    if command -v safety >/dev/null 2>&1; then
        cd backend
        if safety check --json >/dev/null 2>&1; then
            report_success "Python dependencies are secure"
        else
            report_issue "Found vulnerabilities in Python dependencies"
        fi
        cd ..
    else
        report_warning "Install 'safety' to check Python dependencies: pip install safety"
    fi
fi

# Check Node dependencies
if [ -f "frontend/package.json" ]; then
    cd frontend
    if npm audit --audit-level=high --progress=false >/dev/null 2>&1; then
        report_success "Node dependencies are secure"
    else
        report_warning "Found vulnerabilities in Node dependencies (run 'npm audit' for details)"
    fi
    cd ..
fi

# 5. Check for debug/development code in production files
echo -e "${BLUE}🐛 Checking for debug code...${NC}"

# Check for console.log in production files
if grep -r "console\.log\|console\.debug\|debugger" frontend/src/ 2>/dev/null | grep -v "test" | grep -v "__tests__" | grep -v "setupTests" | head -3 | grep -q .; then
    report_warning "Found console.log/debugger statements (consider removing for production)"
else
    report_success "No debug statements found in production code"
fi

# Check for TODO/FIXME with security implications
if grep -r -i "todo.*secur\|fixme.*secur\|hack.*secur" . --include="*.py" --include="*.js" --include="*.ts" 2>/dev/null | head -3 | grep -q .; then
    report_warning "Found security-related TODOs/FIXMEs"
else
    report_success "No security-related TODOs found"
fi

# 6. Check CORS and security headers
echo -e "${BLUE}🌐 Security configuration check...${NC}"

# Check CORS configuration
if grep -r "allow_origins.*\*" backend/ 2>/dev/null | grep -q .; then
    report_warning "CORS allows all origins - consider restricting for production"
else
    report_success "CORS configuration looks secure"
fi

# Summary
echo ""
echo "🔒 Security Audit Complete"
echo "=========================="

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No critical security issues found!${NC}"
    echo -e "${GREEN}🛡️  Your codebase appears secure.${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $ISSUES_FOUND security issues that need attention.${NC}"
    echo -e "${YELLOW}🔧 Please review and fix the issues above.${NC}"
    exit 1
fi