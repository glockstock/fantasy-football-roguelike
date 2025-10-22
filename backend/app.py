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
            current_run INTEGER DEFAULT 1,
            deck TEXT NOT NULL,  -- JSON string
            score INTEGER DEFAULT 0,
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
    
    # Create initial deck with basic cards
    initial_deck = get_initial_deck()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_sessions (player_name, deck)
        VALUES (?, ?)
    ''', (player_name, json.dumps(initial_deck)))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'session_id': session_id,
        'deck': initial_deck,
        'season': 1,
        'run': 1,
        'score': 0
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

@app.route('/api/game/<int:session_id>/play-run', methods=['POST'])
def play_run(session_id):
    """Play a run (sequence of cards)"""
    data = request.get_json()
    cards_played = data.get('cards', [])
    
    # Calculate run score
    run_score = calculate_run_score(cards_played)
    
    # Update session
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE game_sessions 
        SET score = score + ?, current_run = current_run + 1
        WHERE id = ?
    ''', (run_score, session_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        'run_score': run_score,
        'cards_played': cards_played,
        'valid_run': run_score > 0
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

def get_initial_deck():
    """Get starting deck for new players"""
    return {
        'players': [1, 2],  # IDs of starting players
        'plays': [1, 2, 3],  # IDs of starting plays
        'modifiers': [1]  # IDs of starting modifiers
    }

def calculate_run_score(cards_played):
    """Calculate score for a run based on cards played"""
    if not cards_played:
        return 0
    
    # Basic scoring logic - can be expanded
    base_score = len(cards_played) * 10
    
    # Check if run ends with scoring play
    last_card = cards_played[-1]
    if last_card.get('type') == 'play' and 'scoring' in last_card.get('name', '').lower():
        base_score *= 2
    
    return base_score

if __name__ == '__main__':
    init_db()
    seed_initial_data()
    app.run(debug=True, port=5000)
