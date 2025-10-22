import React, { useState, useEffect } from 'react';
import { useGame } from '../context/GameContext';
import { Card, Player, Play, Modifier } from '../types/game';
import CardComponent from './CardComponent';

const GameBoard: React.FC = () => {
  const { gameState, setGameState } = useGame();
  const [field, setField] = useState<Card[]>([]);
  const [isPlayingRun, setIsPlayingRun] = useState(false);

  const handleCardPlay = async (card: Card) => {
    if (!gameState) return;

    const newField = [...field, card];
    setField(newField);

    // Check if this completes a drive (simplified logic)
    if (card.type === 'play' && (card.data as Play).name.toLowerCase().includes('touchdown')) {
      await executeDrive(newField);
    }
  };

  const executeDrive = async (cards: Card[]) => {
    if (!gameState) return;

    try {
      const response = await fetch(`/api/game/${gameState.session_id}/play-run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cards }),
      });

      const result = await response.json();
      
      if (result.valid_run) {
        // Update game state with new score
        setGameState({
          ...gameState,
          score: gameState.score + result.run_score,
          run: gameState.run + 1, // This represents drives/games in the season
        });
        
        // Clear field
        setField([]);
        
        // Show success message
        alert(`Drive completed! +${result.run_score} points`);
      } else {
        alert('Invalid drive! Must end with a scoring play.');
        setField([]);
      }
    } catch (error) {
      console.error('Failed to execute drive:', error);
    }
  };

  const clearField = () => {
    setField([]);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Game Field</h2>
        <div className="flex gap-2">
          <button
            onClick={clearField}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Clear Field
          </button>
          <button
            onClick={() => executeDrive(field)}
            disabled={field.length === 0}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Execute Drive
          </button>
        </div>
      </div>

      {/* Field Visualization */}
      <div className="field h-32 rounded-lg mb-6 relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-white font-bold text-lg">
            {field.length === 0 ? 'Drop cards here to build your run' : `${field.length} cards played`}
          </div>
        </div>
      </div>

      {/* Field Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 min-h-32">
        {field.map((card, index) => (
          <div key={`${card.id}-${index}`} className="relative">
            <CardComponent card={card} />
            <div className="absolute -top-2 -right-2 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
              {index + 1}
            </div>
          </div>
        ))}
      </div>

      {/* Run Instructions */}
      <div className="mt-6 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-bold text-gray-800 mb-2">How to Play:</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Drag cards from your hand to the field to build a run</li>
          <li>• Runs must end with a scoring play (touchdown, field goal, etc.)</li>
          <li>• Each run scores points based on the cards played</li>
          <li>• Complete runs to advance through seasons</li>
        </ul>
      </div>
    </div>
  );
};

export default GameBoard;
