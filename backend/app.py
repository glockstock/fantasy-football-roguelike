from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import random
from typing import Dict, List, Any
import os

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'fantasy_football.db'

def init_db():
    """Initialize the database with game tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            team TEXT NOT NULL,
            base_stats TEXT NOT NULL,  -- JSON string
            rarity TEXT NOT NULL,
            cost INTEGER NOT NULL
        )
    ''')
    
    # Plays table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            play_type TEXT NOT NULL,
            base_stats TEXT NOT NULL,  -- JSON string
            rarity TEXT NOT NULL,
            cost INTEGER NOT NULL
        )
    ''')
    
    # Modifiers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modifiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            modifier_type TEXT NOT NULL,
            effect TEXT NOT NULL,  -- JSON string
            rarity TEXT NOT NULL,
            cost INTEGER NOT NULL
        )
    ''')
    
    # Game sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            current_season INTEGER DEFAULT 1,
            current_game INTEGER DEFAULT 1,
            current_drive INTEGER DEFAULT 1,
            deck TEXT NOT NULL,  -- JSON string
            score INTEGER DEFAULT 0,
            career_level TEXT DEFAULT 'high_school',
            career_progress TEXT DEFAULT '{"current_level": "high_school", "total_score": 0, "championships_won": 0, "super_bowls_won": 0, "hall_of_fame_points": 0}',
            game_progress TEXT DEFAULT '{"current_game": 1, "current_drive": 1, "drives_completed": 0, "games_won": 0, "total_drives_in_game": 4, "total_games_in_season": 10}',
            season_progress TEXT DEFAULT '{"current_season": 1, "games_won": 0, "seasons_won": 0, "total_games_in_season": 10, "total_seasons": 10}',
            deck_type TEXT DEFAULT 'balanced_offense',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_initial_data():
    """Seed the database with initial cards"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM players')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Sample players
    players = [
        ('Tom Brady', 'QB', 'Patriots', '{"passing": 95, "leadership": 90}', 'legendary', 50),
        ('Aaron Rodgers', 'QB', 'Packers', '{"passing": 92, "mobility": 85}', 'epic', 45),
        ('Josh Allen', 'QB', 'Bills', '{"passing": 88, "rushing": 90}', 'epic', 40),
        ('Cooper Kupp', 'WR', 'Rams', '{"catching": 95, "route_running": 90}', 'epic', 35),
        ('Davante Adams', 'WR', 'Raiders', '{"catching": 92, "speed": 88}', 'epic', 35),
        ('Derrick Henry', 'RB', 'Titans', '{"rushing": 95, "power": 90}', 'epic', 40),
        ('Travis Kelce', 'TE', 'Chiefs', '{"catching": 90, "blocking": 85}', 'epic', 30),
        ('Aaron Donald', 'DT', 'Rams', '{"pass_rush": 95, "run_stop": 90}', 'legendary', 50),
    ]
    
    cursor.executemany('INSERT INTO players (name, position, team, base_stats, rarity, cost) VALUES (?, ?, ?, ?, ?, ?)', players)
    
    # Sample plays
    plays = [
        ('Hail Mary', 'passing', '{"risk": 90, "reward": 95, "yards": 50}', 'epic', 25),
        ('Screen Pass', 'passing', '{"risk": 20, "reward": 60, "yards": 8}', 'common', 10),
        ('Draw Play', 'rushing', '{"risk": 30, "reward": 70, "yards": 12}', 'common', 12),
        ('Flea Flicker', 'trick', '{"risk": 80, "reward": 90, "yards": 40}', 'rare', 20),
        ('Wildcat', 'rushing', '{"risk": 60, "reward": 80, "yards": 25}', 'rare', 18),
        ('Play Action', 'passing', '{"risk": 40, "reward": 75, "yards": 20}', 'common', 15),
    ]
    
    cursor.executemany('INSERT INTO plays (name, play_type, base_stats, rarity, cost) VALUES (?, ?, ?, ?, ?)', plays)
    
    # Sample modifiers
    modifiers = [
        ('Red Zone Boost', 'scoring', '{"scoring_multiplier": 1.5}', 'rare', 20),
        ('Weather Advantage', 'environmental', '{"accuracy_boost": 10}', 'common', 15),
        ('Home Field', 'environmental', '{"all_stats_boost": 5}', 'common', 12),
        ('Clutch Factor', 'mental', '{"pressure_resistance": 15}', 'rare', 18),
        ('Momentum', 'temporary', '{"next_play_boost": 20}', 'epic', 25),
    ]
    
    cursor.executemany('INSERT INTO modifiers (name, modifier_type, effect, rarity, cost) VALUES (?, ?, ?, ?, ?)', modifiers)
    
    conn.commit()
    conn.close()

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game session"""
    data = request.get_json()
    player_name = data.get('player_name', 'Player')
    deck_type = data.get('deck_type', 'balanced_offense')
    
    # Get deck based on selected type
    initial_deck = get_deck_by_type(deck_type)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_sessions (player_name, deck, deck_type)
        VALUES (?, ?, ?)
    ''', (player_name, json.dumps(initial_deck), deck_type))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'session_id': session_id,
        'deck': initial_deck,
        'season': 1,
        'game': 1,
        'drive': 1,
        'score': 0,
        'career_level': {
            'level': 'high_school',
            'name': 'High School Coach',
            'description': 'Starting your coaching journey',
            'required_score': 0,
            'next_level': 'college'
        },
        'career_progress': {
            'current_level': 'high_school',
            'total_score': 0,
            'championships_won': 0,
            'super_bowls_won': 0,
            'hall_of_fame_points': 0
        },
        'game_progress': {
            'current_game': 1,
            'current_drive': 1,
            'drives_completed': 0,
            'games_won': 0,
            'total_drives_in_game': 4,
            'total_games_in_season': 10
        },
        'season_progress': {
            'current_season': 1,
            'games_won': 0,
            'seasons_won': 0,
            'total_games_in_season': 10,
            'total_seasons': 10
        }
    })

@app.route('/api/game/<int:session_id>/deck', methods=['GET'])
def get_deck(session_id):
    """Get current deck for a session"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT deck FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({'deck': json.loads(result[0])})

