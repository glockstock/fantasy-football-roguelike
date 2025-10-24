import React, { useState, useEffect } from 'react';
import { Card } from '../types/game';
import CardComponent from './CardComponent';

interface CardShopProps {
  sessionId: number;
  onClose: () => void;
  onUpdateCoachingPoints: (points: number) => void;
}

const CardShop: React.FC<CardShopProps> = ({ sessionId, onClose, onUpdateCoachingPoints }) => {
  const [shopCards, setShopCards] = useState<Card[]>([]);
  const [coachingPoints, setCoachingPoints] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchShop();
  }, [sessionId]);

  const fetchShop = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/game/${sessionId}/shop`);
      const data = await response.json();
      
      if (response.ok) {
        setShopCards(data.shop_cards);
        setCoachingPoints(data.coaching_points);
      } else {
        setError(data.error || 'Failed to load shop');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const buyCard = async (card: Card) => {
    try {
      const response = await fetch(`/api/game/${sessionId}/buy-card`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ card }),
      });

      const data = await response.json();

      if (response.ok) {
        // Remove card from shop
        setShopCards(prev => prev.filter(c => c.id !== card.id || c.type !== card.type));
        // Update coaching points
        setCoachingPoints(data.remaining_points);
        onUpdateCoachingPoints(data.remaining_points);
        alert(`Purchased ${card.data.name} for ${card.data.cost} coaching points!`);
      } else {
        alert(data.error || 'Failed to buy card');
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
          <div className="text-center">Loading shop...</div>
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
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Free Agency Shop</h2>
          <div className="flex items-center gap-4">
            <div className="text-lg font-bold text-green-600">
              Coaching Points: {coachingPoints}
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Close Shop
            </button>
          </div>
        </div>

        <div className="mb-4 p-4 bg-gray-100 rounded-lg">
          <h3 className="font-bold text-gray-800 mb-2">Shop Rules:</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Spend coaching points earned from successful drives</li>
            <li>• Cards scale in cost by rarity: Common (50), Rare (150), Epic (300), Legendary (500)</li>
            <li>• Shop refreshes with 6 random cards each game</li>
            <li>• You can sell cards from your deck for 50% refund</li>
          </ul>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {shopCards.map((card, index) => (
            <div key={`${card.id}-${card.type}-${index}`} className="relative">
              <CardComponent
                card={card}
                className="cursor-pointer hover:scale-105 transition-transform"
              />
              <div className="mt-2 flex items-center justify-between">
                <span className={`px-2 py-1 rounded text-xs font-bold ${getRarityColor(card.data.rarity)}`}>
                  {card.data.rarity.toUpperCase()}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-green-600">
                    {card.data.cost} CP
                  </span>
                  <button
                    onClick={() => buyCard(card)}
                    disabled={coachingPoints < card.data.cost}
                    className={`px-3 py-1 rounded text-sm font-bold ${
                      coachingPoints >= card.data.cost
                        ? 'bg-green-500 text-white hover:bg-green-600'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    Buy
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {shopCards.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No cards available in shop
          </div>
        )}
      </div>
    </div>
  );
};

export default CardShop;