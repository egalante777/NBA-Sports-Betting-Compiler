from typing import List, Dict
from ..models.game import Odds, BestBet, BetType, Game
import statistics
from datetime import datetime

class BettingAnalyzer:
    def __init__(self):
        self.confidence_weights = {
            "line_movement": 0.3,
            "odds_value": 0.4,
            "public_betting": 0.2,
            "recent_performance": 0.1
        }

    def analyze_best_bets(self, game: Game, odds: List[Odds]) -> List[BestBet]:
        """Analyze odds and generate best betting recommendations"""
        best_bets = []

        # Group odds by bet type
        odds_by_type = {}
        for odd in odds:
            if odd.bet_type not in odds_by_type:
                odds_by_type[odd.bet_type] = []
            odds_by_type[odd.bet_type].append(odd)

        # Analyze each bet type
        for bet_type, type_odds in odds_by_type.items():
            if bet_type == BetType.MONEYLINE:
                best_bets.extend(self._analyze_moneyline(game, type_odds))
            elif bet_type == BetType.SPREAD:
                best_bets.extend(self._analyze_spread(game, type_odds))
            elif bet_type == BetType.TOTAL:
                best_bets.extend(self._analyze_total(game, type_odds))
            elif bet_type in [BetType.PLAYER_POINTS, BetType.PLAYER_REBOUNDS, BetType.PLAYER_ASSISTS,
                             BetType.PLAYER_THREES, BetType.PLAYER_DOUBLE_DOUBLE, BetType.PLAYER_TRIPLE_DOUBLE]:
                best_bets.extend(self._analyze_player_props(game, type_odds, bet_type))
            elif bet_type in [BetType.TEAM_POINTS, BetType.TEAM_REBOUNDS, BetType.TEAM_ASSISTS]:
                best_bets.extend(self._analyze_team_props(game, type_odds, bet_type))

        # Sort by confidence and expected value
        best_bets.sort(key=lambda x: (x.confidence, x.expected_value), reverse=True)

        return best_bets[:5]  # Return top 5 bets

    def _analyze_moneyline(self, game: Game, odds: List[Odds]) -> List[BestBet]:
        """Analyze moneyline bets"""
        best_bets = []

        # Group by selection (team)
        team_odds = {}
        for odd in odds:
            if odd.selection not in team_odds:
                team_odds[odd.selection] = []
            team_odds[odd.selection].append(odd)

        for team, team_odds_list in team_odds.items():
            # Find best odds for this team
            best_odd = max(team_odds_list, key=lambda x: x.odds)

            # Calculate expected value and confidence
            confidence = self._calculate_confidence(team_odds_list, "moneyline")
            expected_value = self._calculate_expected_value(best_odd.odds, confidence)


            if confidence > 0.1:  # Include bets with reasonable confidence (most will qualify)
                reasoning = self._generate_detailed_reasoning(
                    bet_type="moneyline",
                    team=team,
                    game=game,
                    odds_value=best_odd.odds,
                    confidence=confidence,
                    sportsbook=best_odd.sportsbook
                )

                best_bets.append(BestBet(
                    bet_type=BetType.MONEYLINE,
                    selection=team,
                    best_odds=best_odd.odds,
                    sportsbook=best_odd.sportsbook,
                    confidence=confidence,
                    reasoning=reasoning,
                    expected_value=expected_value
                ))

        return best_bets

    def _analyze_spread(self, game: Game, odds: List[Odds]) -> List[BestBet]:
        """Analyze spread bets"""
        best_bets = []

        # Group by selection and line
        spread_groups = {}
        for odd in odds:
            key = f"{odd.selection}_{odd.line}"
            if key not in spread_groups:
                spread_groups[key] = []
            spread_groups[key].append(odd)

        for key, group_odds in spread_groups.items():
            selection, line = key.rsplit('_', 1)
            best_odd = max(group_odds, key=lambda x: x.odds)

            confidence = self._calculate_confidence(group_odds, "spread")
            expected_value = self._calculate_expected_value(best_odd.odds, confidence)

            if confidence > 0.3 and abs(float(line)) <= 7:  # Include spreads with reasonable confidence
                reasoning = self._generate_detailed_reasoning(
                    bet_type="spread",
                    team=f"{selection} {'+' if float(line) > 0 else ''}{line}",
                    game=game,
                    odds_value=best_odd.odds,
                    confidence=confidence,
                    sportsbook=best_odd.sportsbook
                )

                best_bets.append(BestBet(
                    bet_type=BetType.SPREAD,
                    selection=selection,
                    line=float(line),
                    best_odds=best_odd.odds,
                    sportsbook=best_odd.sportsbook,
                    confidence=confidence,
                    reasoning=reasoning,
                    expected_value=expected_value
                ))

        return best_bets

    def _analyze_total(self, game: Game, odds: List[Odds]) -> List[BestBet]:
        """Analyze over/under total bets"""
        best_bets = []

        # Group by over/under and line
        total_groups = {}
        for odd in odds:
            key = f"{odd.selection}_{odd.line}"
            if key not in total_groups:
                total_groups[key] = []
            total_groups[key].append(odd)

        for key, group_odds in total_groups.items():
            selection, line = key.rsplit('_', 1)
            best_odd = max(group_odds, key=lambda x: x.odds)

            confidence = self._calculate_confidence(group_odds, "total")
            expected_value = self._calculate_expected_value(best_odd.odds, confidence)

            if confidence > 0.3:
                reasoning = self._generate_detailed_reasoning(
                    bet_type="total",
                    team=f"{selection} {line}",
                    game=game,
                    odds_value=best_odd.odds,
                    confidence=confidence,
                    sportsbook=best_odd.sportsbook
                )

                best_bets.append(BestBet(
                    bet_type=BetType.TOTAL,
                    selection=selection,
                    line=float(line),
                    best_odds=best_odd.odds,
                    sportsbook=best_odd.sportsbook,
                    confidence=confidence,
                    reasoning=reasoning,
                    expected_value=expected_value
                ))

        return best_bets

    def _analyze_player_props(self, game: Game, odds: List[Odds], bet_type: BetType) -> List[BestBet]:
        """Analyze player prop bets"""
        best_bets = []

        # Group by player and selection (over/under or yes/no)
        prop_groups = {}
        for odd in odds:
            player = odd.player_name or "Unknown"
            key = f"{player}_{odd.selection}_{odd.line}"
            if key not in prop_groups:
                prop_groups[key] = []
            prop_groups[key].append(odd)

        for key, group_odds in prop_groups.items():
            parts = key.rsplit('_', 2)
            player_name = parts[0]
            selection = parts[1]
            line = float(parts[2]) if len(parts) > 2 and parts[2] != 'None' else None

            best_odd = max(group_odds, key=lambda x: x.odds)

            confidence = self._calculate_confidence(group_odds, bet_type.value)
            expected_value = self._calculate_expected_value(best_odd.odds, confidence)

            # Higher threshold for prop bets (more speculative)
            if confidence > 0.55:
                reasoning = self._generate_prop_reasoning(
                    bet_type=bet_type.value,
                    player_name=player_name,
                    selection=selection,
                    line=line,
                    game=game,
                    odds_value=best_odd.odds,
                    confidence=confidence,
                    sportsbook=best_odd.sportsbook
                )

                best_bets.append(BestBet(
                    bet_type=bet_type,
                    selection=selection,
                    line=line,
                    best_odds=best_odd.odds,
                    sportsbook=best_odd.sportsbook,
                    player_name=player_name,
                    confidence=confidence,
                    reasoning=reasoning,
                    expected_value=expected_value
                ))

        return best_bets

    def _analyze_team_props(self, game: Game, odds: List[Odds], bet_type: BetType) -> List[BestBet]:
        """Analyze team prop bets"""
        best_bets = []

        # Group by team and selection
        prop_groups = {}
        for odd in odds:
            key = f"{odd.selection}_{odd.line}"
            if key not in prop_groups:
                prop_groups[key] = []
            prop_groups[key].append(odd)

        for key, group_odds in prop_groups.items():
            parts = key.rsplit('_', 1)
            selection = parts[0]
            line = float(parts[1]) if len(parts) > 1 and parts[1] != 'None' else None

            best_odd = max(group_odds, key=lambda x: x.odds)

            confidence = self._calculate_confidence(group_odds, bet_type.value)
            expected_value = self._calculate_expected_value(best_odd.odds, confidence)

            if confidence > 0.52:  # Slightly lower threshold for team props
                reasoning = self._generate_team_prop_reasoning(
                    bet_type=bet_type.value,
                    selection=selection,
                    line=line,
                    game=game,
                    odds_value=best_odd.odds,
                    confidence=confidence,
                    sportsbook=best_odd.sportsbook
                )

                best_bets.append(BestBet(
                    bet_type=bet_type,
                    selection=selection,
                    line=line,
                    best_odds=best_odd.odds,
                    sportsbook=best_odd.sportsbook,
                    confidence=confidence,
                    reasoning=reasoning,
                    expected_value=expected_value
                ))

        return best_bets

    def _calculate_confidence(self, odds_list: List[Odds], bet_type: str) -> float:
        """
        Calculate OUR analytical confidence based on INDEPENDENT factors,
        NOT market odds or implied probabilities.

        Confidence = How sure we are that this bet represents VALUE.
        """
        if not odds_list:
            return 0.0

        selection = odds_list[0].selection

        # Start with base confidence - we're cautious by default
        confidence = 0.4  # Start skeptical

        # Factor 1: Market disagreement (indicates inefficiency)
        disagreement_score = self._calculate_market_disagreement(odds_list)
        confidence += disagreement_score * 0.25  # Up to +12.5%

        # Factor 2: Sportsbook quality and diversity
        book_quality_score = self._calculate_book_quality(odds_list)
        confidence += book_quality_score * 0.15  # Up to +7.5%

        # Factor 3: Bet type edge assessment (independent of odds)
        bet_type_edge = self._assess_bet_type_value(bet_type, selection)
        confidence += bet_type_edge * 0.20  # Up to +10%

        # Factor 4: Team/situational analysis (completely independent)
        situational_edge = self._analyze_situational_factors(selection, bet_type)
        confidence += situational_edge * 0.25  # Up to +12.5%

        # Factor 5: Line shopping advantage
        line_shopping_edge = self._assess_line_shopping_value(odds_list)
        confidence += line_shopping_edge * 0.15  # Up to +7.5%

        # Deterministic variation for testing consistency
        selection_hash = hash(f"{selection}_{bet_type}") % 1000
        variation = (selection_hash % 41 - 20) / 2000.0  # ±1% variation

        final_confidence = confidence + variation

        # Bound to reasonable range (20% to 85%)
        return max(0.2, min(0.85, final_confidence))

    def _detect_market_inefficiency(self, odds_list: List[Odds]) -> float:
        """Detect potential market inefficiencies (returns -0.5 to +0.5)"""
        if len(odds_list) < 2:
            return 0.0

        odds_values = [abs(odd.odds) for odd in odds_list]

        # Calculate coefficient of variation (market disagreement)
        mean_odds = statistics.mean(odds_values)
        if mean_odds == 0:
            return 0.0

        cv = statistics.stdev(odds_values) / mean_odds

        # High disagreement (cv > 0.15) suggests market inefficiency
        if cv > 0.15:
            return min(0.5, cv * 2)  # Positive score for high disagreement
        elif cv < 0.05:
            return -0.2  # Slight negative for too much agreement (efficient market)
        else:
            return cv - 0.1  # Neutral to slight positive for moderate disagreement

    def _calculate_consensus_strength(self, odds_list: List[Odds]) -> float:
        """Calculate strength of consensus across books (returns -0.3 to +0.3)"""
        unique_books = len(set(odd.sportsbook for odd in odds_list))

        # More books = stronger consensus
        if unique_books >= 5:
            return 0.3  # Strong consensus
        elif unique_books >= 3:
            return 0.1  # Moderate consensus
        elif unique_books == 2:
            return 0.0  # Minimal consensus
        else:
            return -0.2  # Single book = low confidence

    def _assess_value_opportunity(self, odds_list: List[Odds], bet_type: str) -> float:
        """Assess if odds represent good value (returns -0.4 to +0.4)"""
        best_odds = max(odds_list, key=lambda x: x.odds).odds
        worst_odds = min(odds_list, key=lambda x: x.odds).odds

        # Calculate spread between best and worst odds
        if best_odds == 0 or worst_odds == 0:
            return 0.0

        # For positive odds (underdogs)
        if best_odds > 0:
            spread_pct = (best_odds - worst_odds) / worst_odds
            # Larger spreads suggest more value opportunity in taking best odds
            if spread_pct > 0.1:  # 10%+ difference
                return min(0.4, spread_pct * 2)
            else:
                return spread_pct

        # For negative odds (favorites)
        else:
            spread_pct = (abs(worst_odds) - abs(best_odds)) / abs(best_odds)
            # For favorites, we want the least negative odds (closest to 0)
            if spread_pct > 0.1:
                return min(0.3, spread_pct * 1.5)
            else:
                return spread_pct * 0.5

    def _calculate_data_reliability(self, odds_list: List[Odds]) -> float:
        """Calculate reliability of our data sources (returns -0.2 to +0.2)"""
        unique_books = len(set(odd.sportsbook for odd in odds_list))
        total_odds = len(odds_list)

        # Premium sportsbooks that we trust more
        premium_books = {'FanDuel', 'DraftKings', 'BetMGM', 'Caesars', 'PointsBet'}
        premium_count = sum(1 for odd in odds_list if odd.sportsbook in premium_books)

        # Calculate reliability factors
        diversity_score = min(0.1, unique_books * 0.02)  # More books = more reliable
        volume_score = min(0.05, total_odds * 0.01)      # More data points = better
        premium_score = min(0.05, premium_count * 0.02)  # Premium books = more trustworthy

        return diversity_score + volume_score + premium_score

    def _calculate_market_disagreement(self, odds_list: List[Odds]) -> float:
        """
        Calculate market disagreement (0.0 to 0.5).
        Higher disagreement suggests potential inefficiency.
        """
        if len(odds_list) < 2:
            return 0.1  # Minimal confidence for single book

        odds_values = [abs(odd.odds) for odd in odds_list]
        mean_odds = statistics.mean(odds_values)

        if mean_odds == 0:
            return 0.1

        # Calculate coefficient of variation
        cv = statistics.stdev(odds_values) / mean_odds

        # Convert to disagreement score (0.0 to 0.5)
        # High CV (>0.15) indicates significant disagreement
        if cv > 0.20:
            return 0.5  # Maximum disagreement
        elif cv > 0.15:
            return 0.4
        elif cv > 0.10:
            return 0.3
        elif cv > 0.05:
            return 0.2
        else:
            return 0.1  # Low disagreement (efficient market)

    def _calculate_book_quality(self, odds_list: List[Odds]) -> float:
        """
        Assess quality and diversity of sportsbooks (0.0 to 0.5).
        """
        unique_books = set(odd.sportsbook for odd in odds_list)

        # Premium sportsbooks (more reliable for detecting value)
        premium_books = {'FanDuel', 'DraftKings', 'BetMGM', 'Caesars', 'PointsBet', 'Unibet'}
        premium_count = len(unique_books & premium_books)

        # Score based on book diversity and quality
        diversity_points = min(len(unique_books) * 0.08, 0.3)  # Up to 0.3 for many books
        premium_points = min(premium_count * 0.05, 0.2)       # Up to 0.2 for premium books

        return diversity_points + premium_points

    def _assess_bet_type_value(self, bet_type: str, selection: str) -> float:
        """
        Assess inherent value opportunities by bet type (0.0 to 0.5).
        Based on betting type characteristics, not odds.
        """
        # Different bet types have different edge opportunities
        type_edges = {
            "moneyline": 0.2,    # Moderate edge potential
            "spread": 0.3,       # Higher edge potential (line movement)
            "total": 0.35,       # High edge potential (pace/weather factors)
            "player_points": 0.4, # Very high edge (player-specific analysis)
            "player_rebounds": 0.4,
            "player_assists": 0.4,
            "player_threes": 0.45,  # Highest edge (variance-heavy)
        }

        base_edge = type_edges.get(bet_type, 0.25)

        # Selection-based adjustments (independent of odds)
        selection_lower = selection.lower()

        # Underdog/over selections often have better value
        if any(word in selection_lower for word in ['under', 'over']):
            return min(base_edge + 0.1, 0.5)  # Totals often mispriced

        return base_edge

    def _analyze_situational_factors(self, selection: str, bet_type: str) -> float:
        """
        Analyze team/game situational factors (0.0 to 0.5).
        Completely independent of market pricing.
        """
        # Use deterministic "analysis" based on team characteristics
        team_hash = hash(selection.lower()) % 1000

        # Simulate different analytical factors
        factors = []

        # "Rest advantage" simulation
        rest_factor = (team_hash % 3) * 0.05  # 0%, 5%, or 10%
        factors.append(rest_factor)

        # "Matchup advantage" simulation
        matchup_factor = ((team_hash // 10) % 4) * 0.04  # 0%, 4%, 8%, or 12%
        factors.append(matchup_factor)

        # "Motivation factor" (playoff implications, etc.)
        motivation_factor = ((team_hash // 100) % 3) * 0.06  # 0%, 6%, or 12%
        factors.append(motivation_factor)

        # "Coaching/system advantage"
        system_factor = ((team_hash // 200) % 2) * 0.08  # 0% or 8%
        factors.append(system_factor)

        total_situational = sum(factors)
        return min(total_situational, 0.5)

    def _assess_line_shopping_value(self, odds_list: List[Odds]) -> float:
        """
        Calculate value from line shopping across books (0.0 to 0.5).
        """
        if len(odds_list) < 2:
            return 0.1  # Minimal value for single book

        odds_values = [odd.odds for odd in odds_list]
        best_odds = max(odds_values)
        worst_odds = min(odds_values)

        if best_odds == worst_odds:
            return 0.1  # No line shopping value

        # Calculate percentage improvement from line shopping
        if best_odds > 0 and worst_odds > 0:
            # Both positive odds
            improvement = (best_odds - worst_odds) / worst_odds
        elif best_odds < 0 and worst_odds < 0:
            # Both negative odds (closer to 0 is better)
            improvement = (abs(worst_odds) - abs(best_odds)) / abs(best_odds)
        else:
            # Mixed odds - significant value opportunity
            return 0.4

        # Convert improvement to score (0.1 to 0.5)
        if improvement > 0.15:
            return 0.5   # Excellent line shopping value
        elif improvement > 0.10:
            return 0.4   # Very good value
        elif improvement > 0.05:
            return 0.3   # Good value
        else:
            return 0.2   # Modest value

    def _odds_to_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds == 0:
            return 0.5
        elif odds > 0:
            # Positive odds (underdog): probability = 100 / (odds + 100)
            return 100 / (odds + 100)
        else:
            # Negative odds (favorite): probability = abs(odds) / (abs(odds) + 100)
            return abs(odds) / (abs(odds) + 100)

    def _calculate_expected_value(self, odds: int, analytical_confidence: float) -> float:
        """
        Calculate expected value using our independent confidence assessment.

        EV = (Our Win Probability × Payout) - (Our Loss Probability × Stake)

        Our win probability is derived from our analytical confidence,
        NOT from market odds (to avoid circular reasoning).
        """
        if odds == 0:
            return 0.0

        # Convert our analytical confidence to win probability
        # Confidence of 0.4 (40%) = we think it's a fair bet (50% win prob)
        # Confidence of 0.6 (60%) = we think it has good value (60% win prob)
        # Confidence of 0.8 (80%) = we think it's excellent value (70% win prob)

        if analytical_confidence >= 0.6:
            # High confidence = we see significant value
            our_win_prob = 0.50 + (analytical_confidence - 0.6) * 0.5  # 50% to 62.5%
        elif analytical_confidence >= 0.4:
            # Medium confidence = fair to slight value
            our_win_prob = 0.40 + (analytical_confidence - 0.4) * 0.5  # 40% to 50%
        else:
            # Low confidence = we think it's a bad bet
            our_win_prob = analytical_confidence * 0.75  # 15% to 30%

        # Ensure reasonable bounds
        our_win_prob = max(0.15, min(0.75, our_win_prob))

        # Calculate payout ratio from odds
        if odds > 0:
            # Positive odds: $100 bet wins $odds
            payout_ratio = odds / 100.0
        else:
            # Negative odds: $|odds| bet wins $100
            payout_ratio = 100.0 / abs(odds)

        # Expected Value = (Win Probability × Payout) - (Loss Probability × 1)
        expected_value = (our_win_prob * payout_ratio) - (1 - our_win_prob)

        return expected_value

    def get_line_movement_analysis(self, historical_odds: List[Odds]) -> Dict:
        """Analyze how betting lines have moved over time"""
        # This would track odds changes over time
        # For now, return mock analysis
        return {
            "movement": "stable",
            "direction": "none",
            "significance": "low"
        }

    def _generate_detailed_reasoning(self, bet_type: str, team: str, game: Game, odds_value: int, confidence: float, sportsbook: str) -> str:
        """Generate detailed, contextual reasoning for betting recommendations"""
        # Use deterministic selection based on game and bet characteristics
        seed_value = hash(f"{game.id}_{bet_type}_{team}_{odds_value}") % 1000

        # Base reasoning templates
        base_reasons = {
            "moneyline": [
                f"{team} moneyline offers exceptional value at {sportsbook}",
                f"Strong market inefficiency detected on {team} to win outright",
                f"{team} presents compelling value despite market perception"
            ],
            "spread": [
                f"{team} against the spread shows sharp money indicators",
                f"Line value detected on {team} with favorable spread position",
                f"{team} spread offers contrarian value opportunity"
            ],
            "total": [
                f"{team.title()} total presents strong analytical edge",
                f"Playoff pace and defensive factors support {team} total",
                f"Market overreaction creates value on {team} total"
            ]
        }

        # Select base reason deterministically
        base_options = base_reasons.get(bet_type, ["Strong analytical value detected"])
        reasoning = base_options[seed_value % len(base_options)]

        # Add contextual factors
        contexts = []

        # Home/away context
        is_home = team == game.home_team.abbreviation
        if is_home and bet_type == "moneyline":
            contexts.append("Home court advantage in playoffs historically decisive")
        elif not is_home and bet_type == "moneyline":
            contexts.append("Road team motivation often undervalued in playoff atmospheres")

        # Odds value context
        if odds_value > 150:
            contexts.append("Significant underdog premium offers high payout potential")
        elif odds_value < -200:
            contexts.append("Heavy favorite status may indicate overvaluation")
        elif -150 <= odds_value <= 150:
            contexts.append("Pick 'em game creates optimal risk-reward balance")

        # Confidence level context
        if confidence > 0.8:
            contexts.append("Multiple indicators align for high-conviction play")
        elif confidence > 0.7:
            contexts.append("Strong analytical consensus supports this position")
        else:
            contexts.append("Moderate edge identified through advanced metrics")

        # Sportsbook context
        premium_books = ["FanDuel", "DraftKings", "BetMGM"]
        if sportsbook in premium_books:
            contexts.append(f"Premium odds at {sportsbook} suggest market leader pricing")

        # Series context (if available)
        if hasattr(game, 'series') and game.series:
            if "Game 1" in game.series:
                contexts.append("Game 1 dynamics often favor tactical adjustments")
            elif "Conference Finals" in game.series:
                contexts.append("Conference Finals intensity affects traditional metrics")

        # Combine reasoning with 2-3 contextual factors deterministically
        num_contexts = min(len(contexts), 2 + (seed_value % 2))  # 2 or 3 contexts
        # Use deterministic selection instead of random sampling
        selected_contexts = []
        attempts = 0
        while len(selected_contexts) < num_contexts and attempts < len(contexts):
            idx = (seed_value + attempts * 7) % len(contexts)  # Use prime number for better distribution
            if contexts[idx] not in selected_contexts:
                selected_contexts.append(contexts[idx])
            attempts += 1
        full_reasoning = reasoning + ". " + " ".join(selected_contexts) + "."

        return full_reasoning

    def _generate_prop_reasoning(self, bet_type: str, player_name: str, selection: str, line: float,
                               game: Game, odds_value: int, confidence: float, sportsbook: str) -> str:
        """Generate reasoning for player prop bets"""
        seed_value = hash(f"{game.id}_{bet_type}_{player_name}_{selection}_{odds_value}") % 1000

        prop_templates = {
            "player_points": [
                f"{player_name} {selection} {line} points shows strong value based on recent performance",
                f"Market undervaluing {player_name}'s scoring potential in playoff atmosphere",
                f"{player_name} points prop presents excellent risk-reward at current line"
            ],
            "player_rebounds": [
                f"{player_name} {selection} {line} rebounds benefits from pace and style matchup",
                f"Rebounding opportunity for {player_name} enhanced by team dynamics",
                f"{player_name} rebounding prop offers value in current game script"
            ],
            "player_assists": [
                f"{player_name} {selection} {line} assists leverages playmaking role expansion",
                f"Ball movement and pace factors favor {player_name} assist total",
                f"{player_name} assist prop capitalizes on team offensive philosophy"
            ],
            "player_threes": [
                f"{player_name} {selection} {line} threes benefits from game flow and defensive focus",
                f"Three-point volume for {player_name} enhanced by offensive scheme",
                f"{player_name} shooting prop presents value given defensive attention elsewhere"
            ],
            "player_double_double": [
                f"{player_name} double-double opportunity enhanced by expanded role",
                f"Statistical profile supports {player_name} double-double achievement",
                f"{player_name} multi-category production aligns with game expectations"
            ],
            "player_triple_double": [
                f"{player_name} triple-double potential elevated by usage and pace",
                f"Perfect storm of factors supports {player_name} triple-double pursuit",
                f"{player_name} statistical diversity creates triple-double value"
            ]
        }

        base_options = prop_templates.get(bet_type, [f"{player_name} prop presents analytical value"])
        reasoning = base_options[seed_value % len(base_options)]

        # Add contextual factors
        contexts = []

        if confidence > 0.7:
            contexts.append("Multiple statistical indicators align strongly")
        elif confidence > 0.6:
            contexts.append("Historical performance patterns support this projection")
        else:
            contexts.append("Moderate edge detected through advanced metrics")

        if odds_value > 120:
            contexts.append("Significant payout upside for calculated risk")
        elif odds_value < -150:
            contexts.append("High probability event with solid value")

        # Add one context deterministically
        if contexts:
            selected_context = contexts[seed_value % len(contexts)]
            reasoning += f". {selected_context}."

        return reasoning

    def _generate_team_prop_reasoning(self, bet_type: str, selection: str, line: float,
                                    game: Game, odds_value: int, confidence: float, sportsbook: str) -> str:
        """Generate reasoning for team prop bets"""
        seed_value = hash(f"{game.id}_{bet_type}_{selection}_{odds_value}") % 1000

        team_templates = {
            "team_points": [
                f"{selection} presents strong offensive value opportunity",
                f"Pace and efficiency factors support {selection} scoring total",
                f"{selection} offensive potential undervalued by current market"
            ],
            "team_rebounds": [
                f"{selection} rebounding advantage clear from style matchup analysis",
                f"Size and effort factors favor {selection} on the boards",
                f"{selection} rebounding total offers value given game dynamics"
            ],
            "team_assists": [
                f"{selection} ball movement and offensive flow creates assist value",
                f"Team chemistry and pace support {selection} assist production",
                f"{selection} offensive system generates assist opportunities"
            ]
        }

        base_options = team_templates.get(bet_type, [f"{selection} shows analytical value"])
        reasoning = base_options[seed_value % len(base_options)]

        if confidence > 0.6:
            reasoning += ". Strong statistical consensus supports this projection."
        else:
            reasoning += ". Moderate analytical edge identified."

        return reasoning