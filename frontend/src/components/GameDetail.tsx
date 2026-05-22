import React from 'react';
import { GameWithBestBets, BetType } from '../types';
import {
  X,
  Clock,
  MapPin,
  TrendingUp,
  DollarSign,
  Target,
  BarChart3,
  Info,
  AlertTriangle
} from 'lucide-react';
import './GameDetail.css';

interface GameDetailProps {
  game: GameWithBestBets;
  onClose: () => void;
}

const GameDetail: React.FC<GameDetailProps> = ({ game, onClose }) => {
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatOdds = (odds: number) => {
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  const getBetTypeIcon = (betType: BetType) => {
    switch (betType) {
      case BetType.MONEYLINE:
        return <DollarSign size={20} />;
      case BetType.SPREAD:
        return <BarChart3 size={20} />;
      case BetType.TOTAL:
        return <Target size={20} />;
      default:
        return <Info size={20} />;
    }
  };

  const getBetTypeName = (betType: BetType) => {
    switch (betType) {
      case BetType.MONEYLINE:
        return 'Moneyline';
      case BetType.SPREAD:
        return 'Point Spread';
      case BetType.TOTAL:
        return 'Over/Under';
      default:
        return 'Special Bet';
    }
  };

  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return { level: 'High', color: '#28a745', icon: '🔥' };
    if (confidence >= 0.6) return { level: 'Medium', color: '#ffc107', icon: '⚡' };
    return { level: 'Low', color: '#dc3545', icon: '⚠️' };
  };

  const getExpectedValueColor = (ev: number) => {
    if (ev > 0.1) return '#28a745';
    if (ev > 0.05) return '#ffc107';
    return '#6c757d';
  };

  return (
    <div className="game-detail-overlay" onClick={onClose}>
      <div className="game-detail-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="game-detail-header">
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>

          <div className="game-matchup">
            <div className="teams-detailed">
              <div className="team-detailed">
                <span className="team-seed">#{game.away_team.seed}</span>
                <div className="team-info">
                  <h2>{game.away_team.city}</h2>
                  <h3>{game.away_team.name}</h3>
                  <span className="team-abbr">{game.away_team.abbreviation}</span>
                </div>
              </div>

              <div className="vs-detailed">@</div>

              <div className="team-detailed">
                <span className="team-seed">#{game.home_team.seed}</span>
                <div className="team-info">
                  <h2>{game.home_team.city}</h2>
                  <h3>{game.home_team.name}</h3>
                  <span className="team-abbr">{game.home_team.abbreviation}</span>
                </div>
              </div>
            </div>

            <div className="game-meta">
              <div className="meta-item">
                <Clock size={18} />
                <div>
                  <div className="meta-label">Game Time</div>
                  <div className="meta-value">{formatDate(game.scheduled_time)}</div>
                  <div className="meta-subvalue">{formatTime(game.scheduled_time)}</div>
                </div>
              </div>

              <div className="meta-item">
                <MapPin size={18} />
                <div>
                  <div className="meta-label">Venue</div>
                  <div className="meta-value">{game.arena}</div>
                </div>
              </div>

              {game.series && (
                <div className="meta-item">
                  <TrendingUp size={18} />
                  <div>
                    <div className="meta-label">Series</div>
                    <div className="meta-value">{game.series}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Betting Analysis */}
        <div className="game-detail-content">
          <div className="betting-summary">
            <h3>
              <DollarSign size={24} />
              Complete Betting Analysis
            </h3>
            <p className="summary-text">
              Our AI has analyzed {game.odds.length} odds from multiple sportsbooks and identified{' '}
              {game.best_bets.length} high-value betting opportunities with detailed reasoning.
            </p>
          </div>

          {/* Best Bets List */}
          <div className="best-bets-detailed">
            {game.best_bets.length > 0 ? (
              game.best_bets.map((bet, index) => {
                const confidenceInfo = getConfidenceLevel(bet.confidence);
                return (
                  <div key={index} className="bet-card-detailed">
                    <div className="bet-header-detailed">
                      <div className="bet-type-section">
                        {getBetTypeIcon(bet.bet_type)}
                        <div>
                          <h4>{getBetTypeName(bet.bet_type)}</h4>
                          <div className="bet-selection-detailed">
                            {bet.selection}
                            {bet.line && ` ${bet.line > 0 ? '+' : ''}${bet.line}`}
                          </div>
                        </div>
                      </div>

                      <div className="bet-odds-section">
                        <div className="odds-value">{formatOdds(bet.best_odds)}</div>
                        <div className="sportsbook">{bet.sportsbook}</div>
                      </div>
                    </div>

                    <div className="bet-analysis">
                      <div className="analysis-metrics">
                        <div className="metric">
                          <div className="metric-label">Confidence</div>
                          <div
                            className="metric-value confidence"
                            style={{ color: confidenceInfo.color }}
                          >
                            {confidenceInfo.icon} {(bet.confidence * 100).toFixed(0)}%
                            <span className="confidence-level">({confidenceInfo.level})</span>
                          </div>
                        </div>

                        <div className="metric">
                          <div className="metric-label">Expected Value</div>
                          <div
                            className="metric-value"
                            style={{ color: getExpectedValueColor(bet.expected_value) }}
                          >
                            +{(bet.expected_value * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>

                      <div className="reasoning-section">
                        <div className="reasoning-label">
                          <Info size={16} />
                          Analysis & Reasoning
                        </div>
                        <p className="reasoning-text">{bet.reasoning}</p>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="no-bets-detailed">
                <AlertTriangle size={48} />
                <h4>No Betting Recommendations</h4>
                <p>Our analysis didn't find any high-value betting opportunities for this game.</p>
              </div>
            )}
          </div>

          {/* Disclaimer */}
          <div className="detailed-disclaimer">
            <AlertTriangle size={20} />
            <div>
              <h4>Important Disclaimer</h4>
              <p>
                This analysis is for entertainment and educational purposes only.
                Sports betting involves risk and you should never bet more than you can afford to lose.
                Please gamble responsibly and be aware of the risks involved.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameDetail;