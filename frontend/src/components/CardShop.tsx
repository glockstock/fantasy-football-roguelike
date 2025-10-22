import React, { useState, useEffect } from 'react';
import { useGame } from '../context/GameContext';
import { Player, Play, Modifier } from '../types/game';
import CardComponent from './CardComponent';

const CardShop: React.FC = () => {
  const { gameState, setGameState } = useGame();
  const [availableCards, setAvailableCards] = useState<{
    players: Player[];
    plays: Play[];
    modifiers: Modifier[];
  }>({ players: [], plays: [], modifiers: [] });
  const [selectedCategory, setSelectedCategory] = useState<'players' | 'plays' | 'modifiers'>('players');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchAvailableCards();
  }, []);

  const fetchAvailableCards = async () => {
    try {
      const [playersRes, playsRes, modifiersRes] = await Promise.all([
        fetch('/api/cards/players'),
        fetch('/api/cards/plays'),
        fetch('/api/cards/modifiers'),
      ]);

      const players = await playersRes.json();
      const plays = await playsRes.json();
      const modifiers = await modifiersRes.json();

      setAvailableCards({ players, plays, modifiers });
    } catch (error) {
      console.error('Failed to fetch available cards:', error);
    }
  };

  const buyCard = async (cardId: number, cardType: 'players' | 'plays' | 'modifiers') => {
    if (!gameState) return;

    let card: Player | Play | Modifier | undefined;
    if (cardType === 'players') {
      card = availableCards.players.find((c: Player) => c.id === cardId);
    } else if (cardType === 'plays') {
      card = availableCards.plays.find((c: Play) => c.id === cardId);
    } else {
      card = availableCards.modifiers.find((c: Modifier) => c.id === cardId);
    }
    
    if (!card) return;

    // Simple buying logic - in a real game, you'd have currency/points system
    const newDeck = {
      ...gameState.deck,
      [cardType]: [...gameState.deck[cardType], cardId]
    };

    setGameState({
      ...gameState,
      deck: newDeck
    });

    alert(`Added ${card.name} to your deck!`);
  };

  const getCurrentCards = () => {
    switch (selectedCategory) {
      case 'players': return availableCards.players;
      case 'plays': return availableCards.plays;
      case 'modifiers': return availableCards.modifiers;
      default: return [];
    }
  };

  if (!isOpen) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <button
          onClick={() => setIsOpen(true)}
          className="w-full px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
        >
          Open Card Shop
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">Card Shop</h2>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      {/* Category Tabs */}
      <div className="flex space-x-2 mb-4">
        {(['players', 'plays', 'modifiers'] as const).map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded capitalize transition-colors ${
              selectedCategory === category
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 gap-4 max-h-96 overflow-y-auto">
        {getCurrentCards().map(card => (
          <div key={card.id} className="flex items-center space-x-4 p-3 border rounded-lg">
            <div className="flex-1">
              <CardComponent 
                card={{ 
                  id: card.id, 
                  type: selectedCategory.slice(0, -1) as 'player' | 'play' | 'modifier', 
                  data: card 
                }}
              />
            </div>
            <button
              onClick={() => buyCard(card.id, selectedCategory)}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
            >
              Buy (${card.cost})
            </button>
          </div>
        ))}
      </div>

      {getCurrentCards().length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No {selectedCategory} available
        </div>
      )}
    </div>
  );
};

export default CardShop;
