import React, { createContext, useContext, ReactNode, useState } from 'react';
import { GameState, Card, Play } from '../types/game';

interface GameContextType {
  gameState: GameState | null;
  setGameState: (state: GameState | null) => void;
  field: Card[];
  setField: (cards: Card[]) => void;
  playCard: (card: Card) => void;
  executeDrive: () => Promise<void>;
  drawCards: (numCards: number) => Promise<void>;
  mulligan: () => Promise<void>;
  hand: Card[];
  deckCards: Card[];
  discardPile: Card[];
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
  const [hand, setHand] = useState<Card[]>([]);
  const [deckCards, setDeckCards] = useState<Card[]>([]);
  const [discardPile, setDiscardPile] = useState<Card[]>([]);

  const drawCards = async (numCards: number) => {
    if (!gameState) return;
    
    try {
      const response = await fetch(`/api/game/${gameState.session_id}/draw-cards`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ num_cards: numCards }),
      });
      
      const result = await response.json();
      setHand(result.hand);
      setDeckCards(prev => prev.slice(numCards));
    } catch (error) {
      console.error('Failed to draw cards:', error);
    }
  };

  const mulligan = async () => {
    if (!gameState) return;
    
    try {
      const response = await fetch(`/api/game/${gameState.session_id}/mulligan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      setHand(result.hand);
      setDeckCards(prev => prev.slice(5));
      setDiscardPile(prev => [...prev, ...hand]);
    } catch (error) {
      console.error('Failed to mulligan:', error);
    }
  };

  const playCard = (card: Card) => {
    const newField = [...field, card];
    setField(newField);
    
    // Remove card from hand
    setHand(prev => prev.filter(c => c.id !== card.id || c.type !== card.type));

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
          coaching_points: gameState.coaching_points + result.drive_result.drive_score,
          game: result.next_game,
          drive: result.next_drive,
          downs: result.downs,
          distance: result.distance,
          yards_to_go: result.yards_to_go,
          pressure_level: result.drive_result.pressure_level,
          game_progress: result.game_progress,
          season_progress: result.season_progress,
        });
        
        // Clear field and move cards to discard pile
        setField([]);
        setDiscardPile(prev => [...prev, ...cardsToExecute]);
        
        // Show success message with drive details
        const driveResult = result.drive_result;
        alert(`Drive completed! +${driveResult.drive_score} points\nYards: ${driveResult.yards_gained}\nPoints: ${driveResult.points_scored}\nMultiplier: ${driveResult.multiplier?.toFixed(1)}x`);
        
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
        if (result.drive_result.turnover) {
          alert('TURNOVER! Drive failed due to defensive pressure.');
        } else {
          alert('Drive failed! You need to gain at least 10 yards or score points.');
        }
        setField([]);
        setDiscardPile(prev => [...prev, ...cardsToExecute]);
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
    drawCards,
    mulligan,
    hand,
    deckCards,
    discardPile,
  };

  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  );
};
