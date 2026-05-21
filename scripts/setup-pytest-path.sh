#!/bin/bash

# NBA Sports Betting Compiler - Setup pytest in PATH

echo "🐍 Setting up pytest in your shell PATH..."

# Get the current project's pytest path
PROJECT_ROOT="/Users/egalante/Development/nba-sports-betting-compiler"
PYTEST_PATH="$PROJECT_ROOT/backend/venv/bin"

# Detect shell
if [[ "$SHELL" == */zsh* ]]; then
    SHELL_RC="$HOME/.zshrc"
    echo "📝 Detected zsh shell, updating $SHELL_RC"
elif [[ "$SHELL" == */bash* ]]; then
    SHELL_RC="$HOME/.bashrc"
    echo "📝 Detected bash shell, updating $SHELL_RC"
else
    echo "⚠️  Unknown shell: $SHELL"
    exit 1
fi

# Create alias and PATH addition
ALIAS_LINE="alias nba-pytest='cd $PROJECT_ROOT/backend && source venv/bin/activate && pytest'"
PATH_LINE="export PATH=\"$PYTEST_PATH:\$PATH\""

# Check if already added
if grep -q "nba-pytest" "$SHELL_RC" 2>/dev/null; then
    echo "✅ NBA pytest alias already exists in $SHELL_RC"
else
    echo "
# NBA Sports Betting Compiler - pytest setup
$ALIAS_LINE" >> "$SHELL_RC"
    echo "✅ Added NBA pytest alias to $SHELL_RC"
fi

# Alternative: Add the venv bin to PATH (optional)
echo "
💡 You can now use pytest in three ways:

1. Use the alias: 'nba-pytest' (recommended)
2. Use make command: 'make test-backend'
3. Activate venv manually:
   cd $PROJECT_ROOT/backend && source venv/bin/activate && pytest

To use the alias immediately, run:
source $SHELL_RC

Or restart your terminal.
"

# Show current pytest location
echo "🔍 Current pytest location: $PYTEST_PATH/pytest"

# Test if pytest is available
if [[ -f "$PYTEST_PATH/pytest" ]]; then
    echo "✅ pytest is installed and ready!"
    "$PYTEST_PATH/pytest" --version
else
    echo "❌ pytest not found. Run 'make setup' first."
fi