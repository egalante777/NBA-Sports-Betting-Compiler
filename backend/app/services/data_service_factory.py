"""
Data Service Factory - Production NBA data sources only

Required Environment Variables:
- ODDS_API_KEY: Required for real betting odds from The Odds API
"""

import os
from .real_nba_service import RealNBAService

class DataServiceFactory:
    @staticmethod
    def get_nba_service():
        """
        Factory method to return the NBA service - production ready with real data only
        """
        print("🔴 Using REAL NBA data sources (ESPN API, The Odds API)")
        return RealNBAService()

    @staticmethod
    def get_service_info():
        """Get information about current data source configuration"""
        odds_api_key = os.getenv('ODDS_API_KEY', '')

        return {
            'data_source': 'real',
            'odds_api_configured': bool(odds_api_key),
            'available_sources': {
                'espn': 'Free NBA game data and scores',
                'odds_api': 'Premium betting odds (requires API key)',
                'balldontlie': 'Free NBA stats and game data'
            }
        }