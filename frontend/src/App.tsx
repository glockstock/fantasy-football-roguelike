import React, { useState, useEffect } from 'react';
import { GameProvider } from './context/GameContext';
import GameBoard from './components/GameBoard';
import Hand from './components/Hand';
import Scoreboard from './components/Scoreboard';
import CardShop from './components/CardShop';
import DraftReward from './components/DraftReward';
import SplashPage from './components/SplashPage';
import DeckSelection from './components/DeckSelection';
import { Card, GameState, AppState, DeckType } from './types/game';

function App() {
  const [appState, setAppState] = useState<AppState>({
    currentScreen: 'splash',
    selectedDeckType: undefined,
    playerName: undefined
  });
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showShop, setShowShop] = useState(false);
  const [showDraftReward, setShowDraftReward] = useState(false);

  const handleStartNewRun = (playerName: string) => {
    setAppState(prev => ({ ...prev, currentScreen: 'deck_selection', playerName }));
  };

  const handleDeckSelected = async (deckType: DeckType) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/game/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          player_name: appState.playerName,
          deck_type: deckType.id
        }),
      });
      
      const gameData = await response.json();
      setGameState(gameData);
      setAppState(prev => ({ 
        ...prev, 
        currentScreen: 'game',
        selectedDeckType: deckType.id
      }));
    } catch (error) {
      console.error('Failed to initialize game:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToSplash = () => {
    setAppState({
      currentScreen: 'splash',
      selectedDeckType: undefined,
      playerName: undefined
    });
    setGameState(null);
  };

  const handlePlayerNameChange = (name: string) => {
    setAppState(prev => ({ ...prev, playerName: name }));
  };

  const handleUpdateCoachingPoints = (points: number) => {
    if (gameState) {
      setGameState({
        ...gameState,
        coaching_points: points
      });
    }
  };

  const handleDraftCardSelected = (card: Card) => {
    // Card is already added to deck by the DraftReward component
    // Just close the modal
    setShowDraftReward(false);
  };

  // Check for game wins to show draft reward
  useEffect(() => {
    if (gameState && gameState.game_progress.games_won > 0) {
      // Show draft reward after game win
      setShowDraftReward(true);
    }
  }, [gameState?.game_progress.games_won]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-football-green to-field-green">
        <div className="text-white text-2xl">Starting your coaching career...</div>
      </div>
    );
  }

  // Render splash page
  if (appState.currentScreen === 'splash') {
    return (
      <SplashPage 
        onStartNewRun={handleStartNewRun}
        careerProgress={gameState?.career_progress}
      />
    );
  }

  // Render deck selection
  if (appState.currentScreen === 'deck_selection') {
    return (
      <DeckSelection
        onDeckSelected={handleDeckSelected}
        onBack={handleBackToSplash}
        playerName={appState.playerName || 'Coach'}
        careerLevel={gameState?.career_level?.level || 'high_school'}
      />
    );
  }

  // Render main game
  if (!gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-football-green to-field-green">
        <div className="text-white text-2xl">Failed to load game</div>
      </div>
    );
  }

  return (
    <GameProvider gameState={gameState} setGameState={setGameState}>
      <div className="min-h-screen bg-gradient-to-br from-football-green to-field-green">
        <div className="container mx-auto px-4 py-8">
          <header className="text-center mb-8">
            <button
              onClick={handleBackToSplash}
              className="absolute left-4 top-4 bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              ← Main Menu
            </button>
            
            <button
              onClick={() => setShowShop(true)}
              className="absolute right-4 top-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              🛒 Shop ({gameState.coaching_points} CP)
            </button>
            
            <h1 className="text-4xl font-bold text-white mb-2">
              Fantasy Football Roguelike
            </h1>
            <p className="text-gray-300">
              Coach {appState.playerName} - {gameState.career_level.name} | Season {gameState.season_progress.current_season} | Game {gameState.game_progress.current_game} | Drive {gameState.game_progress.current_drive}
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
            </div>
          </div>

          {/* Bottom - Hand */}
          <div className="mt-8">
            <Hand />
          </div>

          {/* Shop Modal */}
          {showShop && gameState && (
            <CardShop
              sessionId={gameState.session_id}
              onClose={() => setShowShop(false)}
              onUpdateCoachingPoints={handleUpdateCoachingPoints}
            />
          )}

          {/* Draft Reward Modal */}
          {showDraftReward && gameState && (
            <DraftReward
              sessionId={gameState.session_id}
              onClose={() => setShowDraftReward(false)}
              onCardSelected={handleDraftCardSelected}
            />
          )}
        </div>
      </div>
    </GameProvider>
  );
}

export default App;
