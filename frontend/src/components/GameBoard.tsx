import React, { useState, useEffect } from 'react';
import { useGame } from '../context/GameContext';
import CardComponent from './CardComponent';

const GameBoard: React.FC = () => {
  const { gameState, field, setField, executeDrive } = useGame();
  const [comboAnimation, setComboAnimation] = useState<string | null>(null);
  const [pressureAnimation, setPressureAnimation] = useState(false);

  const getDownSuffix = (down: number) => {
    if (down === 1) return 'st';
    if (down === 2) return 'nd';
    if (down === 3) return 'rd';
    return 'th';
  };

  const clearField = () => {
    setField([]);
  };

  // Calculate current multiplier from field cards and detect combos
  const calculateMultiplier = () => {
    let multiplier = 1.0;
    let comboCount = 0;
    let comboType = '';
    
    field.forEach((card, index) => {
      if (card.type === 'player') {
        multiplier += 0.1; // Base player bonus
      } else if (card.type === 'modifier') {
        const modifierData = card.data as any;
        const effect = modifierData.effect || {};
        if (effect.multiplier_boost) {
          multiplier += effect.multiplier_boost;
        }
        if (effect.scoring_multiplier) {
          multiplier *= effect.scoring_multiplier;
        }
      }
      // Add synergy bonuses and detect combos
      if (card.synergy_tags) {
        field.slice(0, index).forEach(otherCard => {
          if (otherCard.synergy_tags) {
            const matchingTags = card.synergy_tags!.filter(tag => otherCard.synergy_tags!.includes(tag));
            if (matchingTags.length > 0) {
              comboCount += matchingTags.length;
              comboType = matchingTags[0]; // Use first matching tag as combo type
              multiplier += matchingTags.length * 0.1;
            }
          }
        });
      }
    });
    
    // Trigger combo animation if we have 3+ matching synergies
    if (comboCount >= 3 && comboType) {
      setComboAnimation(`${comboType} COMBO!`);
      setTimeout(() => setComboAnimation(null), 2000);
    }
    
    return multiplier;
  };

  const currentMultiplier = calculateMultiplier();

  // Trigger pressure animation when pressure level changes
  useEffect(() => {
    if (gameState?.pressure_level && gameState.pressure_level > 50) {
      setPressureAnimation(true);
      setTimeout(() => setPressureAnimation(false), 1000);
    }
  }, [gameState?.pressure_level]);

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
            onClick={() => executeDrive()}
            disabled={field.length === 0}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Execute Drive
          </button>
        </div>
      </div>

      {/* Drive Status */}
      <div className={`mb-6 p-4 rounded-lg transition-all duration-500 ${
        pressureAnimation ? 'bg-red-100 border-2 border-red-300' : 'bg-gray-100'
      }`}>
        <div className="flex justify-between items-center mb-2">
          <div className="text-lg font-bold">
            {gameState?.downs || 1}{getDownSuffix(gameState?.downs || 1)} & {gameState?.yards_to_go || 10}
          </div>
          <div className={`text-lg font-bold transition-colors duration-300 ${
            currentMultiplier >= 2.0 ? 'text-purple-600' : 
            currentMultiplier >= 1.5 ? 'text-blue-600' : 'text-gray-600'
          }`}>
            Multiplier: {currentMultiplier.toFixed(1)}x
          </div>
        </div>
        
        {/* Pressure Meter */}
        <div className="mb-2">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Defensive Pressure</span>
            <span>{gameState?.pressure_level || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-500 ${
                (gameState?.pressure_level || 0) > 75 ? 'bg-red-500' :
                (gameState?.pressure_level || 0) > 50 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(gameState?.pressure_level || 0, 100)}%` }}
            ></div>
          </div>
        </div>
        
        <div className="text-sm text-gray-600">
          Distance: {gameState?.distance || 0} yards
        </div>
      </div>

      {/* Field Visualization */}
      <div className="field h-32 rounded-lg mb-6 relative overflow-hidden bg-gradient-to-r from-green-400 to-green-600 border-2 border-green-300">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-white font-bold text-lg drop-shadow-lg">
            {field.length === 0 ? 'Drop cards here to build your drive' : `${field.length} cards played`}
          </div>
        </div>
        
        {/* Combo Animation Overlay */}
        {comboAnimation && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-purple-600 text-white px-6 py-3 rounded-lg font-bold text-xl animate-pulse shadow-lg">
              {comboAnimation}
            </div>
          </div>
        )}
      </div>

      {/* Field Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 min-h-32">
        {field.map((card, index) => (
          <div key={`${card.id}-${index}`} className="relative transform transition-all duration-300 hover:scale-105">
            <CardComponent card={card} />
            <div className="absolute -top-2 -right-2 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shadow-lg">
              {index + 1}
            </div>
            {/* Synergy indicator */}
            {card.synergy_tags && card.synergy_tags.length > 0 && (
              <div className="absolute -bottom-1 -left-1 bg-purple-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-xs font-bold">
                ⭐
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Drive Instructions */}
      <div className="mt-6 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-bold text-gray-800 mb-2">How to Play:</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Click cards from your hand to play them on the field</li>
          <li>• Each card played = 1 down (max 4 downs per drive)</li>
          <li>• Cards with matching synergy tags give bonus multipliers</li>
          <li>• High-risk plays can fail due to defensive pressure</li>
          <li>• Gain 10+ yards for a first down, or score points</li>
          <li>• Turnover on downs if you don't gain 10 yards in 4 downs</li>
          <li>• Complete 4 successful drives to win each game</li>
          <li>• Win 10 games to win each season</li>
          <li>• Complete all 10 seasons to win the championship!</li>
        </ul>
      </div>
    </div>
  );
};

export default GameBoard;