@app.route('/api/game/<int:session_id>/play-drive', methods=['POST'])
def play_drive(session_id):
    """Play a drive (sequence of cards)"""
    data = request.get_json()
    cards_played = data.get('cards', [])
    
    # Calculate drive score and results
    drive_result = calculate_drive_score(cards_played)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session state
    cursor.execute('SELECT current_game, current_drive, game_progress, season_progress FROM game_sessions WHERE id = ?', (session_id,))
    session_data = cursor.fetchone()
    
    if not session_data:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    current_game, current_drive, game_progress_json, season_progress_json = session_data
    game_progress = json.loads(game_progress_json)
    season_progress = json.loads(season_progress_json)
    
    # Update drive progress
    game_progress['drives_completed'] += 1
    
    # Check if drive was successful
    if drive_result['drive_successful']:
        # Move to next drive
        if current_drive < game_progress['total_drives_in_game']:
            # Next drive in same game
            game_progress['current_drive'] = current_drive + 1
            next_game = current_game
            next_drive = current_drive + 1
        else:
            # Game completed! Move to next game
            game_progress['games_won'] += 1
            season_progress['games_won'] += 1
            
            if current_game < game_progress['total_games_in_season']:
                # Next game in same season
                game_progress['current_game'] = current_game + 1
                game_progress['current_drive'] = 1
                game_progress['drives_completed'] = 0
                next_game = current_game + 1
                next_drive = 1
            else:
                # Season completed! Check for championship
                if season_progress['games_won'] == game_progress['total_games_in_season']:
                    season_progress['seasons_won'] += 1
                    # Start new season
                    if season_progress['current_season'] < season_progress['total_seasons']:
                        season_progress['current_season'] += 1
                        season_progress['games_won'] = 0
                        game_progress['current_game'] = 1
                        game_progress['current_drive'] = 1
                        game_progress['drives_completed'] = 0
                        game_progress['games_won'] = 0
                        next_game = 1
                        next_drive = 1
                    else:
                        # All seasons completed - Championship won!
                        next_game = current_game
                        next_drive = current_drive
                else:
                    # Season failed
                    next_game = current_game
                    next_drive = current_drive
    else:
        # Drive failed - game over
        next_game = current_game
        next_drive = current_drive
    
    # Update session with new progress
    cursor.execute('''
        UPDATE game_sessions 
        SET score = score + ?, 
            current_game = ?, 
            current_drive = ?,
            game_progress = ?,
            season_progress = ?
        WHERE id = ?
    ''', (drive_result['drive_score'], next_game, next_drive, 
          json.dumps(game_progress), json.dumps(season_progress), session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'drive_result': drive_result,
        'game_progress': game_progress,
        'season_progress': season_progress,
        'next_game': next_game,
        'next_drive': next_drive
    })

