import React, { useState, useEffect } from 'react';
import { DeckType } from '../types/game';

interface DeckSelectionProps {
  onDeckSelected: (deckType: DeckType) => void;
  onBack: () => void;
  playerName: string;
  careerLevel: string;
}

const DeckSelection: React.FC<DeckSelectionProps> = ({ onDeckSelected, onBack, playerName, careerLevel }) => {
  const [deckTypes, setDeckTypes] = useState<DeckType[]>([]);
  const [selectedDeck, setSelectedDeck] = useState<DeckType | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDeckTypes();
  }, []);

  const fetchDeckTypes = async () => {
    try {
      const response = await fetch('/api/deck-types');
      const data = await response.json();
      setDeckTypes(data);
    } catch (error) {
      console.error('Failed to fetch deck types:', error);
      // Fallback to default deck types
      setDeckTypes(getDefaultDeckTypes());
    } finally {
      setIsLoading(false);
    }
  };

  const getDefaultDeckTypes = (): DeckType[] => [
    {
      id: 'balanced_offense',
      name: 'Balanced Offense',
      description: 'A well-rounded coaching philosophy focusing on both passing and rushing plays. Perfect for new coaches.',
      difficulty: 'beginner',
      cards: {
        players: [1, 2], // Tom Brady, Aaron Rodgers
        plays: [1, 2, 3], // Hail Mary, Screen Pass, Draw Play
        modifiers: [1] // Red Zone Boost
      }
    },
    {
      id: 'air_raid',
      name: 'Air Raid',
      description: 'High-flying passing attack with explosive plays. High risk, high reward coaching style.',
      difficulty: 'beginner',
      cards: {
        players: [1, 4], // Tom Brady, Cooper Kupp
        plays: [1, 5], // Hail Mary, Play Action
        modifiers: [2] // Weather Advantage
      }
    },
    {
      id: 'ground_and_pound',
      name: 'Ground & Pound',
      description: 'Power running game with strong defense. Consistent and reliable coaching approach.',
      difficulty: 'beginner',
      cards: {
        players: [6, 7], // Derrick Henry, Travis Kelce
        plays: [2, 3], // Screen Pass, Draw Play
        modifiers: [3] // Home Field
      }
    },
    {
      id: 'trick_plays',
      name: 'Trick Plays',
      description: 'Unconventional plays and misdirection. Surprise your opponents with creative coaching!',
      difficulty: 'intermediate',
      cards: {
        players: [2, 5], // Aaron Rodgers, Davante Adams
        plays: [4, 5], // Flea Flicker, Wildcat
        modifiers: [4] // Clutch Factor
      },
      unlock_requirement: {
        career_level: 'college'
      }
    }
  ];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-400 bg-green-900';
      case 'intermediate': return 'text-yellow-400 bg-yellow-900';
      case 'advanced': return 'text-red-400 bg-red-900';
      default: return 'text-gray-400 bg-gray-900';
    }
  };

  const isDeckUnlocked = (deck: DeckType) => {
    if (!deck.unlock_requirement) return true;
    
    if (deck.unlock_requirement.career_level) {
      const levelOrder = ['high_school', 'college', 'nfl', 'hall_of_fame'];
      const currentLevelIndex = levelOrder.indexOf(careerLevel);
      const requiredLevelIndex = levelOrder.indexOf(deck.unlock_requirement.career_level);
      return currentLevelIndex >= requiredLevelIndex;
    }
    
    return true;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-football-green to-field-green flex items-center justify-center">
        <div className="text-white text-2xl">Loading deck types...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-football-green to-field-green">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <button
            onClick={onBack}
            className="absolute left-4 top-4 bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            ← Back
          </button>
          
          <h1 className="text-4xl font-bold text-white mb-2">
            {careerLevel === 'nfl' ? 'Draft Your Team' : 'Recruit Your Team'}
          </h1>
          <p className="text-gray-300">
            Welcome, Coach {playerName}! {careerLevel === 'nfl' ? 'Draft your roster' : 'Recruit your players'} for this season.
          </p>
        </div>

        {/* Deck Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {deckTypes.map((deck) => {
            const isUnlocked = isDeckUnlocked(deck);
            const isSelected = selectedDeck?.id === deck.id;
            
            return (
              <div
                key={deck.id}
                className={`bg-black bg-opacity-30 rounded-lg p-6 backdrop-blur-sm border-2 transition-all duration-200 cursor-pointer ${
                  isSelected 
                    ? 'border-blue-500 bg-blue-900 bg-opacity-20' 
                    : isUnlocked 
                      ? 'border-gray-600 hover:border-gray-400 hover:bg-opacity-40' 
                      : 'border-gray-800 bg-opacity-20 cursor-not-allowed'
                }`}
                onClick={() => isUnlocked && setSelectedDeck(deck)}
              >
                {/* Deck Header */}
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-white">{deck.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getDifficultyColor(deck.difficulty)}`}>
                    {deck.difficulty}
                  </span>
                </div>

                {/* Description */}
                <p className="text-gray-300 mb-4 text-sm">
                  {deck.description}
                </p>
                
                {/* Coaching Philosophy */}
                <div className="mb-4">
                  <h5 className="text-white font-semibold text-sm mb-2">Coaching Philosophy:</h5>
                  <p className="text-gray-400 text-xs">
                    {deck.id === 'balanced_offense' && 'Balanced approach with both passing and running'}
                    {deck.id === 'air_raid' && 'High-flying passing attack with explosive plays'}
                    {deck.id === 'ground_and_pound' && 'Power running game with strong defense'}
                    {deck.id === 'trick_plays' && 'Unconventional plays and misdirection'}
                  </p>
                </div>

                {/* Lock Status */}
                {!isUnlocked && (
                  <div className="text-center py-4">
                    <div className="text-2xl mb-2">🔒</div>
                    <p className="text-gray-500 text-sm">
                      Requires: {deck.unlock_requirement?.career_level?.replace('_', ' ').toUpperCase()}
                    </p>
                  </div>
                )}

                {/* Roster Preview */}
                {isUnlocked && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Players:</span>
                      <span className="text-white">{deck.cards.players.length}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Playbook:</span>
                      <span className="text-white">{deck.cards.plays.length}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Coaching:</span>
                      <span className="text-white">{deck.cards.modifiers.length}</span>
                    </div>
                  </div>
                )}

                {/* Selection Indicator */}
                {isSelected && (
                  <div className="mt-4 text-center">
                    <div className="text-green-400 text-sm font-semibold">✓ Selected</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Start Game Button */}
        <div className="text-center mt-8">
          <button
            onClick={() => selectedDeck && onDeckSelected(selectedDeck)}
            disabled={!selectedDeck}
            className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-bold py-4 px-8 rounded-lg text-xl transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100"
          >
            🏈 Start Season
          </button>
          
          {!selectedDeck && (
            <p className="text-gray-400 text-sm mt-2">
              Select a coaching philosophy to begin your season
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default DeckSelection;
