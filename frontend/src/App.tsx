import React, { useState, useEffect } from 'react';
import './App.css';
import GamesList from './components/GamesList';
import GameDetail from './components/GameDetail';
import { TrendingUp } from 'lucide-react';
import { GameWithBestBets } from './types';
import { gameService } from './services/api';

function App() {
  const [selectedGame, setSelectedGame] = useState<GameWithBestBets | null>(null);
  const [games, setGames] = useState<GameWithBestBets[]>([]);

  // Fetch games data for the detail modal
  useEffect(() => {
    const fetchGames = async () => {
      try {
        const gamesData = await gameService.getAllGamesWithBets();
        setGames(gamesData);
      } catch (error) {
        console.error('Error fetching games for detail view:', error);
      }
    };

    fetchGames();
  }, []);

  const handleGameSelect = (gameId: string) => {
    const game = games.find(g => g.id === gameId);
    if (game) {
      setSelectedGame(game);
    }
  };

  const handleCloseDetail = () => {
    setSelectedGame(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <div className="logo-section">
            <TrendingUp size={32} color="#007bff" />
            <h1>NBA Betting Compiler</h1>
          </div>
          <div className="header-subtitle">
            Smart NBA Playoff Betting Analysis & Recommendations
          </div>
        </div>
      </header>
      <main className="App-main">
        <GamesList onGameSelect={handleGameSelect} />
      </main>

      {/* Game Detail Modal */}
      {selectedGame && (
        <GameDetail
          game={selectedGame}
          onClose={handleCloseDetail}
        />
      )}
    </div>
  );
}

export default App;
