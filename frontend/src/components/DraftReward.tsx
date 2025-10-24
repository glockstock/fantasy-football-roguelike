import React, { useState, useEffect } from 'react';
import { Card } from '../types/game';
import CardComponent from './CardComponent';

interface DraftRewardProps {
  sessionId: number;
  onClose: () => void;
  onCardSelected: (card: Card) => void;
}

const DraftReward: React.FC<DraftRewardProps> = ({ sessionId, onClose, onCardSelected }) => {
  const [draftCards, setDraftCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);

  useEffect(() => {
    fetchDraftReward();
  }, [sessionId]);

  const fetchDraftReward = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/game/${sessionId}/draft-reward`);
      const data = await response.json();
      
      if (response.ok) {
        setDraftCards(data.draft_cards);
      } else {
        setError(data.error || 'Failed to load draft reward');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const selectCard = async (card: Card) => {
    try {
      const response = await fetch(`/api/game/${sessionId}/select-draft-card`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ card }),
      });

      const data = await response.json();

      if (response.ok) {
        setSelectedCard(card);
        onCardSelected(card);
        alert(`Selected ${card.data.name}! Added to your deck.`);
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        alert(data.error || 'Failed to select card');
      }
    } catch (err) {
      alert('Network error');
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'bg-gray-100 text-gray-800';
      case 'rare': return 'bg-blue-100 text-blue-800';
      case 'epic': return 'bg-purple-100 text-purple-800';
      case 'legendary': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg">
          <div className="text-center">Loading draft picks...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">🎉 Draft Pick! 🎉</h2>
          <p className="text-lg text-gray-600">
            Congratulations on winning the game! Choose 1 of 3 cards to add to your deck.
          </p>
        </div>

        <div className="mb-4 p-4 bg-blue-100 rounded-lg">
          <h3 className="font-bold text-blue-800 mb-2">Draft Rules:</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Cards are weighted by rarity - better performance = better chances</li>
            <li>• Choose the card that best fits your strategy</li>
            <li>• Each card will be permanently added to your deck</li>
            <li>• You can only pick one card per game win</li>
          </ul>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {draftCards.map((card, index) => (
            <div key={`${card.id}-${card.type}-${index}`} className="relative">
              <div className={`p-2 rounded-lg border-2 ${
                selectedCard?.id === card.id && selectedCard?.type === card.type
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}>
                <CardComponent
                  card={card}
                  className="cursor-pointer hover:scale-105 transition-transform"
                />
                <div className="mt-3 flex flex-col items-center gap-2">
                  <span className={`px-3 py-1 rounded text-sm font-bold ${getRarityColor(card.data.rarity)}`}>
                    {card.data.rarity.toUpperCase()}
                  </span>
                  <button
                    onClick={() => selectCard(card)}
                    disabled={selectedCard !== null}
                    className={`px-4 py-2 rounded font-bold transition-colors ${
                      selectedCard === null
                        ? 'bg-blue-500 text-white hover:bg-blue-600'
                        : selectedCard?.id === card.id && selectedCard?.type === card.type
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    {selectedCard?.id === card.id && selectedCard?.type === card.type
                      ? '✓ Selected!'
                      : selectedCard === null
                      ? 'Select This Card'
                      : 'Card Selected'
                    }
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {selectedCard && (
          <div className="mt-6 p-4 bg-green-100 rounded-lg text-center">
            <p className="text-green-800 font-bold">
              Great choice! {selectedCard.data.name} has been added to your deck.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DraftReward;
