import React from 'react';
import { Card, Player, Play, Modifier } from '../types/game';

interface CardComponentProps {
  card: Card;
  onClick?: () => void;
  className?: string;
}

const CardComponent: React.FC<CardComponentProps> = ({ card, onClick, className = '' }) => {
  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'border-gray-400 bg-gray-50';
      case 'rare': return 'border-blue-400 bg-blue-50';
      case 'epic': return 'border-purple-400 bg-purple-50';
      case 'legendary': return 'border-yellow-400 bg-yellow-50';
      default: return 'border-gray-400 bg-gray-50';
    }
  };

  const getCardTypeClass = (type: string) => {
    switch (type) {
      case 'player': return 'card-player';
      case 'play': return 'card-play';
      case 'modifier': return 'card-modifier';
      default: return 'card';
    }
  };

  const renderCardContent = () => {
    switch (card.type) {
      case 'player':
        const player = card.data as Player;
        return (
          <div>
            <div className="font-bold text-lg mb-2">{player.name}</div>
            <div className="text-sm text-gray-600 mb-2">
              {player.position} • {player.team}
            </div>
            <div className="space-y-1">
              {Object.entries(player.base_stats).map(([stat, value]) => (
                <div key={stat} className="flex justify-between text-sm">
                  <span className="capitalize">{stat}:</span>
                  <span className="font-bold">{value}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'play':
        const play = card.data as Play;
        return (
          <div>
            <div className="font-bold text-lg mb-2">{play.name}</div>
            <div className="text-sm text-gray-600 mb-2 capitalize">
              {play.play_type} Play
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Risk:</span>
                <span className="font-bold text-red-600">{play.base_stats.risk}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Reward:</span>
                <span className="font-bold text-green-600">{play.base_stats.reward}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Yards:</span>
                <span className="font-bold">{play.base_stats.yards}</span>
              </div>
            </div>
          </div>
        );

      case 'modifier':
        const modifier = card.data as Modifier;
        return (
          <div>
            <div className="font-bold text-lg mb-2">{modifier.name}</div>
            <div className="text-sm text-gray-600 mb-2 capitalize">
              {modifier.modifier_type} Modifier
            </div>
            <div className="space-y-1">
              {Object.entries(modifier.effect).map(([effect, value]) => (
                <div key={effect} className="flex justify-between text-sm">
                  <span className="capitalize">{effect.replace('_', ' ')}:</span>
                  <span className="font-bold text-purple-600">+{value}</span>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return <div>Unknown card type</div>;
    }
  };

  return (
    <div
      className={`
        ${getCardTypeClass(card.type)}
        ${getRarityColor(card.data.rarity)}
        ${onClick ? 'cursor-pointer hover:shadow-lg' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="text-xs font-bold uppercase text-gray-500">
          {card.data.rarity}
        </div>
        <div className="text-xs font-bold text-gray-600">
          ${card.data.cost}
        </div>
      </div>
      
      {renderCardContent()}
    </div>
  );
};

export default CardComponent;
