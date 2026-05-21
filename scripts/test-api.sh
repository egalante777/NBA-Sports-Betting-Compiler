#!/bin/bash

# NBA Sports Betting Compiler - API Test Script

echo "🏀 Testing NBA Betting Compiler API..."

# Test health endpoint
echo "📊 Testing health endpoint..."
health_response=$(curl -s http://localhost:8000/health)
if [[ $health_response == *"healthy"* ]]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "Response: $health_response"
    exit 1
fi

# Test games endpoint
echo "🏀 Testing games endpoint..."
games_response=$(curl -s http://localhost:8000/api/games/today)
game_count=$(echo $games_response | jq '. | length')
if [[ $game_count -gt 0 ]]; then
    echo "✅ Games endpoint working - Found $game_count games"
else
    echo "❌ Games endpoint failed or no games found"
    echo "Response: $games_response"
    exit 1
fi

# Test complete games with best bets
echo "🎯 Testing best bets endpoint..."
bets_response=$(curl -s http://localhost:8000/api/games/)
first_game_id=$(echo $bets_response | jq -r '.[0].id')
bet_count=$(echo $bets_response | jq '.[0].best_bets | length')
if [[ $bet_count -gt 0 ]]; then
    echo "✅ Best bets working - Found $bet_count recommendations for game $first_game_id"
else
    echo "❌ Best bets failed or no recommendations found"
    exit 1
fi

# Test frontend
echo "🌐 Testing frontend..."
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [[ $frontend_response -eq 200 ]]; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend not accessible (HTTP $frontend_response)"
    exit 1
fi

echo ""
echo "🎉 All tests passed!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
echo "📋 Sample API Endpoints:"
echo "  GET /health - Health check"
echo "  GET /api/games/today - Today's games"
echo "  GET /api/games/ - All games with best bets"
echo "  GET /api/games/{id}/odds - Odds for specific game"
echo "  GET /api/games/{id}/best-bets - Best bets for specific game"