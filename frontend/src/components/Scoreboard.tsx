import React from 'react';
import { useGame } from '../context/GameContext';

const Scoreboard: React.FC = () => {
  const { gameState } = useGame();

  if (!gameState) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-500">Loading scoreboard...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Scoreboard</h2>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Score:</span>
          <span className="text-2xl font-bold text-green-600">{gameState.score}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Coaching Points:</span>
          <span className="text-xl font-bold text-blue-600">{gameState.coaching_points}</span>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Season Progress</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Season:</span>
              <span className="font-semibold">{gameState.season_progress.current_season}/{gameState.season_progress.total_seasons}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(gameState.season_progress.current_season / gameState.season_progress.total_seasons) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Games Won:</span>
              <span className="font-semibold">{gameState.season_progress.games_won}/{gameState.season_progress.total_games_in_season}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(gameState.season_progress.games_won / gameState.season_progress.total_games_in_season) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Championships:</span>
              <span className="font-semibold text-yellow-600">{gameState.season_progress.seasons_won}</span>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Game Progress</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Game:</span>
              <span className="font-semibold">{gameState.game_progress.current_game}/{gameState.game_progress.total_games_in_season}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(gameState.game_progress.current_game / gameState.game_progress.total_games_in_season) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Drive:</span>
              <span className="font-semibold">{gameState.game_progress.current_drive}/{gameState.game_progress.total_drives_in_game}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(gameState.game_progress.current_drive / gameState.game_progress.total_drives_in_game) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Drives Completed:</span>
              <span className="font-semibold">{gameState.game_progress.drives_completed}</span>
            </div>
          </div>
        </div>
        
        <div className="pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-500">
            <div className="flex justify-between mb-1">
              <span>Deck Size:</span>
              <span>
                {gameState.deck.players.length + gameState.deck.plays.length + gameState.deck.modifiers.length} cards
              </span>
            </div>
            <div className="flex justify-between">
              <span>Players:</span>
              <span>{gameState.deck.players.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Plays:</span>
              <span>{gameState.deck.plays.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Modifiers:</span>
              <span>{gameState.deck.modifiers.length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Scoreboard;
