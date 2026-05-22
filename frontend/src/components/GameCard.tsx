import React from 'react';
import { GameWithBestBets, GameStatus, BetType } from '../types';
import { Clock, MapPin, TrendingUp, DollarSign } from 'lucide-react';
import './GameCard.css';

interface GameCardProps {
  game: GameWithBestBets;
  onGameClick: (gameId: string) => void;
}

const GameCard: React.FC<GameCardProps> = ({ game, onGameClick }) => {
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatOdds = (odds: number) => {
    return odds > 0 ? `+${odds}` : `${odds}`;
  };

  const getStatusBadge = (status: GameStatus) => {
    const badgeClass = {
      [GameStatus.SCHEDULED]: 'status-scheduled',
      [GameStatus.LIVE]: 'status-live',
      [GameStatus.FINISHED]: 'status-finished',
      [GameStatus.POSTPONED]: 'status-postponed'
    };

    return <span className={`status-badge ${badgeClass[status]}`}>{status.toUpperCase()}</span>;
  };

  const getBetTypeIcon = (betType: BetType) => {
    switch (betType) {
      case BetType.MONEYLINE:
        return '💰';
      case BetType.SPREAD:
        return '📊';
      case BetType.TOTAL:
        return '⚖️';
      case BetType.PLAYER_POINTS:
        return '🏀';
      case BetType.PLAYER_REBOUNDS:
        return '🔄';
      case BetType.PLAYER_ASSISTS:
        return '🤝';
      case BetType.PLAYER_THREES:
        return '🎯';
      case BetType.PLAYER_DOUBLE_DOUBLE:
        return '✌️';
      case BetType.PLAYER_TRIPLE_DOUBLE:
        return '🎩';
      case BetType.TEAM_POINTS:
        return '🏆';
      case BetType.TEAM_REBOUNDS:
        return '📈';
      case BetType.TEAM_ASSISTS:
        return '🔗';
      default:
        return '🎯';
    }
  };

  // Separate main bets from prop bets
  const mainBetTypes = [BetType.MONEYLINE, BetType.SPREAD, BetType.TOTAL];
  const propBetTypes = [
    BetType.PLAYER_POINTS, BetType.PLAYER_REBOUNDS, BetType.PLAYER_ASSISTS,
    BetType.PLAYER_THREES, BetType.PLAYER_DOUBLE_DOUBLE, BetType.PLAYER_TRIPLE_DOUBLE,
    BetType.TEAM_POINTS, BetType.TEAM_REBOUNDS, BetType.TEAM_ASSISTS
  ];

  const mainBets = game.best_bets.filter(bet => mainBetTypes.includes(bet.bet_type)).slice(0, 3);
  const propBets = game.best_bets.filter(bet => propBetTypes.includes(bet.bet_type)).slice(0, 3);

  return (
    <div className="game-card clickable" onClick={() => onGameClick(game.id)} title="Click to view detailed analysis">
      <div className="game-header">
        <div className="teams">
          <div className="team">
            <span className="team-seed">#{game.away_team.seed}</span>
            <span className="team-name">{game.away_team.city} {game.away_team.name}</span>
            <span className="team-abbr">({game.away_team.abbreviation})</span>
          </div>
          <div className="vs">@</div>
          <div className="team">
            <span className="team-seed">#{game.home_team.seed}</span>
            <span className="team-name">{game.home_team.city} {game.home_team.name}</span>
            <span className="team-abbr">({game.home_team.abbreviation})</span>
          </div>
        </div>
        {getStatusBadge(game.status)}
      </div>

      <div className="game-info">
        <div className="info-item">
          <Clock size={16} />
          <span>{formatTime(game.scheduled_time)}</span>
        </div>
        <div className="info-item">
          <MapPin size={16} />
          <span>{game.arena}</span>
        </div>
      </div>

      {game.series && (
        <div className="series-info">
          <TrendingUp size={16} />
          <span>{game.series}</span>
        </div>
      )}

      {/* Main Bets Section */}
      <div className="best-bets">
        <h4 className="best-bets-title">
          <DollarSign size={16} />
          Top Picks
        </h4>
        {mainBets.length > 0 ? (
          <div className="bets-list">
            {mainBets.map((bet, index) => (
              <div key={index} className="bet-item">
                <div className="bet-main">
                  <span className="bet-icon">{getBetTypeIcon(bet.bet_type)}</span>
                  <span className="bet-selection">
                    {bet.selection}
                    {bet.line && ` ${bet.line > 0 ? '+' : ''}${bet.line}`}
                  </span>
                  <span className="bet-odds">{formatOdds(bet.best_odds)}</span>
                </div>
                <div className="bet-details">
                  <span className="confidence">
                    Confidence: {(bet.confidence * 100).toFixed(0)}%
                  </span>
                  <span className="sportsbook">{bet.sportsbook}</span>
                </div>
                <div className="bet-reasoning">{bet.reasoning}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-bets">No main recommendations available</div>
        )}
      </div>

      {/* Prop Bets Section */}
      {propBets.length > 0 && (
        <div className="prop-bets">
          <h4 className="prop-bets-title">
            🎯 Player Props
          </h4>
          <div className="bets-list">
            {propBets.map((bet, index) => (
              <div key={index} className="bet-item prop-bet-item">
                <div className="bet-main">
                  <span className="bet-icon">{getBetTypeIcon(bet.bet_type)}</span>
                  <span className="bet-selection">
                    {bet.player_name && <span className="player-name">{bet.player_name}</span>}
                    <span className="prop-detail">
                      {bet.selection}
                      {bet.line && ` ${bet.line > 0 ? '+' : ''}${bet.line}`}
                    </span>
                  </span>
                  <span className="bet-odds">{formatOdds(bet.best_odds)}</span>
                </div>
                <div className="bet-details">
                  <span className="confidence">
                    Confidence: {(bet.confidence * 100).toFixed(0)}%
                  </span>
                  <span className="sportsbook">{bet.sportsbook}</span>
                </div>
                <div className="bet-reasoning">{bet.reasoning}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card-footer">
        <span className="bet-count">{game.best_bets.length} total recommendations</span>
        <span className="click-hint">Click for details →</span>
      </div>
    </div>
  );
};

export default GameCard;