import React, { useState, useEffect } from 'react';
import { GameWithBestBets } from '../types';
import { gameService } from '../services/api';
import GameCard from './GameCard';
import LoadingSpinner from './LoadingSpinner';
import { RefreshCw, AlertCircle, Trophy } from 'lucide-react';
import './GamesList.css';

interface GamesListProps {
  onGameSelect: (gameId: string) => void;
}

const GamesList: React.FC<GamesListProps> = ({ onGameSelect }) => {
  const [games, setGames] = useState<GameWithBestBets[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchGames = async () => {
    try {
      setLoading(true);
      setError(null);
      const gamesData = await gameService.getAllGamesWithBets();
      setGames(gamesData);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch games data. Please try again.');
      console.error('Error fetching games:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGames();

    // Set up auto-refresh every 5 minutes
    const interval = setInterval(fetchGames, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchGames();
  };

  if (loading && games.length === 0) {
    return (
      <div className="games-list-container">
        <LoadingSpinner message="Loading today's NBA playoff games..." />
      </div>
    );
  }

  if (error && games.length === 0) {
    return (
      <div className="games-list-container">
        <div className="error-state">
          <AlertCircle size={48} color="#dc3545" />
          <h3>Unable to Load Games</h3>
          <p>{error}</p>
          <button onClick={handleRefresh} className="retry-button">
            <RefreshCw size={16} />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="games-list-container">
      <div className="games-header">
        <div className="header-content">
          <div className="title-section">
            <Trophy size={24} />
            <h2>NBA Playoff Games - {new Date().toLocaleDateString()}</h2>
          </div>
          <button
            onClick={handleRefresh}
            className={`refresh-button ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
        {lastUpdated && (
          <div className="last-updated">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </div>
        )}
        {error && (
          <div className="error-banner">
            <AlertCircle size={16} />
            {error}
          </div>
        )}
      </div>

      <div className="games-grid">
        {games.length > 0 ? (
          games.map((game) => (
            <GameCard
              key={game.id}
              game={game}
              onGameClick={onGameSelect}
            />
          ))
        ) : (
          <div className="no-games">
            <Trophy size={48} color="#8e8e93" />
            <h3>No Games Today</h3>
            <p>No NBA playoff games scheduled for today.</p>
          </div>
        )}
      </div>

      {games.length > 0 && (
        <div className="games-footer">
          <p className="disclaimer">
            <strong>Disclaimer:</strong> This information is for entertainment purposes only.
            Please gamble responsibly and be aware of the risks involved in sports betting.
          </p>
        </div>
      )}
    </div>
  );
};

export default GamesList;