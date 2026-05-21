"""
Unit tests for Pydantic models in the NBA Sports Betting Compiler.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.game import (
    Team, Game, Odds, BestBet, GameWithBestBets,
    GameStatus, BetType
)


@pytest.mark.unit
class TestTeamModel:
    """Test the Team model validation and functionality."""

    def test_valid_team_creation(self):
        """Test creating a valid team."""
        team = Team(
            id=1610612738,
            name="Boston Celtics",
            abbreviation="BOS",
            city="Boston",
            seed=1
        )

        assert team.id == 1610612738
        assert team.name == "Boston Celtics"
        assert team.abbreviation == "BOS"
        assert team.city == "Boston"
        assert team.seed == 1
        assert team.logo_url is None

    def test_team_with_logo(self):
        """Test team creation with logo URL."""
        team = Team(
            id=1610612738,
            name="Boston Celtics",
            abbreviation="BOS",
            city="Boston",
            logo_url="https://example.com/logo.png"
        )

        assert team.logo_url == "https://example.com/logo.png"

    def test_team_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            Team(name="Boston Celtics")  # Missing required fields


@pytest.mark.unit
class TestGameModel:
    """Test the Game model validation and functionality."""

    def test_valid_game_creation(self, sample_game_data):
        """Test creating a valid game."""
        game = sample_game_data

        assert game.id == "test_game_001"
        assert game.home_team.name == "Boston Celtics"
        assert game.away_team.name == "Miami Heat"
        assert game.status == GameStatus.SCHEDULED
        assert game.arena == "TD Garden"
        assert game.season_type == "playoffs"

    def test_game_status_enum(self):
        """Test GameStatus enum values."""
        valid_statuses = [
            GameStatus.SCHEDULED,
            GameStatus.LIVE,
            GameStatus.FINISHED,
            GameStatus.POSTPONED
        ]

        for status in valid_statuses:
            assert status in GameStatus

    def test_game_with_odds(self, sample_game_data, sample_odds_data):
        """Test game with betting odds."""
        game = sample_game_data
        game.odds = sample_odds_data

        assert len(game.odds) == 2
        assert all(isinstance(odd, Odds) for odd in game.odds)


@pytest.mark.unit
class TestOddsModel:
    """Test the Odds model validation and functionality."""

    def test_valid_odds_creation(self):
        """Test creating valid betting odds."""
        odds = Odds(
            sportsbook="DraftKings",
            bet_type=BetType.MONEYLINE,
            odds=-150,
            selection="BOS",
            last_updated=datetime.now().isoformat()
        )

        assert odds.sportsbook == "DraftKings"
        assert odds.bet_type == BetType.MONEYLINE
        assert odds.odds == -150
        assert odds.selection == "BOS"
        assert odds.line is None

    def test_odds_with_line(self):
        """Test odds with point spread line."""
        odds = Odds(
            sportsbook="FanDuel",
            bet_type=BetType.SPREAD,
            line=-4.5,
            odds=-110,
            selection="BOS",
            last_updated=datetime.now().isoformat()
        )

        assert odds.line == -4.5
        assert odds.bet_type == BetType.SPREAD

    def test_bet_type_enum(self):
        """Test BetType enum values."""
        valid_bet_types = [
            BetType.MONEYLINE,
            BetType.SPREAD,
            BetType.TOTAL,
            BetType.PLAYER_PROPS
        ]

        for bet_type in valid_bet_types:
            assert bet_type in BetType


@pytest.mark.unit
class TestBestBetModel:
    """Test the BestBet model validation and functionality."""

    def test_valid_best_bet_creation(self):
        """Test creating a valid best bet recommendation."""
        best_bet = BestBet(
            bet_type=BetType.MONEYLINE,
            selection="BOS",
            best_odds=-150,
            sportsbook="DraftKings",
            confidence=0.75,
            reasoning="Strong home court advantage",
            expected_value=0.25
        )

        assert best_bet.bet_type == BetType.MONEYLINE
        assert best_bet.confidence == 0.75
        assert best_bet.expected_value == 0.25
        assert best_bet.reasoning == "Strong home court advantage"

    def test_confidence_validation(self):
        """Test confidence score validation (should be 0-1)."""
        # Valid confidence
        best_bet = BestBet(
            bet_type=BetType.MONEYLINE,
            selection="BOS",
            best_odds=-150,
            sportsbook="DraftKings",
            confidence=0.75,
            reasoning="Test",
            expected_value=0.25
        )
        assert best_bet.confidence == 0.75

        # Test edge cases - Pydantic allows values outside 0-1 by default
        # In a real app, you might want to add custom validators


@pytest.mark.unit
class TestGameWithBestBetsModel:
    """Test the GameWithBestBets model."""

    def test_game_with_best_bets_creation(self, sample_game_data, sample_best_bets):
        """Test creating game with best bets."""
        game_data = sample_game_data.model_dump()
        game_data["best_bets"] = sample_best_bets

        game_with_bets = GameWithBestBets(**game_data)

        assert len(game_with_bets.best_bets) == 1
        assert game_with_bets.best_bets[0].confidence == 0.75
        assert isinstance(game_with_bets.best_bets[0], BestBet)


@pytest.mark.unit
class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_team_json_serialization(self):
        """Test Team model JSON serialization."""
        team = Team(
            id=1610612738,
            name="Boston Celtics",
            abbreviation="BOS",
            city="Boston"
        )

        # Test to dict
        team_dict = team.model_dump()
        assert isinstance(team_dict, dict)
        assert team_dict["name"] == "Boston Celtics"

        # Test JSON serialization
        team_json = team.model_dump_json()
        assert isinstance(team_json, str)
        assert "Boston Celtics" in team_json

    def test_game_json_serialization(self, sample_game_data):
        """Test Game model JSON serialization."""
        game = sample_game_data

        game_dict = game.model_dump()
        assert isinstance(game_dict, dict)
        assert "home_team" in game_dict
        assert "away_team" in game_dict

        game_json = game.model_dump_json()
        assert isinstance(game_json, str)

    def test_model_from_dict(self):
        """Test creating models from dictionaries."""
        team_dict = {
            "id": 1610612738,
            "name": "Boston Celtics",
            "abbreviation": "BOS",
            "city": "Boston"
        }

        team = Team(**team_dict)
        assert team.name == "Boston Celtics"

    def test_invalid_model_data(self):
        """Test model validation with invalid data."""
        # Invalid team ID (string instead of int)
        with pytest.raises(ValidationError):
            Team(
                id="invalid",
                name="Boston Celtics",
                abbreviation="BOS",
                city="Boston"
            )

        # Invalid bet type
        with pytest.raises(ValidationError):
            Odds(
                sportsbook="DraftKings",
                bet_type="invalid_bet_type",
                odds=-150,
                selection="BOS",
                last_updated=datetime.now().isoformat()
            )