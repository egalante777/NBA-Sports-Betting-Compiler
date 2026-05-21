#!/bin/bash
# API Credit Conservation Status Check

echo "🔍 NBA Betting Compiler - API Conservation Status"
echo "=================================================="

# Load environment variables from .env file if it exists
if [ -f "backend/.env" ]; then
    source backend/.env
fi

# Check if ODDS_API_KEY is set
if [ -z "$ODDS_API_KEY" ]; then
    echo "❌ ODDS_API_KEY not set - odds API disabled"
else
    echo "✅ ODDS_API_KEY found: ${ODDS_API_KEY:0:8}..."
fi

# Check prop bets setting
if [ "$ENABLE_PROP_BETS" = "true" ]; then
    echo "🎯 Prop bets: ENABLED (uses 4x more credits)"
else
    echo "💰 Prop bets: DISABLED (credit conservation mode)"
fi

# Check if servers are running
if pgrep -f "uvicorn.*8000" > /dev/null; then
    echo "🟢 Backend server: RUNNING on port 8000"
else
    echo "🔴 Backend server: STOPPED"
fi

if pgrep -f "node.*3000" > /dev/null; then
    echo "🟢 Frontend server: RUNNING on port 3000"
else
    echo "🔴 Frontend server: STOPPED"
fi

echo ""
echo "💡 Credit Conservation Tips:"
echo "   - Each game odds request = 1 credit"
echo "   - Prop bets multiply credit usage by 4x"
echo "   - Caching active for 5 minutes"
echo "   - Stop servers with 'make stop' when not testing"
echo "   - Run 'python test_api_conservation.py' to test caching"