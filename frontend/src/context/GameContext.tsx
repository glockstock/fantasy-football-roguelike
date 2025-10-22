import React, { createContext, useContext, ReactNode } from 'react';
import { GameState } from '../types/game';

interface GameContextType {
  gameState: GameState | null;
  setGameState: (state: GameState | null) => void;
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
  value: GameContextType;
}

export const GameProvider: React.FC<GameProviderProps> = ({ children, value }) => {
  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  );
};
