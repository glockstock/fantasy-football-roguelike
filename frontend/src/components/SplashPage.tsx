import React, { useState } from 'react';

interface SplashPageProps {
  onStartNewRun: (playerName: string) => void;
  careerProgress?: {
    current_level: string;
    total_score: number;
    championships_won: number;
    super_bowls_won: number;
    hall_of_fame_points: number;
  };
}

const SplashPage: React.FC<SplashPageProps> = ({ onStartNewRun, careerProgress }) => {
  const [playerName, setPlayerName] = useState('');

  const getCareerLevelInfo = (level: string) => {
    const levels = {
      'high_school': { name: 'High School Coach', color: 'text-yellow-400', icon: '🏈' },
      'college': { name: 'College Coach', color: 'text-blue-400', icon: '🎓' },
      'nfl': { name: 'NFL Coach', color: 'text-green-400', icon: '🏆' },
      'hall_of_fame': { name: 'Hall of Fame Coach', color: 'text-purple-400', icon: '⭐' }
    };
    return levels[level as keyof typeof levels] || levels['high_school'];
  };

  const currentLevelInfo = getCareerLevelInfo(careerProgress?.current_level || 'high_school');

  return (
    <div className="min-h-screen bg-gradient-to-br from-football-green to-field-green flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-4">
        {/* Main Title */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold text-white mb-4">
            Fantasy Football Roguelike
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Build your coaching legacy from high school to the Hall of Fame
          </p>
        </div>

        {/* Career Progress Display */}
        {careerProgress && (
          <div className="bg-black bg-opacity-30 rounded-lg p-6 mb-8 backdrop-blur-sm">
            <div className="text-center mb-6">
              <div className="text-4xl mb-2">{currentLevelInfo.icon}</div>
              <h2 className={`text-2xl font-bold ${currentLevelInfo.color}`}>
                {currentLevelInfo.name}
              </h2>
              <p className="text-gray-300 mt-2">
                Total Career Score: {careerProgress.total_score.toLocaleString()}
              </p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-yellow-400">{careerProgress.championships_won}</div>
                <div className="text-sm text-gray-300">State Championships</div>
              </div>
              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-400">{careerProgress.championships_won}</div>
                <div className="text-sm text-gray-300">National Championships</div>
              </div>
              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-400">{careerProgress.super_bowls_won}</div>
                <div className="text-sm text-gray-300">Super Bowls</div>
              </div>
              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-400">{careerProgress.hall_of_fame_points}</div>
                <div className="text-sm text-gray-300">Hall of Fame Points</div>
              </div>
            </div>
          </div>
        )}

        {/* Player Name Input */}
        <div className="bg-black bg-opacity-30 rounded-lg p-6 mb-8 backdrop-blur-sm">
          <label htmlFor="playerName" className="block text-white text-lg font-semibold mb-3">
            Coach Name
          </label>
          <input
            id="playerName"
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Enter your coach name..."
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none text-lg"
          />
        </div>

        {/* Action Buttons */}
        <div className="text-center space-y-4">
          <button
            onClick={() => onStartNewRun(playerName)}
            disabled={!playerName.trim()}
            className="w-full max-w-md mx-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-bold py-4 px-8 rounded-lg text-xl transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100"
          >
            🏈 Start New Run
          </button>
          
          <p className="text-gray-400 text-sm">
            {!playerName.trim() ? 'Enter your coach name to begin' : 'Ready to build your legacy!'}
          </p>
        </div>

        {/* Game Description */}
        <div className="mt-12 bg-black bg-opacity-20 rounded-lg p-6 backdrop-blur-sm">
          <h3 className="text-white text-xl font-semibold mb-4 text-center">How to Play</h3>
          <div className="grid md:grid-cols-3 gap-6 text-gray-300">
            <div className="text-center">
              <div className="text-3xl mb-2">🎯</div>
              <h4 className="font-semibold text-white mb-2">Recruit Your Team</h4>
              <p className="text-sm">Choose your coaching philosophy and recruit players that fit your system</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🏃</div>
              <h4 className="font-semibold text-white mb-2">Play Out the Season</h4>
              <p className="text-sm">Call plays and execute drives to score touchdowns and win games</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🏆</div>
              <h4 className="font-semibold text-white mb-2">Climb the Ranks</h4>
              <p className="text-sm">Progress from high school to NFL and eventually the Hall of Fame</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SplashPage;
