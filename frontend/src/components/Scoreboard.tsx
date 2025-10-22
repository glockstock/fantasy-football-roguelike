import React from 'react';
import { useGame } from '../context/GameContext';

const Scoreboard: React.FC = () => {
  const { gameState } = useGame();

  if (!gameState) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-500">Loading scoreboard...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Scoreboard</h2>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Score:</span>
          <span className="text-2xl font-bold text-green-600">{gameState.score}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Season:</span>
          <span className="text-lg font-semibold">{gameState.season}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Run:</span>
          <span className="text-lg font-semibold">{gameState.run}</span>
        </div>
        
        <div className="pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-500">
            <div className="flex justify-between mb-1">
              <span>Deck Size:</span>
              <span>
                {gameState.deck.players.length + gameState.deck.plays.length + gameState.deck.modifiers.length} cards
              </span>
            </div>
            <div className="flex justify-between">
              <span>Players:</span>
              <span>{gameState.deck.players.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Plays:</span>
              <span>{gameState.deck.plays.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Modifiers:</span>
              <span>{gameState.deck.modifiers.length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Scoreboard;
