#!/usr/bin/env python3
"""
Test script to verify API credit conservation measures.
This shows how many API calls would be made vs cached responses.
"""
import os
import sys
import asyncio
from datetime import datetime

# Add backend to path
sys.path.append('/Users/egalante/Development/nba-sports-betting-compiler/backend')

from app.services.real_nba_service import RealNBAService

async def test_api_conservation():
    """Test the API caching and prop bet controls"""
    service = RealNBAService()

    print("🧪 Testing NBA Sports Betting API Conservation")
    print("=" * 50)

    # Check if API key is available
    if not service.odds_api_key:
        print("❌ No ODDS_API_KEY found - testing will use mock mode")
        return

    print(f"✅ ODDS_API_KEY found: {service.odds_api_key[:8]}...")

    # Check prop bets setting
    prop_bets_enabled = os.getenv("ENABLE_PROP_BETS", "false").lower() == "true"
    print(f"🎯 Prop bets enabled: {prop_bets_enabled}")

    # Test games fetching (free ESPN API)
    print("\n📊 Fetching NBA games (ESPN API - Free)...")
    games = await service.get_todays_games()
    print(f"   Found {len(games)} games")

    if games:
        game = games[0]
        print(f"   Test game: {game.away_team.name} @ {game.home_team.name}")

        # Test odds fetching (premium API - costs credits)
        print(f"\n💰 Testing odds API caching for game {game.id}...")

        # First call - should hit API
        print("   First call (should use API)...")
        start_time = datetime.now()
        try:
            odds1 = await service.get_real_odds(game.id)
            elapsed1 = (datetime.now() - start_time).total_seconds()
            print(f"   ✅ Retrieved {len(odds1)} odds in {elapsed1:.2f}s")

            # Second call - should use cache
            print("   Second call (should use cache)...")
            start_time = datetime.now()
            odds2 = await service.get_real_odds(game.id)
            elapsed2 = (datetime.now() - start_time).total_seconds()
            print(f"   ✅ Retrieved {len(odds2)} odds in {elapsed2:.2f}s")

            if elapsed2 < elapsed1 * 0.5:  # Cache should be much faster
                print("   🎯 Caching is working - second call much faster!")
            else:
                print("   ⚠️  Caching may not be working properly")

        except Exception as e:
            print(f"   ❌ API Error: {e}")

    print("\n💡 API Credit Conservation Tips:")
    print("   - Caching saves repeated calls (5-minute cache)")
    print("   - Prop bets disabled by default (saves credits)")
    print("   - Set ENABLE_PROP_BETS=true only when needed")
    print("   - ESPN API is free, only Odds API costs credits")

if __name__ == "__main__":
    asyncio.run(test_api_conservation())