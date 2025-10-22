import React, { useState, useEffect } from 'react';
import { GameProvider } from './context/GameContext';
import GameBoard from './components/GameBoard';
import Hand from './components/Hand';
import Scoreboard from './components/Scoreboard';
import CardShop from './components/CardShop';
import { Card, GameState } from './types/game';

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize game on load
    initializeGame();
  }, []);

  const initializeGame = async () => {
    try {
      const response = await fetch('/api/game/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: 'Player' }),
      });
      
      const gameData = await response.json();
      setGameState(gameData);
    } catch (error) {
      console.error('Failed to initialize game:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-2xl">Loading Game...</div>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-2xl">Failed to load game</div>
      </div>
    );
  }

  return (
    <GameProvider value={{ gameState, setGameState }}>
      <div className="min-h-screen bg-gradient-to-br from-football-green to-field-green">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              Fantasy Football Roguelike
            </h1>
            <p className="text-gray-300">
              Build your deck, make your runs, score touchdowns!
            </p>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Game Board */}
            <div className="lg:col-span-2">
              <GameBoard />
            </div>

            {/* Right Column - UI Elements */}
            <div className="space-y-6">
              <Scoreboard />
              <CardShop />
            </div>
          </div>

          {/* Bottom - Hand */}
          <div className="mt-8">
            <Hand />
          </div>
        </div>
      </div>
    </GameProvider>
  );
}

export default App;
