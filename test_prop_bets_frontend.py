#!/usr/bin/env python3
"""
Create mock prop bets to test frontend display
"""
import json

# Mock data with prop bets for frontend testing
mock_game_with_props = {
    "id": "nba_2026-05-20_401873341",
    "home_team": {
        "id": 18,
        "name": "Knicks",
        "abbreviation": "NYK",
        "city": "New York",
        "seed": 2
    },
    "away_team": {
        "id": 5,
        "name": "Cavaliers",
        "abbreviation": "CLE",
        "city": "Cleveland",
        "seed": 4
    },
    "scheduled_time": "2026-05-20T20:00:00",
    "status": "scheduled",
    "arena": "Madison Square Garden",
    "series": "Eastern Conference First Round - Game 7",
    "season_type": "playoffs",
    "best_bets": [
        # Main bets
        {
            "bet_type": "moneyline",
            "selection": "New York Knicks",
            "best_odds": -185,
            "sportsbook": "FanDuel",
            "confidence": 0.72,
            "reasoning": "Knicks home court advantage in Game 7 creates significant value opportunity.",
            "expected_value": 0.08
        },
        {
            "bet_type": "spread",
            "selection": "Cleveland Cavaliers",
            "line": 4.5,
            "best_odds": -110,
            "sportsbook": "DraftKings",
            "confidence": 0.68,
            "reasoning": "Cavaliers spread offers contrarian value in hostile environment.",
            "expected_value": 0.05
        },
        {
            "bet_type": "total",
            "selection": "under",
            "line": 215.5,
            "best_odds": -115,
            "sportsbook": "BetMGM",
            "confidence": 0.65,
            "reasoning": "Game 7 defensive intensity typically favors under totals.",
            "expected_value": 0.03
        },
        # Prop bets
        {
            "bet_type": "player_points",
            "selection": "over",
            "line": 28.5,
            "best_odds": -105,
            "sportsbook": "FanDuel",
            "player_name": "Jalen Brunson",
            "confidence": 0.78,
            "reasoning": "Brunson points prop presents strong analytical edge in elimination game.",
            "expected_value": 0.12
        },
        {
            "bet_type": "player_rebounds",
            "selection": "over",
            "line": 12.5,
            "best_odds": +120,
            "sportsbook": "DraftKings",
            "player_name": "Jarrett Allen",
            "confidence": 0.75,
            "reasoning": "Allen rebounding opportunity enhanced by game pace and intensity.",
            "expected_value": 0.15
        },
        {
            "bet_type": "player_assists",
            "selection": "over",
            "line": 6.5,
            "best_odds": -110,
            "sportsbook": "Caesars",
            "player_name": "Darius Garland",
            "confidence": 0.71,
            "reasoning": "Garland assist total leverages Cavaliers' offensive system in crucial game.",
            "expected_value": 0.09
        }
    ]
}

print("🎯 Mock Game Data with Prop Bets:")
print("=" * 50)
print(json.dumps(mock_game_with_props, indent=2))

# Show separated bets
main_bets = [bet for bet in mock_game_with_props["best_bets"]
             if bet["bet_type"] in ["moneyline", "spread", "total"]]
prop_bets = [bet for bet in mock_game_with_props["best_bets"]
             if bet["bet_type"] not in ["moneyline", "spread", "total"]]

print(f"\n📊 Analysis:")
print(f"Main Bets: {len(main_bets)}")
print(f"Prop Bets: {len(prop_bets)}")

print(f"\n🏀 Prop Bets Preview:")
for prop in prop_bets:
    player = prop.get("player_name", "Team")
    print(f"  - {player} {prop['selection']} {prop['line']} ({prop['bet_type'].replace('_', ' ').title()})")
    print(f"    Confidence: {int(prop['confidence'] * 100)}% | EV: +{int(prop['expected_value'] * 100)}%")