# NBA Sports Betting Compiler - API Setup Guide

## 🎯 **Required API Keys**

This application requires **real data sources** for production use. Mock data has been completely removed to ensure reliability and accuracy.

### **1. The Odds API (REQUIRED for betting odds)**

**What it provides:**
- Live betting odds from major sportsbooks (DraftKings, FanDuel, BetMGM, etc.)
- Moneyline, point spread, and over/under totals
- Real-time line movements and updates

**How to get it:**
1. Visit [https://the-odds-api.com/](https://the-odds-api.com/)
2. Sign up for an account
3. Choose a plan:
   - **Free tier**: 500 requests/month (good for development)
   - **Pro tier**: $100/month for 100,000 requests (recommended for production)

**Setup:**
1. Copy your API key from the dashboard
2. Add it to your `.env` file:
   ```bash
   # backend/.env
   ODDS_API_KEY=your_api_key_here
   ```

### **2. NBA Data Sources (FREE)**

The application automatically uses free NBA APIs:

- **ESPN Sports API**: Game schedules, team info, scores (no key required)
- **NBA Stats API**: Official NBA data (no key required)
- **BalldontLie API**: Backup NBA data (no key required)

## 🚀 **Setup Instructions**

### **Step 1: Configure API Key**
```bash
cd backend
cp .env.example .env  # If you don't have .env yet
echo "ODDS_API_KEY=your_actual_api_key" >> .env
```

### **Step 2: Test Configuration**
```bash
# Start the development environment
make dev

# In another terminal, test the API
curl http://localhost:8000/api/games/data-source

# Should return:
{
  "data_source": "real",
  "odds_api_configured": true,
  "available_sources": {
    "espn": "Free NBA game data and scores",
    "odds_api": "Premium betting odds (requires API key)",
    "balldontlie": "Free NBA stats and game data"
  }
}
```

### **Step 3: Verify Full Functionality**
```bash
# Test getting games with betting odds
curl http://localhost:8000/api/games/

# Should return real NBA games with betting analysis
```

## 🔧 **Troubleshooting**

### **Error: "ODDS_API_KEY environment variable is required"**
- **Solution**: Add your API key to the `.env` file as shown above

### **Error: "Invalid ODDS_API_KEY"**
- **Solution**: Double-check your API key in The Odds API dashboard
- Make sure there are no extra spaces or characters

### **Error: "Odds API quota exceeded"**
- **Solution**: Upgrade your The Odds API plan or wait for quota reset

### **No games returned****
- **Possible cause**: No NBA games scheduled today
- **Solution**: Check ESPN or NBA.com for current game schedule

## 💰 **Cost Estimation**

**The Odds API pricing:**
- Development (Free tier): $0/month - 500 requests
- Light production: $100/month - 100,000 requests  
- Heavy production: $200+/month - 500,000+ requests

**Request usage:**
- Each game analysis: ~3-5 API requests
- Typical daily usage: 50-200 requests (5-20 games)
- Monthly estimate: 1,500-6,000 requests

**Recommendation:** Start with the free tier for development, then upgrade to Pro ($100/month) for production.

## 🔒 **Security Notes**

- **Never commit API keys to git**
- **Use different API keys for development vs production**
- **Monitor your API usage in The Odds API dashboard**
- **Set up usage alerts to avoid unexpected charges**

## 📊 **Data Sources Summary**

| Data Type | Source | Cost | Setup Required |
|-----------|--------|------|----------------|
| NBA Games | ESPN API | Free | None |
| Team Info | NBA Stats API | Free | None |
| Betting Odds | The Odds API | $100/month | API Key Required |
| Backup Data | BalldontLie API | Free | None |

## 🚀 **Ready for Production**

Once configured with real API keys, your NBA Sports Betting Compiler will provide:
- ✅ Real NBA game schedules and team data
- ✅ Live betting odds from major sportsbooks
- ✅ Professional-grade betting analysis
- ✅ No mock or simulated data