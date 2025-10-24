import React, { useState, useEffect } from 'react';
import { useGame } from '../context/GameContext';
import { Card, Player, Play, Modifier } from '../types/game';
import CardComponent from './CardComponent';

const Hand: React.FC = () => {
  const { gameState, playCard, hand, drawCards, mulligan } = useGame();
  const [allCards, setAllCards] = useState<{
    players: Player[];
    plays: Play[];
    modifiers: Modifier[];
  }>({ players: [], plays: [], modifiers: [] });
  const [playedCardAnimation, setPlayedCardAnimation] = useState<string | null>(null);

  useEffect(() => {
    fetchAllCards();
  }, []);

  useEffect(() => {
    if (gameState && allCards.players.length > 0 && hand.length === 0) {
      // Draw initial hand of 5 cards
      drawCards(5);
    }
  }, [gameState, allCards, hand.length, drawCards]);

  const fetchAllCards = async () => {
    try {
      const [playersRes, playsRes, modifiersRes] = await Promise.all([
        fetch('/api/cards/players'),
        fetch('/api/cards/plays'),
        fetch('/api/cards/modifiers'),
      ]);

      const players = await playersRes.json();
      const plays = await playsRes.json();
      const modifiers = await modifiersRes.json();

      setAllCards({ players, plays, modifiers });
    } catch (error) {
      console.error('Failed to fetch cards:', error);
    }
  };

  const handleCardClick = (card: Card) => {
    // Show animation feedback
    setPlayedCardAnimation(card.data.name);
    setTimeout(() => setPlayedCardAnimation(null), 1000);
    
    playCard(card);
  };

  const handleDrawCards = () => {
    drawCards(3);
  };

  const handleMulligan = () => {
    mulligan();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">Your Hand ({hand.length}/8)</h2>
        <div className="flex gap-2">
          <button
            onClick={handleDrawCards}
            disabled={hand.length >= 8}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Draw 3 Cards
          </button>
          <button
            onClick={handleMulligan}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
          >
            Mulligan Hand
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 relative">
        {hand.map((card, index) => (
          <div 
            key={`${card.id}-${index}`} 
            className={`cursor-pointer transition-all duration-300 ${
              playedCardAnimation === card.data.name 
                ? 'animate-pulse scale-110' 
                : 'hover:scale-105 hover:shadow-lg'
            }`}
          >
            <CardComponent card={card} onClick={() => handleCardClick(card)} />
          </div>
        ))}
        
        {/* Played Card Animation Overlay */}
        {playedCardAnimation && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="bg-green-500 text-white px-4 py-2 rounded-lg font-bold animate-bounce">
              Played: {playedCardAnimation}
            </div>
          </div>
        )}
      </div>

      {hand.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No cards in hand. Click "Draw 3 Cards" to get started!
        </div>
      )}
    </div>
  );
};

export default Hand;