@app.route('/api/cards/players', methods=['GET'])
def get_players():
    """Get all available players"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players')
    players = []
    for row in cursor.fetchall():
        players.append({
            'id': row[0],
            'name': row[1],
            'position': row[2],
            'team': row[3],
            'base_stats': json.loads(row[4]),
            'rarity': row[5],
            'cost': row[6]
        })
    conn.close()
    return jsonify(players)

@app.route('/api/cards/plays', methods=['GET'])
def get_plays():
    """Get all available plays"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plays')
    plays = []
    for row in cursor.fetchall():
        plays.append({
            'id': row[0],
            'name': row[1],
            'play_type': row[2],
            'base_stats': json.loads(row[3]),
            'rarity': row[4],
            'cost': row[5]
        })
    conn.close()
    return jsonify(plays)

@app.route('/api/cards/modifiers', methods=['GET'])
def get_modifiers():
    """Get all available modifiers"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM modifiers')
    modifiers = []
    for row in cursor.fetchall():
        modifiers.append({
            'id': row[0],
            'name': row[1],
            'modifier_type': row[2],
            'effect': json.loads(row[3]),
            'rarity': row[4],
            'cost': row[5]
        })
    conn.close()
    return jsonify(modifiers)

@app.route('/api/deck-types', methods=['GET'])
def get_deck_types():
    """Get all available deck types"""
    return jsonify([
        {
            'id': 'balanced_offense',
            'name': 'Balanced Offense',
            'description': 'A well-rounded coaching philosophy focusing on both passing and rushing plays. Perfect for new coaches.',
            'difficulty': 'beginner',
            'cards': {
                'players': [1, 2],  # Tom Brady, Aaron Rodgers
                'plays': [1, 2, 3],  # Hail Mary, Screen Pass, Draw Play
                'modifiers': [1]  # Red Zone Boost
            }
        },
        {
            'id': 'air_raid',
            'name': 'Air Raid',
            'description': 'High-flying passing attack with explosive plays. High risk, high reward coaching style.',
            'difficulty': 'beginner',
            'cards': {
                'players': [1, 4],  # Tom Brady, Cooper Kupp
                'plays': [1, 5],  # Hail Mary, Play Action
                'modifiers': [2]  # Weather Advantage
            }
        },
        {
            'id': 'ground_and_pound',
            'name': 'Ground & Pound',
            'description': 'Power running game with strong defense. Consistent and reliable coaching approach.',
            'difficulty': 'beginner',
            'cards': {
                'players': [6, 7],  # Derrick Henry, Travis Kelce
                'plays': [2, 3],  # Screen Pass, Draw Play
                'modifiers': [3]  # Home Field
            }
        },
        {
            'id': 'trick_plays',
            'name': 'Trick Plays',
            'description': 'Unconventional plays and misdirection. Surprise your opponents with creative coaching!',
            'difficulty': 'intermediate',
            'cards': {
                'players': [2, 5],  # Aaron Rodgers, Davante Adams
                'plays': [4, 5],  # Flea Flicker, Wildcat
                'modifiers': [4]  # Clutch Factor
            },
            'unlock_requirement': {
                'career_level': 'college'
            }
        }
    ])

@app.route('/api/career-progress', methods=['GET'])
def get_career_progress():
    """Get career progression information"""
    return jsonify({
        'levels': [
            {
                'level': 'high_school',
                'name': 'High School Coach',
                'description': 'Starting your coaching journey',
                'required_score': 0,
                'next_level': 'college'
            },
            {
                'level': 'college',
                'name': 'College Coach',
                'description': 'Leading a college program',
                'required_score': 1000,
                'next_level': 'nfl'
            },
            {
                'level': 'nfl',
                'name': 'NFL Coach',
                'description': 'Coaching in the National Football League',
                'required_score': 5000,
                'next_level': 'hall_of_fame'
            },
            {
                'level': 'hall_of_fame',
                'name': 'Hall of Fame Coach',
                'description': 'Legendary coaching career',
                'required_score': 20000,
                'next_level': None
            }
        ]
    })

def get_deck_by_type(deck_type: str):
    """Get deck configuration based on deck type"""
    deck_configs = {
        'balanced_offense': {
            'players': [1, 2],  # Tom Brady, Aaron Rodgers
            'plays': [1, 2, 3],  # Hail Mary, Screen Pass, Draw Play
            'modifiers': [1]  # Red Zone Boost
        },
        'air_raid': {
            'players': [1, 4],  # Tom Brady, Cooper Kupp
            'plays': [1, 5],  # Hail Mary, Play Action
            'modifiers': [2]  # Weather Advantage
        },
        'ground_and_pound': {
            'players': [6, 7],  # Derrick Henry, Travis Kelce
            'plays': [2, 3],  # Screen Pass, Draw Play
            'modifiers': [3]  # Home Field
        },
        'trick_plays': {
            'players': [2, 5],  # Aaron Rodgers, Davante Adams
            'plays': [4, 5],  # Flea Flicker, Wildcat
            'modifiers': [4]  # Clutch Factor
        }
    }
    
    return deck_configs.get(deck_type, deck_configs['balanced_offense'])

def get_initial_deck():
    """Get starting deck for new players (legacy function)"""
    return get_deck_by_type('balanced_offense')

def calculate_drive_score(cards_played):
    """Calculate score and results for a drive based on cards played"""
    if not cards_played:
        return {
            'drive_score': 0,
            'cards_played': [],
            'drive_successful': False,
            'yards_gained': 0,
            'points_scored': 0
        }
    
    # Basic drive scoring logic
    base_score = len(cards_played) * 10
    yards_gained = 0
    points_scored = 0
    drive_successful = False
    
    # Calculate yards and points based on cards played
    for card in cards_played:
        if card.get('type') == 'play':
            play_stats = card.get('data', {}).get('base_stats', {})
            yards_gained += play_stats.get('yards', 0)
            
            # Check for scoring plays
            play_name = card.get('data', {}).get('name', '').lower()
            if any(scoring_term in play_name for scoring_term in ['touchdown', 'field goal', 'hail mary']):
                if 'touchdown' in play_name:
                    points_scored += 6
                elif 'field goal' in play_name:
                    points_scored += 3
                elif 'hail mary' in play_name and yards_gained >= 40:
                    points_scored += 6  # Long TD
    
    # Drive is successful if we gain at least 10 yards or score
    drive_successful = yards_gained >= 10 or points_scored > 0
    
    # Bonus points for successful drives
    if drive_successful:
        base_score += yards_gained * 2
        base_score += points_scored * 10
    
    return {
        'drive_score': base_score,
        'cards_played': cards_played,
        'drive_successful': drive_successful,
        'yards_gained': yards_gained,
        'points_scored': points_scored
    }

if __name__ == '__main__':
    init_db()
    seed_initial_data()
    app.run(debug=True, port=5000)
