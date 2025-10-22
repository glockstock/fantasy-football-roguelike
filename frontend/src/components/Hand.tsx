import React, { useState, useEffect } from 'react';
import { useGame } from '../context/GameContext';
import { Card, Player, Play, Modifier } from '../types/game';
import CardComponent from './CardComponent';

const Hand: React.FC = () => {
  const { gameState, setGameState } = useGame();
  const [hand, setHand] = useState<Card[]>([]);
  const [allCards, setAllCards] = useState<{
    players: Player[];
    plays: Play[];
    modifiers: Modifier[];
  }>({ players: [], plays: [], modifiers: [] });

  useEffect(() => {
    fetchAllCards();
  }, []);

  useEffect(() => {
    if (gameState && allCards.players.length > 0) {
      generateHand();
    }
  }, [gameState, allCards]);

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

  const generateHand = () => {
    if (!gameState || !allCards.players.length) return;

    const handCards: Card[] = [];

    // Add players from deck
    gameState.deck.players.forEach(playerId => {
      const player = allCards.players.find(p => p.id === playerId);
      if (player) {
        handCards.push({ id: player.id, type: 'player', data: player });
      }
    });

    // Add plays from deck
    gameState.deck.plays.forEach(playId => {
      const play = allCards.plays.find(p => p.id === playId);
      if (play) {
        handCards.push({ id: play.id, type: 'play', data: play });
      }
    });

    // Add modifiers from deck
    gameState.deck.modifiers.forEach(modifierId => {
      const modifier = allCards.modifiers.find(m => m.id === modifierId);
      if (modifier) {
        handCards.push({ id: modifier.id, type: 'modifier', data: modifier });
      }
    });

    setHand(handCards);
  };

  const drawCard = () => {
    // Simple card drawing logic - can be enhanced
    const allAvailableCards = [
      ...allCards.players.map(p => ({ id: p.id, type: 'player' as const, data: p })),
      ...allCards.plays.map(p => ({ id: p.id, type: 'play' as const, data: p })),
      ...allCards.modifiers.map(m => ({ id: m.id, type: 'modifier' as const, data: m })),
    ];

    const randomCard = allAvailableCards[Math.floor(Math.random() * allAvailableCards.length)];
    setHand(prev => [...prev, randomCard]);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">Your Hand</h2>
        <button
          onClick={drawCard}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Draw Card
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {hand.map((card, index) => (
          <div key={`${card.id}-${index}`} className="cursor-pointer hover:scale-105 transition-transform">
            <CardComponent card={card} />
          </div>
        ))}
      </div>

      {hand.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No cards in hand. Click "Draw Card" to get started!
        </div>
      )}
    </div>
  );
};

export default Hand;
