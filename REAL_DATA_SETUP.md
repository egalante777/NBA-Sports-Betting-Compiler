# 🏀 Real NBA Data Integration Guide

This guide explains how to switch from mock data to real NBA game and betting odds data.

## 📊 Current Status: MOCK DATA

The application currently uses **hardcoded mock data** for development and demonstration. This includes:
- Fake playoff games (Celtics vs Heat, Warriors vs Lakers)
- Mock betting odds from DraftKings, FanDuel, BetMGM
- Generated game times and schedules

## 🔌 Real Data Sources Available

### 1. **Free NBA Game Data**

#### ESPN API (Recommended - Free)
```bash
# Endpoint: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard
# ✅ No API key required
# ✅ Real-time game data, scores, and schedules
# ✅ Team information and logos
# ✅ Game status (scheduled, live, finished)
```

#### NBA Official Data API (Free)
```bash
# Endpoint: https://data.nba.net/10s/prod/v1/{date}/scoreboard.json
# ✅ No API key required
# ✅ Official NBA data
# ⚠️ Limited documentation
```

#### balldontlie API (Free)
```bash
# Endpoint: https://www.balldontlie.io/api/v1/games
# ✅ No API key required
# ✅ Well-documented
# ⚠️ May have rate limits
```

### 2. **Premium Betting Odds Data**

#### The Odds API (Recommended - Paid)
```bash
# Endpoint: https://api.the-odds-api.com/v4/sports/basketball_nba/odds
# 💰 $10/month for 10,000 requests
# ✅ Real-time odds from 40+ sportsbooks
# ✅ Multiple bet types (moneyline, spread, totals)
# ✅ Historical data available

# Free tier: 500 requests/month
# Sign up: https://the-odds-api.com/
```

## 🚀 Quick Setup: Enable Real Data

### Option 1: Environment Variables (Recommended)
```bash
# In backend/.env file
USE_REAL_DATA=true
ODDS_API_KEY=your_odds_api_key_here
```

### Option 2: Makefile Command
```bash
# Add to Makefile for easy switching
make real-data    # Switch to real data
make mock-data    # Switch to mock data
```

### Option 3: Docker Environment
```yaml
# In docker-compose.yml
environment:
  - USE_REAL_DATA=true
  - ODDS_API_KEY=your_key_here
```

## 🔑 Getting API Keys

### The Odds API Setup
1. **Sign up:** https://the-odds-api.com/
2. **Get API key:** Dashboard → API Keys
3. **Free tier:** 500 requests/month
4. **Paid plans:** Start at $10/month

```bash
# Test your API key
curl "https://api.the-odds-api.com/v4/sports/basketball_nba/odds?apiKey=YOUR_KEY"
```

## 📝 Step-by-Step Integration

### 1. **Create Environment File**
```bash
cd backend
cp .env.example .env
```

### 2. **Add API Configuration**
```env
# backend/.env
USE_REAL_DATA=true
ODDS_API_KEY=your_odds_api_key_from_theoddsapi_com
ENVIRONMENT=development
```

### 3. **Test Real Data Endpoints**
```bash
# Check data source status
curl http://localhost:8000/api/games/data-source

# Test with real data
curl http://localhost:8000/api/games/today
```

### 4. **Verify Integration**
```bash
# Run health checks
make test

# Check API health
curl http://localhost:8000/api/games/data-source | jq .
```

## 🔄 Switching Between Data Sources

### Environment Variables
```bash
# Mock data (default)
export USE_REAL_DATA=false

# Real data
export USE_REAL_DATA=true
export ODDS_API_KEY=your_key_here
```

### Runtime Switching (Future Enhancement)
```python
# Add to API endpoints
POST /api/admin/switch-data-source
{
    "source": "real",  # or "mock"
    "odds_api_key": "optional_key"
}
```

## 🧪 Testing Real Data Integration

### 1. **API Health Check**
```bash
curl http://localhost:8000/api/games/data-source
```

Expected response:
```json
{
    "data_source": "real",
    "odds_api_configured": true,
    "api_health": {
        "espn": true,
        "odds_api": true,
        "balldontlie": true
    }
}
```

### 2. **Real Games Test**
```bash
curl http://localhost:8000/api/games/today | jq length
# Should return actual NBA games for today
```

### 3. **Real Odds Test**
```bash
curl http://localhost:8000/api/games/ | jq '.[0].odds | length'
# Should return real betting odds from multiple sportsbooks
```

## ⚡ Performance Considerations

### API Rate Limits
- **ESPN API:** ~100 requests/minute (unofficial)
- **The Odds API:** Based on your plan
- **balldontlie:** ~60 requests/minute

### Caching Strategy
```python
# Recommended caching
- Game schedules: Cache for 1 hour
- Live odds: Cache for 30 seconds
- Team data: Cache for 24 hours
```

### Error Handling
```python
# Fallback chain
ESPN API → NBA Data API → balldontlie → Mock Data
```

## 🔒 Security Best Practices

### API Key Management
```bash
# Never commit API keys to git
echo "*.env" >> .gitignore

# Use environment variables
export ODDS_API_KEY=your_key_here

# For production, use secrets management
# - AWS Secrets Manager
# - Google Secret Manager  
# - Azure Key Vault
```

### Rate Limiting
```python
# Add rate limiting to protect APIs
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/games/")
@limiter.limit("10/minute")
async def get_games():
    # Your endpoint logic
```

## 🚨 Common Issues & Solutions

### Issue: "No games found"
**Cause:** NBA off-season or no games today
**Solution:** 
```python
# Add date parameter to test with specific dates
curl "http://localhost:8000/api/games/today?date=2024-06-01"
```

### Issue: "Odds API key invalid"
**Cause:** Wrong API key or expired subscription
**Solution:**
```bash
# Test key directly
curl "https://api.the-odds-api.com/v4/sports/?apiKey=YOUR_KEY"
```

### Issue: "ESPN API rate limit"
**Cause:** Too many requests
**Solution:** Add caching or reduce request frequency

## 📈 Monitoring Real Data

### Key Metrics to Track
- API response times
- Success/error rates  
- Data freshness
- API quota usage

### Logging Setup
```python
import logging

logger = logging.getLogger("nba_data")
logger.info(f"Fetched {len(games)} games from ESPN API")
logger.warning(f"Odds API quota at {usage}%")
```

## 🎯 Next Steps After Integration

1. **Add Data Validation**
   - Verify game times and teams
   - Check odds for reasonableness
   - Flag suspicious data

2. **Enhance User Experience**
   - Show data source in UI
   - Add "last updated" timestamps
   - Display API health status

3. **Add Advanced Features**
   - Historical odds tracking
   - Line movement alerts
   - Injury impact analysis

---

**Ready to get real NBA data flowing? Set your API keys and flip the switch! 🏀**