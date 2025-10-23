import React, { createContext, useContext, ReactNode, useState } from 'react';
import { GameState, Card, Play } from '../types/game';

interface GameContextType {
  gameState: GameState | null;
  setGameState: (state: GameState | null) => void;
  field: Card[];
  setField: (cards: Card[]) => void;
  playCard: (card: Card) => void;
  executeDrive: () => Promise<void>;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export const useGame = () => {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
};

interface GameProviderProps {
  children: ReactNode;
  gameState: GameState | null;
  setGameState: (state: GameState | null) => void;
}

export const GameProvider: React.FC<GameProviderProps> = ({ children, gameState, setGameState }) => {
  const [field, setField] = useState<Card[]>([]);

  const playCard = (card: Card) => {
    const newField = [...field, card];
    setField(newField);

    // Check if this completes a drive (simplified logic)
    if (card.type === 'play' && (card.data as Play).name.toLowerCase().includes('touchdown')) {
      executeDrive(newField);
    }
  };

  const executeDrive = async (cards?: Card[]) => {
    if (!gameState) return;

    const cardsToExecute = cards || field;
    if (cardsToExecute.length === 0) return;

    try {
      const response = await fetch(`/api/game/${gameState.session_id}/play-drive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cards: cardsToExecute }),
      });

      const result = await response.json();
      
      if (result.drive_result.drive_successful) {
        // Update game state with new progress
        setGameState({
          ...gameState,
          score: gameState.score + result.drive_result.drive_score,
          game: result.next_game,
          drive: result.next_drive,
          game_progress: result.game_progress,
          season_progress: result.season_progress,
        });
        
        // Clear field
        setField([]);
        
        // Show success message with drive details
        const driveResult = result.drive_result;
        alert(`Drive completed! +${driveResult.drive_score} points\nYards: ${driveResult.yards_gained}\nPoints: ${driveResult.points_scored}`);
        
        // Check for game/season completion
        if (result.game_progress.current_game > gameState.game_progress.current_game) {
          alert(`Game ${gameState.game_progress.current_game} won! Moving to Game ${result.game_progress.current_game}`);
        }
        if (result.season_progress.current_season > gameState.season_progress.current_season) {
          alert(`Season ${gameState.season_progress.current_season} won! Moving to Season ${result.season_progress.current_season}`);
        }
        if (result.season_progress.seasons_won > gameState.season_progress.seasons_won) {
          alert(`🏆 CHAMPIONSHIP WON! You've completed all ${result.season_progress.total_seasons} seasons!`);
        }
      } else {
        alert('Drive failed! You need to gain at least 10 yards or score points.');
        setField([]);
      }
    } catch (error) {
      console.error('Failed to execute drive:', error);
    }
  };

  const value: GameContextType = {
    gameState,
    setGameState,
    field,
    setField,
    playCard,
    executeDrive,
  };

  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  );
};
