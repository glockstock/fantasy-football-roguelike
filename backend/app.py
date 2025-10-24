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
            synergy_tags TEXT DEFAULT '[]',  -- JSON string
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
            synergy_tags TEXT DEFAULT '[]',  -- JSON string
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
            synergy_tags TEXT DEFAULT '[]',  -- JSON string
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
            hand TEXT DEFAULT '[]',  -- JSON string
            deck_cards TEXT DEFAULT '[]',  -- JSON string
            bench TEXT DEFAULT '[]',  -- JSON string
            discard_pile TEXT DEFAULT '[]',  -- JSON string
            field TEXT DEFAULT '[]',  -- JSON string
            score INTEGER DEFAULT 0,
            coaching_points INTEGER DEFAULT 0,
            downs INTEGER DEFAULT 1,
            distance INTEGER DEFAULT 0,
            yards_to_go INTEGER DEFAULT 10,
            pressure_level INTEGER DEFAULT 0,
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
    
    # Sample players with synergy tags
    players = [
        ('Tom Brady', 'QB', 'Patriots', '{"passing": 95, "leadership": 90}', '["pocket_passer", "clutch", "deep_ball"]', 'legendary', 50),
        ('Aaron Rodgers', 'QB', 'Packers', '{"passing": 92, "mobility": 85}', '["mobile_qb", "accuracy", "play_action"]', 'epic', 45),
        ('Josh Allen', 'QB', 'Bills', '{"passing": 88, "rushing": 90}', '["dual_threat", "power", "deep_ball"]', 'epic', 40),
        ('Cooper Kupp', 'WR', 'Rams', '{"catching": 95, "route_running": 90}', '["slot_receiver", "route_running", "possession"]', 'epic', 35),
        ('Davante Adams', 'WR', 'Raiders', '{"catching": 92, "speed": 88}', '["deep_threat", "speed", "red_zone"]', 'epic', 35),
        ('Derrick Henry', 'RB', 'Titans', '{"rushing": 95, "power": 90}', '["power_back", "short_yardage", "goal_line"]', 'epic', 40),
        ('Travis Kelce', 'TE', 'Chiefs', '{"catching": 90, "blocking": 85}', '["receiving_te", "red_zone", "mismatch"]', 'epic', 30),
        ('Aaron Donald', 'DT', 'Rams', '{"pass_rush": 95, "run_stop": 90}', '["pass_rush", "run_stop", "pressure"]', 'legendary', 50),
        ('Tyreek Hill', 'WR', 'Dolphins', '{"catching": 88, "speed": 98}', '["deep_threat", "speed", "big_play"]', 'epic', 38),
        ('Christian McCaffrey', 'RB', '49ers', '{"rushing": 90, "catching": 85}', '["receiving_back", "versatile", "screen_pass"]', 'epic', 42),
        ('Patrick Mahomes', 'QB', 'Chiefs', '{"passing": 96, "mobility": 80}', '["mobile_qb", "deep_ball", "clutch"]', 'legendary', 55),
        ('Stefon Diggs', 'WR', 'Bills', '{"catching": 90, "route_running": 88}', '["possession", "route_running", "clutch"]', 'epic', 36),
        ('Lamar Jackson', 'QB', 'Ravens', '{"passing": 85, "rushing": 95}', '["mobile_qb", "dual_threat", "big_play"]', 'epic', 38),
        ('Saquon Barkley', 'RB', 'Giants', '{"rushing": 90, "catching": 80}', '["versatile", "receiving_back", "big_play"]', 'epic', 35),
        ('Justin Jefferson', 'WR', 'Vikings', '{"catching": 94, "speed": 90}', '["deep_threat", "possession", "clutch"]', 'epic', 37),
        ('Ja\'Marr Chase', 'WR', 'Bengals', '{"catching": 90, "speed": 92}', '["deep_threat", "big_play", "clutch"]', 'epic', 36),
        ('CeeDee Lamb', 'WR', 'Cowboys', '{"catching": 92, "route_running": 90}', '["possession", "versatile", "clutch"]', 'rare', 30),
        ('A.J. Brown', 'WR', 'Eagles', '{"catching": 91, "speed": 88}', '["possession", "red_zone", "clutch"]', 'rare', 29),
        ('DK Metcalf', 'WR', 'Seahawks', '{"catching": 88, "speed": 94}', '["deep_threat", "big_play", "red_zone"]', 'rare', 28),
        ('DeAndre Hopkins', 'WR', 'Titans', '{"catching": 95, "route_running": 93}', '["possession", "clutch", "red_zone"]', 'rare', 27),
        ('Mike Evans', 'WR', 'Buccaneers', '{"catching": 92, "speed": 87}', '["red_zone", "possession", "clutch"]', 'rare', 26),
        ('Keenan Allen', 'WR', 'Chargers', '{"catching": 94, "route_running": 92}', '["possession", "slot_receiver", "clutch"]', 'rare', 25),
        ('Amari Cooper', 'WR', 'Browns', '{"catching": 90, "route_running": 89}', '["possession", "versatile", "clutch"]', 'rare', 24),
        ('Terry McLaurin', 'WR', 'Commanders', '{"catching": 89, "speed": 91}', '["deep_threat", "versatile", "clutch"]', 'rare', 23),
        ('Diontae Johnson', 'WR', 'Panthers', '{"catching": 88, "route_running": 86}', '["possession", "versatile", "clutch"]', 'common', 20),
        ('Brandin Cooks', 'WR', 'Texans', '{"catching": 85, "speed": 93}', '["deep_threat", "speed", "versatile"]', 'common', 18),
        ('Tyler Lockett', 'WR', 'Seahawks', '{"catching": 87, "speed": 90}', '["deep_threat", "versatile", "clutch"]', 'common', 19),
        ('Marquise Brown', 'WR', 'Cardinals', '{"catching": 86, "speed": 95}', '["deep_threat", "speed", "big_play"]', 'common', 17),
        ('Courtland Sutton', 'WR', 'Broncos', '{"catching": 88, "speed": 87}', '["possession", "red_zone", "versatile"]', 'common', 16),
        ('Jerry Jeudy', 'WR', 'Broncos', '{"catching": 87, "route_running": 88}', '["possession", "versatile", "clutch"]', 'common', 18),
        ('Rashod Bateman', 'WR', 'Ravens', '{"catching": 86, "route_running": 85}', '["possession", "versatile", "clutch"]', 'common', 15),
        ('Elijah Moore', 'WR', 'Browns', '{"catching": 85, "speed": 89}', '["possession", "versatile", "clutch"]', 'common', 14),
        ('Gabriel Davis', 'WR', 'Bills', '{"catching": 84, "speed": 88}', '["deep_threat", "versatile", "clutch"]', 'common', 13),
        ('Van Jefferson', 'WR', 'Rams', '{"catching": 83, "route_running": 82}', '["possession", "versatile", "clutch"]', 'common', 12),
        ('Josh Jacobs', 'RB', 'Raiders', '{"rushing": 90, "power": 88}', '["power_back", "workhorse", "versatile"]', 'rare', 30),
        ('Austin Ekeler', 'RB', 'Chargers', '{"rushing": 80, "catching": 88}', '["receiving_back", "versatile", "clutch"]', 'rare', 28),
        ('Alvin Kamara', 'RB', 'Saints', '{"rushing": 82, "catching": 90}', '["receiving_back", "versatile", "clutch"]', 'rare', 29),
        ('Dalvin Cook', 'RB', 'Jets', '{"rushing": 85, "speed": 91}', '["versatile", "workhorse", "clutch"]', 'rare', 27),
        ('Ezekiel Elliott', 'RB', 'Cowboys', '{"rushing": 88, "power": 86}', '["power_back", "workhorse", "versatile"]', 'rare', 26),
        ('Leonard Fournette', 'RB', 'Bills', '{"rushing": 89, "power": 87}', '["power_back", "workhorse", "versatile"]', 'common', 22),
        ('Miles Sanders', 'RB', 'Panthers', '{"rushing": 83, "speed": 88}', '["versatile", "workhorse", "clutch"]', 'common', 21),
        ('Tony Pollard', 'RB', 'Cowboys', '{"rushing": 80, "speed": 90}', '["versatile", "receiving_back", "clutch"]', 'common', 20),
        ('Rhamondre Stevenson', 'RB', 'Patriots', '{"rushing": 87, "power": 85}', '["power_back", "versatile", "clutch"]', 'common', 19),
        ('Kenneth Walker III', 'RB', 'Seahawks', '{"rushing": 84, "speed": 89}', '["versatile", "workhorse", "clutch"]', 'common', 18),
        ('Breece Hall', 'RB', 'Jets', '{"rushing": 85, "speed": 91}', '["versatile", "workhorse", "clutch"]', 'common', 17),
        ('Javonte Williams', 'RB', 'Broncos', '{"rushing": 86, "power": 87}', '["power_back", "versatile", "clutch"]', 'common', 16),
        ('Cam Akers', 'RB', 'Vikings', '{"rushing": 83, "speed": 88}', '["versatile", "workhorse", "clutch"]', 'common', 15),
        ('Dameon Pierce', 'RB', 'Texans', '{"rushing": 88, "power": 86}', '["power_back", "workhorse", "versatile"]', 'common', 14),
        ('James Robinson', 'RB', 'Giants', '{"rushing": 85, "power": 85}', '["power_back", "workhorse", "versatile"]', 'common', 13),
        ('Travis Etienne', 'RB', 'Jaguars', '{"rushing": 80, "speed": 92}', '["versatile", "receiving_back", "clutch"]', 'common', 16),
        ('Najee Harris', 'RB', 'Steelers', '{"rushing": 89, "power": 84}', '["power_back", "workhorse", "versatile"]', 'common', 17),
        ('Joe Mixon', 'RB', 'Bengals', '{"rushing": 87, "power": 86}', '["power_back", "versatile", "clutch"]', 'common', 18),
        ('Aaron Jones', 'RB', 'Packers', '{"rushing": 82, "catching": 85}', '["versatile", "receiving_back", "clutch"]', 'common', 19),
        ('David Montgomery', 'RB', 'Lions', '{"rushing": 86, "power": 85}', '["power_back", "workhorse", "versatile"]', 'common', 15),
        ('Mark Andrews', 'TE', 'Ravens', '{"catching": 92, "blocking": 75}', '["receiving_te", "red_zone", "clutch"]', 'rare', 32),
        ('George Kittle', 'TE', '49ers', '{"catching": 90, "blocking": 85}', '["versatile", "possession", "clutch"]', 'rare', 30),
        ('Darren Waller', 'TE', 'Giants', '{"catching": 88, "speed": 85}', '["receiving_te", "versatile", "clutch"]', 'rare', 28),
        ('Kyle Pitts', 'TE', 'Falcons', '{"catching": 89, "speed": 88}', '["receiving_te", "versatile", "clutch"]', 'rare', 29),
        ('T.J. Hockenson', 'TE', 'Vikings', '{"catching": 87, "blocking": 80}', '["possession", "versatile", "clutch"]', 'common', 24),
        ('Dallas Goedert', 'TE', 'Eagles', '{"catching": 85, "blocking": 82}', '["possession", "versatile", "clutch"]', 'common', 23),
        ('Evan Engram', 'TE', 'Jaguars', '{"catching": 83, "speed": 85}', '["receiving_te", "versatile", "clutch"]', 'common', 22),
        ('Pat Freiermuth', 'TE', 'Steelers', '{"catching": 84, "blocking": 78}', '["possession", "versatile", "clutch"]', 'common', 21),
        ('Cole Kmet', 'TE', 'Bears', '{"catching": 82, "blocking": 75}', '["possession", "versatile", "clutch"]', 'common', 20),
        ('Noah Fant', 'TE', 'Seahawks', '{"catching": 81, "speed": 87}', '["receiving_te", "versatile", "clutch"]', 'common', 19),
        ('Hunter Henry', 'TE', 'Patriots', '{"catching": 83, "blocking": 80}', '["possession", "versatile", "clutch"]', 'common', 18),
        ('Gerald Everett', 'TE', 'Chargers', '{"catching": 80, "speed": 82}', '["receiving_te", "versatile", "clutch"]', 'common', 17),
        ('Tyler Higbee', 'TE', 'Rams', '{"catching": 81, "blocking": 78}', '["possession", "versatile", "clutch"]', 'common', 16),
        ('Logan Thomas', 'TE', 'Commanders', '{"catching": 79, "blocking": 75}', '["possession", "versatile", "clutch"]', 'common', 15),
        ('Robert Tonyan', 'TE', 'Bears', '{"catching": 80, "blocking": 72}', '["possession", "versatile", "clutch"]', 'common', 14),
        ('Zach Ertz', 'TE', 'Cardinals', '{"catching": 82, "blocking": 78}', '["possession", "versatile", "clutch"]', 'common', 13),
        ('C.J. Uzomah', 'TE', 'Jets', '{"catching": 78, "blocking": 80}', '["possession", "versatile", "clutch"]', 'common', 12),
        ('Jonnu Smith', 'TE', 'Dolphins', '{"catching": 77, "speed": 82}', '["receiving_te", "versatile", "clutch"]', 'common', 11),
        ('Mike Gesicki', 'TE', 'Patriots', '{"catching": 79, "speed": 80}', '["receiving_te", "versatile", "clutch"]', 'common', 10),
        ('Hayden Hurst', 'TE', 'Panthers', '{"catching": 76, "blocking": 72}', '["possession", "versatile", "clutch"]', 'common', 9),
        ('Russell Wilson', 'QB', 'Broncos', '{"passing": 90, "mobility": 85}', '["mobile_qb", "clutch", "versatile"]', 'epic', 38),
        ('Dak Prescott', 'QB', 'Cowboys', '{"passing": 88, "accuracy": 90}', '["accuracy", "clutch", "versatile"]', 'epic', 36),
        ('Matthew Stafford', 'QB', 'Rams', '{"passing": 92, "arm_strength": 88}', '["arm_strength", "clutch", "leadership"]', 'epic', 34),
        ('Kirk Cousins', 'QB', 'Vikings', '{"passing": 85, "accuracy": 90}', '["accuracy", "clutch", "versatile"]', 'rare', 30),
        ('Ryan Tannehill', 'QB', 'Titans', '{"passing": 82, "mobility": 80}', '["mobile_qb", "versatile", "clutch"]', 'rare', 28),
        ('Carson Wentz', 'QB', 'Rams', '{"passing": 88, "arm_strength": 82}', '["arm_strength", "versatile", "clutch"]', 'rare', 26),
        ('Baker Mayfield', 'QB', 'Buccaneers', '{"passing": 85, "mobility": 78}', '["mobile_qb", "versatile", "clutch"]', 'rare', 24),
        ('Jared Goff', 'QB', 'Lions', '{"passing": 82, "accuracy": 85}', '["accuracy", "versatile", "clutch"]', 'common', 22),
        ('Mac Jones', 'QB', 'Patriots', '{"passing": 80, "accuracy": 88}', '["accuracy", "clutch", "versatile"]', 'common', 20),
        ('Tua Tagovailoa', 'QB', 'Dolphins', '{"passing": 78, "accuracy": 85}', '["accuracy", "clutch", "versatile"]', 'common', 18),
        ('Justin Fields', 'QB', 'Bears', '{"passing": 85, "mobility": 90}', '["mobile_qb", "versatile", "clutch"]', 'common', 19),
        ('Trevor Lawrence', 'QB', 'Jaguars', '{"passing": 88, "arm_strength": 82}', '["arm_strength", "versatile", "clutch"]', 'common', 21),
        ('Zach Wilson', 'QB', 'Jets', '{"passing": 85, "mobility": 85}', '["mobile_qb", "versatile", "clutch"]', 'common', 17),
        ('Trey Lance', 'QB', '49ers', '{"passing": 88, "mobility": 90}', '["mobile_qb", "versatile", "clutch"]', 'common', 16),
        ('Kenny Pickett', 'QB', 'Steelers', '{"passing": 80, "accuracy": 82}', '["accuracy", "clutch", "versatile"]', 'common', 15),
        ('Desmond Ridder', 'QB', 'Falcons', '{"passing": 82, "mobility": 80}', '["mobile_qb", "versatile", "clutch"]', 'common', 14),
        ('Malik Willis', 'QB', 'Packers', '{"passing": 85, "mobility": 95}', '["mobile_qb", "versatile", "clutch"]', 'common', 13),
        ('Sam Howell', 'QB', 'Commanders', '{"passing": 85, "mobility": 80}', '["mobile_qb", "versatile", "clutch"]', 'common', 12),
    ]
    
    cursor.executemany('INSERT INTO players (name, position, team, base_stats, synergy_tags, rarity, cost) VALUES (?, ?, ?, ?, ?, ?, ?)', players)
    
    # Sample plays with synergy tags
    plays = [
        ('Hail Mary', 'passing', '{"risk": 90, "reward": 95, "yards": 50}', '["deep_ball", "clutch", "big_play"]', 'epic', 25),
        ('Screen Pass', 'passing', '{"risk": 20, "reward": 60, "yards": 8}', '["quick", "short", "screen_pass"]', 'common', 10),
        ('Draw Play', 'rushing', '{"risk": 30, "reward": 70, "yards": 12}', '["power", "short_yardage", "play_action"]', 'common', 12),
        ('Flea Flicker', 'trick', '{"risk": 80, "reward": 90, "yards": 40}', '["trick_play", "deep_ball", "big_play"]', 'rare', 20),
        ('Wildcat', 'rushing', '{"risk": 60, "reward": 80, "yards": 25}', '["trick_play", "power", "versatile"]', 'rare', 18),
        ('Play Action', 'passing', '{"risk": 40, "reward": 75, "yards": 20}', '["play_action", "deep_ball", "mobility"]', 'common', 15),
        ('Slant Route', 'passing', '{"risk": 20, "reward": 60, "yards": 8}', '["quick", "short", "possession"]', 'common', 8),
        ('Deep Post', 'passing', '{"risk": 75, "reward": 95, "yards": 35}', '["deep_ball", "big_play", "clutch"]', 'rare', 22),
        ('QB Sneak', 'rushing', '{"risk": 10, "reward": 40, "yards": 2}', '["short_yardage", "goal_line", "power"]', 'common', 5),
        ('Statue of Liberty', 'trick', '{"risk": 85, "reward": 98, "yards": 45}', '["trick_play", "big_play", "clutch"]', 'legendary', 30),
        ('Jet Sweep', 'rushing', '{"risk": 35, "reward": 65, "yards": 15}', '["speed", "versatile", "quick"]', 'common', 12),
        ('Corner Route', 'passing', '{"risk": 50, "reward": 80, "yards": 25}', '["deep_ball", "route_running", "red_zone"]', 'rare', 18),
        ('Power Run', 'rushing', '{"risk": 25, "reward": 70, "yards": 10}', '["power", "short_yardage", "goal_line"]', 'common', 10),
        ('Fade Route', 'passing', '{"risk": 60, "reward": 85, "yards": 30}', '["deep_ball", "red_zone", "clutch"]', 'rare', 20),
        ('Counter Run', 'rushing', '{"risk": 40, "reward": 75, "yards": 18}', '["power", "versatile", "play_action"]', 'common', 14),
        ('Out Route', 'passing', '{"risk": 30, "reward": 65, "yards": 12}', '["quick", "possession", "route_running"]', 'common', 9),
        ('Inside Zone', 'rushing', '{"risk": 25, "reward": 70, "yards": 8}', '["power", "short_yardage", "versatile"]', 'common', 8),
        ('Go Route', 'passing', '{"risk": 70, "reward": 90, "yards": 40}', '["deep_ball", "speed", "big_play"]', 'rare', 24),
        ('Toss Sweep', 'rushing', '{"risk": 35, "reward": 70, "yards": 16}', '["speed", "versatile", "quick"]', 'common', 11),
        ('Curl Route', 'passing', '{"risk": 25, "reward": 60, "yards": 10}', '["possession", "route_running", "short"]', 'common', 7),
        ('Dive Play', 'rushing', '{"risk": 20, "reward": 55, "yards": 6}', '["power", "short_yardage", "goal_line"]', 'common', 6),
        ('Wheel Route', 'passing', '{"risk": 45, "reward": 75, "yards": 22}', '["versatile", "receiving_back", "big_play"]', 'rare', 16),
        ('Off Tackle', 'rushing', '{"risk": 30, "reward": 65, "yards": 12}', '["power", "versatile", "play_action"]', 'common', 9),
        ('Seam Route', 'passing', '{"risk": 55, "reward": 80, "yards": 28}', '["deep_ball", "receiving_te", "red_zone"]', 'rare', 19),
        ('Pitch Play', 'rushing', '{"risk": 40, "reward": 70, "yards": 18}', '["speed", "versatile", "quick"]', 'common', 13),
        ('Back Shoulder', 'passing', '{"risk": 65, "reward": 85, "yards": 32}', '["possession", "red_zone", "clutch"]', 'rare', 21),
        ('Read Option', 'rushing', '{"risk": 50, "reward": 80, "yards": 25}', '["mobile_qb", "versatile", "big_play"]', 'rare', 17),
        ('Crossing Route', 'passing', '{"risk": 35, "reward": 70, "yards": 15}', '["possession", "route_running", "versatile"]', 'common', 10),
        ('Stretch Play', 'rushing', '{"risk": 30, "reward": 65, "yards": 14}', '["speed", "versatile", "play_action"]', 'common', 11),
        ('Corner Fade', 'passing', '{"risk": 70, "reward": 90, "yards": 35}', '["deep_ball", "red_zone", "clutch"]', 'rare', 23),
        ('Power O', 'rushing', '{"risk": 25, "reward": 70, "yards": 9}', '["power", "short_yardage", "goal_line"]', 'common', 7),
        ('Sluggo Route', 'passing', '{"risk": 60, "reward": 85, "yards": 30}', '["deep_ball", "route_running", "big_play"]', 'rare', 20),
        ('Trap Play', 'rushing', '{"risk": 35, "reward": 70, "yards": 16}', '["power", "versatile", "play_action"]', 'common', 12),
        ('Double Move', 'passing', '{"risk": 75, "reward": 95, "yards": 42}', '["deep_ball", "route_running", "big_play"]', 'epic', 26),
        ('Lead Draw', 'rushing', '{"risk": 30, "reward": 65, "yards": 13}', '["power", "versatile", "play_action"]', 'common', 10),
        ('Mesh Route', 'passing', '{"risk": 25, "reward": 60, "yards": 9}', '["quick", "possession", "short"]', 'common', 6),
        ('Counter Trey', 'rushing', '{"risk": 40, "reward": 75, "yards": 20}', '["power", "versatile", "play_action"]', 'rare', 15),
        ('Rub Route', 'passing', '{"risk": 30, "reward": 65, "yards": 12}', '["possession", "route_running", "short"]', 'common', 8),
        ('Zone Read', 'rushing', '{"risk": 45, "reward": 75, "yards": 22}', '["mobile_qb", "versatile", "big_play"]', 'rare', 16),
        ('Smoke Route', 'passing', '{"risk": 15, "reward": 50, "yards": 5}', '["quick", "short", "screen_pass"]', 'common', 4),
        ('Pin and Pull', 'rushing', '{"risk": 35, "reward": 70, "yards": 17}', '["power", "versatile", "play_action"]', 'common', 13),
        ('Hitch Route', 'passing', '{"risk": 20, "reward": 55, "yards": 7}', '["quick", "possession", "short"]', 'common', 5),
        ('Wham Play', 'rushing', '{"risk": 30, "reward": 65, "yards": 14}', '["power", "versatile", "play_action"]', 'common', 11),
        ('Bubble Screen', 'passing', '{"risk": 25, "reward": 60, "yards": 8}', '["quick", "screen_pass", "short"]', 'common', 7),
        ('Toss Crack', 'rushing', '{"risk": 35, "reward": 70, "yards": 18}', '["speed", "versatile", "quick"]', 'common', 12),
        ('Quick Slant', 'passing', '{"risk": 20, "reward": 55, "yards": 6}', '["quick", "short", "possession"]', 'common', 5),
        ('Sweep Right', 'rushing', '{"risk": 30, "reward": 65, "yards": 15}', '["speed", "versatile", "quick"]', 'common', 10),
        ('Drag Route', 'passing', '{"risk": 25, "reward": 60, "yards": 10}', '["possession", "route_running", "short"]', 'common', 7),
        ('Offensive Pass Interference', 'penalty', '{"risk": 100, "reward": 0, "yards": -10}', '["penalty", "negative", "mistake"]', 'common', 0),
        ('False Start', 'penalty', '{"risk": 100, "reward": 0, "yards": -5}', '["penalty", "negative", "mistake"]', 'common', 0),
        ('Holding', 'penalty', '{"risk": 100, "reward": 0, "yards": -10}', '["penalty", "negative", "mistake"]', 'common', 0),
        ('Delay of Game', 'penalty', '{"risk": 100, "reward": 0, "yards": -5}', '["penalty", "negative", "mistake"]', 'common', 0),
        ('Intentional Grounding', 'penalty', '{"risk": 100, "reward": 0, "yards": -10}', '["penalty", "negative", "mistake"]', 'common', 0),
    ]
    
    cursor.executemany('INSERT INTO plays (name, play_type, base_stats, synergy_tags, rarity, cost) VALUES (?, ?, ?, ?, ?, ?)', plays)
    
    # Sample modifiers with synergy tags
    modifiers = [
        ('Red Zone Boost', 'scoring', '{"scoring_multiplier": 1.5}', '["red_zone", "scoring", "clutch"]', 'rare', 20),
        ('Weather Advantage', 'environmental', '{"accuracy_boost": 10}', '["environmental", "accuracy", "consistency"]', 'common', 15),
        ('Home Field', 'environmental', '{"all_stats_boost": 5}', '["environmental", "consistency", "momentum"]', 'common', 12),
        ('Clutch Factor', 'mental', '{"pressure_resistance": 15}', '["clutch", "mental", "pressure"]', 'rare', 18),
        ('Momentum', 'temporary', '{"next_play_boost": 20}', '["momentum", "temporary", "big_play"]', 'epic', 25),
        ('Offensive Coordinator', 'coaching', '{"multiplier_boost": 0.5}', '["coaching", "multiplier", "consistency"]', 'rare', 22),
        ('Hot Streak', 'temporary', '{"consecutive_boost": 0.3}', '["temporary", "momentum", "streak"]', 'epic', 28),
        ('Momentum Shift', 'mental', '{"comeback_multiplier": 2.0}', '["mental", "clutch", "comeback"]', 'legendary', 35),
        ('Red Zone Master', 'scoring', '{"red_zone_multiplier": 3.0}', '["red_zone", "scoring", "clutch"]', 'epic', 30),
        ('Playoff Pressure', 'mental', '{"high_risk_multiplier": 1.5}', '["mental", "pressure", "clutch"]', 'legendary', 40),
        ('Speed Boost', 'physical', '{"speed_plays_boost": 15}', '["speed", "physical", "big_play"]', 'common', 12),
        ('Power Surge', 'physical', '{"power_plays_boost": 20}', '["power", "physical", "short_yardage"]', 'common', 14),
        ('Wind Advantage', 'environmental', '{"passing_boost": 12}', '["environmental", "passing", "consistency"]', 'common', 10),
        ('Crowd Noise', 'environmental', '{"opponent_penalty": 8}', '["environmental", "pressure", "home_field"]', 'common', 8),
        ('Cold Weather', 'environmental', '{"running_boost": 15}', '["environmental", "power", "consistency"]', 'common', 9),
        ('Rain Advantage', 'environmental', '{"defensive_boost": 10}', '["environmental", "defense", "consistency"]', 'common', 7),
        ('Snow Game', 'environmental', '{"ground_game_boost": 20}', '["environmental", "power", "versatile"]', 'rare', 16),
        ('Dome Advantage', 'environmental', '{"passing_boost": 8}', '["environmental", "passing", "consistency"]', 'common', 6),
        ('Altitude Training', 'physical', '{"endurance_boost": 12}', '["physical", "endurance", "consistency"]', 'common', 11),
        ('Muscle Memory', 'mental', '{"repetition_boost": 10}', '["mental", "consistency", "practice"]', 'common', 8),
        ('Game Film Study', 'coaching', '{"defensive_read_boost": 15}', '["coaching", "mental", "consistency"]', 'rare', 18),
        ('Halftime Adjustment', 'coaching', '{"second_half_boost": 12}', '["coaching", "mental", "adjustment"]', 'rare', 16),
        ('Clock Management', 'coaching', '{"timeout_efficiency": 20}', '["coaching", "mental", "clutch"]', 'rare', 14),
        ('Playbook Mastery', 'coaching', '{"play_variety_boost": 15}', '["coaching", "versatile", "consistency"]', 'rare', 17),
        ('Team Chemistry', 'mental', '{"teamwork_boost": 10}', '["mental", "teamwork", "consistency"]', 'common', 9),
        ('Leadership', 'mental', '{"team_morale_boost": 12}', '["mental", "leadership", "teamwork"]', 'rare', 15),
        ('Experience', 'mental', '{"pressure_resistance": 8}', '["mental", "pressure", "consistency"]', 'common', 7),
        ('Youth Energy', 'physical', '{"speed_boost": 10}', '["physical", "speed", "energy"]', 'common', 8),
        ('Veteran Savvy', 'mental', '{"decision_making_boost": 12}', '["mental", "decision_making", "consistency"]', 'rare', 13),
        ('Rookie Mistakes', 'mental', '{"mistake_penalty": -8}', '["mental", "mistake", "negative"]', 'common', -5),
        ('Injury Recovery', 'physical', '{"health_boost": 15}', '["physical", "health", "consistency"]', 'rare', 12),
        ('Fresh Legs', 'physical', '{"endurance_boost": 18}', '["physical", "endurance", "energy"]', 'rare', 14),
        ('Fatigue', 'physical', '{"performance_penalty": -10}', '["physical", "fatigue", "negative"]', 'common', -6),
        ('Adrenaline Rush', 'physical', '{"big_play_boost": 20}', '["physical", "big_play", "clutch"]', 'rare', 16),
        ('Nerves', 'mental', '{"pressure_penalty": -12}', '["mental", "pressure", "negative"]', 'common', -7),
        ('Confidence', 'mental', '{"all_stats_boost": 8}', '["mental", "confidence", "consistency"]', 'common', 10),
        ('Desperation', 'mental', '{"clutch_boost": 15}', '["mental", "clutch", "desperation"]', 'rare', 13),
        ('Complacency', 'mental', '{"effort_penalty": -15}', '["mental", "complacency", "negative"]', 'common', -8),
        ('Revenge Game', 'mental', '{"motivation_boost": 18}', '["mental", "motivation", "clutch"]', 'rare', 17),
        ('Contract Year', 'mental', '{"performance_boost": 12}', '["mental", "motivation", "consistency"]', 'rare', 14),
        ('Rookie Wall', 'physical', '{"endurance_penalty": -10}', '["physical", "fatigue", "negative"]', 'common', -6),
        ('Sophomore Slump', 'mental', '{"confidence_penalty": -8}', '["mental", "confidence", "negative"]', 'common', -5),
        ('Breakout Season', 'mental', '{"confidence_boost": 15}', '["mental", "confidence", "breakout"]', 'rare', 16),
        ('Legacy Game', 'mental', '{"clutch_boost": 20}', '["mental", "clutch", "legacy"]', 'epic', 22),
        ('Retirement Tour', 'mental', '{"motivation_boost": 25}', '["mental", "motivation", "legacy"]', 'epic', 25),
        ('Draft Stock', 'mental', '{"performance_boost": 10}', '["mental", "motivation", "draft"]', 'common', 9),
        ('Free Agency', 'mental', '{"contract_boost": 12}', '["mental", "motivation", "contract"]', 'rare', 11),
        ('Trade Deadline', 'mental', '{"uncertainty_penalty": -8}', '["mental", "uncertainty", "negative"]', 'common', -5),
        ('Playoff Push', 'mental', '{"clutch_boost": 18}', '["mental", "clutch", "playoffs"]', 'rare', 19),
        ('Championship Game', 'mental', '{"pressure_boost": 25}', '["mental", "pressure", "championship"]', 'epic', 28),
        ('Super Bowl', 'mental', '{"legacy_boost": 30}', '["mental", "legacy", "super_bowl"]', 'legendary', 35),
        ('Hall of Fame', 'mental', '{"career_boost": 20}', '["mental", "legacy", "career"]', 'epic', 24),
        ('Comeback Player', 'mental', '{"resilience_boost": 15}', '["mental", "resilience", "comeback"]', 'rare', 16),
        ('Rookie of the Year', 'mental', '{"confidence_boost": 12}', '["mental", "confidence", "rookie"]', 'rare', 13),
        ('MVP Race', 'mental', '{"performance_boost": 18}', '["mental", "performance", "mvp"]', 'epic', 20),
        ('Pro Bowl', 'mental', '{"recognition_boost": 10}', '["mental", "recognition", "pro_bowl"]', 'common', 8),
        ('All-Pro', 'mental', '{"excellence_boost": 15}', '["mental", "excellence", "all_pro"]', 'rare', 14),
        ('Franchise Tag', 'mental', '{"security_boost": 8}', '["mental", "security", "contract"]', 'common', 6),
        ('Long-term Deal', 'mental', '{"stability_boost": 10}', '["mental", "stability", "contract"]', 'common', 7),
        ('Holdout', 'mental', '{"distraction_penalty": -12}', '["mental", "distraction", "negative"]', 'common', -7),
        ('Injury Prone', 'physical', '{"durability_penalty": -15}', '["physical", "durability", "negative"]', 'common', -8),
        ('Iron Man', 'physical', '{"durability_boost": 20}', '["physical", "durability", "consistency"]', 'rare', 18),
        ('Speed Demon', 'physical', '{"speed_boost": 15}', '["physical", "speed", "big_play"]', 'rare', 16),
        ('Power House', 'physical', '{"power_boost": 18}', '["physical", "power", "short_yardage"]', 'rare', 17),
        ('Technician', 'mental', '{"technique_boost": 12}', '["mental", "technique", "consistency"]', 'rare', 13),
        ('Natural Talent', 'physical', '{"raw_ability_boost": 14}', '["physical", "talent", "versatile"]', 'rare', 15),
        ('Hard Worker', 'mental', '{"effort_boost": 10}', '["mental", "effort", "consistency"]', 'common', 9),
        ('Game Changer', 'mental', '{"big_play_boost": 20}', '["mental", "big_play", "clutch"]', 'epic', 23),
        ('Clutch Performer', 'mental', '{"clutch_boost": 18}', '["mental", "clutch", "pressure"]', 'epic', 21),
        ('Consistent', 'mental', '{"consistency_boost": 12}', '["mental", "consistency", "reliable"]', 'rare', 14),
        ('Unpredictable', 'mental', '{"surprise_boost": 15}', '["mental", "surprise", "versatile"]', 'rare', 16),
        ('Reliable', 'mental', '{"reliability_boost": 10}', '["mental", "reliability", "consistency"]', 'common', 8),
        ('Volatile', 'mental', '{"volatility_penalty": -8}', '["mental", "volatility", "negative"]', 'common', -5),
        ('Steady Eddie', 'mental', '{"stability_boost": 8}', '["mental", "stability", "consistency"]', 'common', 6),
        ('Wild Card', 'mental', '{"unpredictability_boost": 12}', '["mental", "unpredictability", "versatile"]', 'rare', 11),
        ('Safe Bet', 'mental', '{"safety_boost": 6}', '["mental", "safety", "consistency"]', 'common', 4),
        ('High Risk, High Reward', 'mental', '{"risk_reward_boost": 20}', '["mental", "risk_reward", "big_play"]', 'epic', 24),
        ('Low Risk, Low Reward', 'mental', '{"safety_boost": 8}', '["mental", "safety", "consistency"]', 'common', 5),
        ('Balanced', 'mental', '{"balance_boost": 10}', '["mental", "balance", "versatile"]', 'common', 7),
        ('Specialized', 'mental', '{"specialization_boost": 15}', '["mental", "specialization", "expertise"]', 'rare', 12),
        ('Versatile', 'mental', '{"versatility_boost": 12}', '["mental", "versatility", "flexible"]', 'rare', 10),
        ('One-Trick Pony', 'mental', '{"specialization_boost": 18}', '["mental", "specialization", "limited"]', 'rare', 13),
        ('Jack of All Trades', 'mental', '{"versatility_boost": 8}', '["mental", "versatility", "generalist"]', 'common', 6),
        ('Master of None', 'mental', '{"generalization_penalty": -5}', '["mental", "generalization", "negative"]', 'common', -3),
        ('Expert', 'mental', '{"expertise_boost": 20}', '["mental", "expertise", "mastery"]', 'epic', 22),
        ('Novice', 'mental', '{"inexperience_penalty": -10}', '["mental", "inexperience", "negative"]', 'common', -6),
        ('Veteran', 'mental', '{"experience_boost": 12}', '["mental", "experience", "wisdom"]', 'rare', 11),
        ('Rookie', 'mental', '{"inexperience_penalty": -8}', '["mental", "inexperience", "negative"]', 'common', -5),
        ('Pro', 'mental', '{"professionalism_boost": 10}', '["mental", "professionalism", "consistency"]', 'common', 8),
        ('Amateur', 'mental', '{"amateurism_penalty": -12}', '["mental", "amateurism", "negative"]', 'common', -7),
        ('Elite', 'mental', '{"elite_boost": 25}', '["mental", "elite", "excellence"]', 'legendary', 30),
        ('Average', 'mental', '{"average_boost": 5}', '["mental", "average", "mediocre"]', 'common', 3),
        ('Below Average', 'mental', '{"below_average_penalty": -8}', '["mental", "below_average", "negative"]', 'common', -5),
        ('Above Average', 'mental', '{"above_average_boost": 8}', '["mental", "above_average", "positive"]', 'common', 6),
        ('Exceptional', 'mental', '{"exceptional_boost": 22}', '["mental", "exceptional", "outstanding"]', 'epic', 26),
        ('Outstanding', 'mental', '{"outstanding_boost": 20}', '["mental", "outstanding", "excellent"]', 'epic', 24),
        ('Excellent', 'mental', '{"excellent_boost": 18}', '["mental", "excellent", "great"]', 'rare', 20),
        ('Great', 'mental', '{"great_boost": 15}', '["mental", "great", "good"]', 'rare', 17),
        ('Good', 'mental', '{"good_boost": 12}', '["mental", "good", "positive"]', 'rare', 14),
        ('Decent', 'mental', '{"decent_boost": 8}', '["mental", "decent", "adequate"]', 'common', 9),
        ('Poor', 'mental', '{"poor_penalty": -10}', '["mental", "poor", "negative"]', 'common', -6),
        ('Terrible', 'mental', '{"terrible_penalty": -15}', '["mental", "terrible", "negative"]', 'common', -8),
        ('Awful', 'mental', '{"awful_penalty": -20}', '["mental", "awful", "negative"]', 'common', -10),
        ('Perfect', 'mental', '{"perfect_boost": 30}', '["mental", "perfect", "flawless"]', 'legendary', 35),
        ('Flawless', 'mental', '{"flawless_boost": 28}', '["mental", "flawless", "perfect"]', 'legendary', 32),
        ('Flawed', 'mental', '{"flawed_penalty": -5}', '["mental", "flawed", "negative"]', 'common', -3),
        ('Imperfect', 'mental', '{"imperfect_penalty": -3}', '["mental", "imperfect", "negative"]', 'common', -2),
        ('Incomplete', 'mental', '{"incomplete_penalty": -8}', '["mental", "incomplete", "negative"]', 'common', -5),
        ('Complete', 'mental', '{"complete_boost": 15}', '["mental", "complete", "whole"]', 'rare', 16),
        ('Partial', 'mental', '{"partial_penalty": -6}', '["mental", "partial", "negative"]', 'common', -4),
        ('Full', 'mental', '{"full_boost": 12}', '["mental", "full", "complete"]', 'rare', 13),
        ('Empty', 'mental', '{"empty_penalty": -12}', '["mental", "empty", "negative"]', 'common', -7),
        ('Full Tank', 'physical', '{"energy_boost": 20}', '["physical", "energy", "full"]', 'rare', 18),
        ('Running on Empty', 'physical', '{"energy_penalty": -15}', '["physical", "energy", "negative"]', 'common', -8),
        ('Fresh', 'physical', '{"freshness_boost": 15}', '["physical", "freshness", "energy"]', 'rare', 14),
        ('Tired', 'physical', '{"fatigue_penalty": -10}', '["physical", "fatigue", "negative"]', 'common', -6),
        ('Exhausted', 'physical', '{"exhaustion_penalty": -18}', '["physical", "exhaustion", "negative"]', 'common', -9),
        ('Energized', 'physical', '{"energy_boost": 18}', '["physical", "energy", "positive"]', 'rare', 16),
        ('Drained', 'physical', '{"drain_penalty": -12}', '["physical", "drain", "negative"]', 'common', -7),
        ('Recharged', 'physical', '{"recharge_boost": 16}', '["physical", "recharge", "positive"]', 'rare', 15),
        ('Depleted', 'physical', '{"depletion_penalty": -14}', '["physical", "depletion", "negative"]', 'common', -8),
        ('Restored', 'physical', '{"restoration_boost": 14}', '["physical", "restoration", "positive"]', 'rare', 13),
        ('Damaged', 'physical', '{"damage_penalty": -16}', '["physical", "damage", "negative"]', 'common', -9),
        ('Repaired', 'physical', '{"repair_boost": 12}', '["physical", "repair", "positive"]', 'rare', 11),
        ('Broken', 'physical', '{"broken_penalty": -20}', '["physical", "broken", "negative"]', 'common', -10),
        ('Fixed', 'physical', '{"fixed_boost": 10}', '["physical", "fixed", "positive"]', 'rare', 9),
        ('Healthy', 'physical', '{"health_boost": 15}', '["physical", "health", "positive"]', 'rare', 14),
        ('Injured', 'physical', '{"injury_penalty": -18}', '["physical", "injury", "negative"]', 'common', -9),
        ('Recovered', 'physical', '{"recovery_boost": 13}', '["physical", "recovery", "positive"]', 'rare', 12),
        ('Sick', 'physical', '{"sickness_penalty": -14}', '["physical", "sickness", "negative"]', 'common', -8),
        ('Cured', 'physical', '{"cure_boost": 11}', '["physical", "cure", "positive"]', 'rare', 10),
        ('Strong', 'physical', '{"strength_boost": 16}', '["physical", "strength", "power"]', 'rare', 15),
        ('Weak', 'physical', '{"weakness_penalty": -12}', '["physical", "weakness", "negative"]', 'common', -7),
        ('Powerful', 'physical', '{"power_boost": 18}', '["physical", "power", "strength"]', 'rare', 17),
        ('Powerless', 'physical', '{"powerlessness_penalty": -15}', '["physical", "powerlessness", "negative"]', 'common', -8),
        ('Mighty', 'physical', '{"might_boost": 20}', '["physical", "might", "power"]', 'epic', 19),
        ('Feeble', 'physical', '{"feebleness_penalty": -10}', '["physical", "feebleness", "negative"]', 'common', -6),
        ('Robust', 'physical', '{"robustness_boost": 14}', '["physical", "robustness", "strength"]', 'rare', 13),
        ('Fragile', 'physical', '{"fragility_penalty": -16}', '["physical", "fragility", "negative"]', 'common', -9),
        ('Sturdy', 'physical', '{"sturdiness_boost": 12}', '["physical", "sturdiness", "strength"]', 'rare', 11),
        ('Delicate', 'physical', '{"delicacy_penalty": -14}', '["physical", "delicacy", "negative"]', 'common', -8),
        ('Tough', 'physical', '{"toughness_boost": 15}', '["physical", "toughness", "strength"]', 'rare', 14),
        ('Tender', 'physical', '{"tenderness_penalty": -8}', '["physical", "tenderness", "negative"]', 'common', -5),
        ('Hard', 'physical', '{"hardness_boost": 13}', '["physical", "hardness", "strength"]', 'rare', 12),
        ('Soft', 'physical', '{"softness_penalty": -11}', '["physical", "softness", "negative"]', 'common', -6),
        ('Solid', 'physical', '{"solidity_boost": 11}', '["physical", "solidity", "strength"]', 'rare', 10),
        ('Liquid', 'physical', '{"liquidity_penalty": -9}', '["physical", "liquidity", "negative"]', 'common', -5),
        ('Gas', 'physical', '{"gaseous_penalty": -7}', '["physical", "gaseous", "negative"]', 'common', -4),
        ('Plasma', 'physical', '{"plasma_penalty": -5}', '["physical", "plasma", "negative"]', 'common', -3),
        ('Crystal', 'physical', '{"crystal_boost": 9}', '["physical", "crystal", "strength"]', 'common', 8),
        ('Metal', 'physical', '{"metal_boost": 12}', '["physical", "metal", "strength"]', 'rare', 11),
        ('Wood', 'physical', '{"wood_boost": 6}', '["physical", "wood", "strength"]', 'common', 5),
        ('Stone', 'physical', '{"stone_boost": 10}', '["physical", "stone", "strength"]', 'rare', 9),
        ('Diamond', 'physical', '{"diamond_boost": 25}', '["physical", "diamond", "strength"]', 'legendary', 30),
        ('Gold', 'physical', '{"gold_boost": 20}', '["physical", "gold", "strength"]', 'epic', 24),
        ('Silver', 'physical', '{"silver_boost": 15}', '["physical", "silver", "strength"]', 'rare', 17),
        ('Bronze', 'physical', '{"bronze_boost": 10}', '["physical", "bronze", "strength"]', 'rare', 12),
        ('Iron', 'physical', '{"iron_boost": 13}', '["physical", "iron", "strength"]', 'rare', 14),
        ('Steel', 'physical', '{"steel_boost": 16}', '["physical", "steel", "strength"]', 'rare', 18),
        ('Aluminum', 'physical', '{"aluminum_boost": 8}', '["physical", "aluminum", "strength"]', 'common', 7),
        ('Copper', 'physical', '{"copper_boost": 7}', '["physical", "copper", "strength"]', 'common', 6),
        ('Lead', 'physical', '{"lead_penalty": -5}', '["physical", "lead", "negative"]', 'common', -3),
        ('Mercury', 'physical', '{"mercury_penalty": -8}', '["physical", "mercury", "negative"]', 'common', -5),
        ('Uranium', 'physical', '{"uranium_penalty": -20}', '["physical", "uranium", "negative"]', 'common', -10),
        ('Plutonium', 'physical', '{"plutonium_penalty": -25}', '["physical", "plutonium", "negative"]', 'common', -12),
        ('Radium', 'physical', '{"radium_penalty": -18}', '["physical", "radium", "negative"]', 'common', -9),
        ('Polonium', 'physical', '{"polonium_penalty": -22}', '["physical", "polonium", "negative"]', 'common', -11),
        ('Francium', 'physical', '{"francium_penalty": -15}', '["physical", "francium", "negative"]', 'common', -8),
        ('Cesium', 'physical', '{"cesium_penalty": -12}', '["physical", "cesium", "negative"]', 'common', -7),
        ('Rubidium', 'physical', '{"rubidium_penalty": -10}', '["physical", "rubidium", "negative"]', 'common', -6),
        ('Potassium', 'physical', '{"potassium_boost": 5}', '["physical", "potassium", "strength"]', 'common', 4),
        ('Sodium', 'physical', '{"sodium_boost": 4}', '["physical", "sodium", "strength"]', 'common', 3),
        ('Lithium', 'physical', '{"lithium_boost": 3}', '["physical", "lithium", "strength"]', 'common', 2),
        ('Hydrogen', 'physical', '{"hydrogen_boost": 2}', '["physical", "hydrogen", "strength"]', 'common', 1),
        ('Helium', 'physical', '{"helium_boost": 1}', '["physical", "helium", "strength"]', 'common', 1),
        ('Neon', 'physical', '{"neon_boost": 1}', '["physical", "neon", "strength"]', 'common', 1),
        ('Argon', 'physical', '{"argon_boost": 1}', '["physical", "argon", "strength"]', 'common', 1),
        ('Krypton', 'physical', '{"krypton_boost": 1}', '["physical", "krypton", "strength"]', 'common', 1),
        ('Xenon', 'physical', '{"xenon_boost": 1}', '["physical", "xenon", "strength"]', 'common', 1),
        ('Radon', 'physical', '{"radon_penalty": -5}', '["physical", "radon", "negative"]', 'common', -3),
        ('Oganesson', 'physical', '{"oganesson_penalty": -3}', '["physical", "oganesson", "negative"]', 'common', -2),
        ('Tennessine', 'physical', '{"tennessine_penalty": -3}', '["physical", "tennessine", "negative"]', 'common', -2),
        ('Moscovium', 'physical', '{"moscovium_penalty": -3}', '["physical", "moscovium", "negative"]', 'common', -2),
        ('Nihonium', 'physical', '{"nihonium_penalty": -3}', '["physical", "nihonium", "negative"]', 'common', -2),
        ('Flerovium', 'physical', '{"flerovium_penalty": -3}', '["physical", "flerovium", "negative"]', 'common', -2),
        ('Livermorium', 'physical', '{"livermorium_penalty": -3}', '["physical", "livermorium", "negative"]', 'common', -2),
        ('Copernicium', 'physical', '{"copernicium_penalty": -3}', '["physical", "copernicium", "negative"]', 'common', -2),
        ('Roentgenium', 'physical', '{"roentgenium_penalty": -3}', '["physical", "roentgenium", "negative"]', 'common', -2),
        ('Darmstadtium', 'physical', '{"darmstadtium_penalty": -3}', '["physical", "darmstadtium", "negative"]', 'common', -2),
        ('Meitnerium', 'physical', '{"meitnerium_penalty": -3}', '["physical", "meitnerium", "negative"]', 'common', -2),
        ('Hassium', 'physical', '{"hassium_penalty": -3}', '["physical", "hassium", "negative"]', 'common', -2),
        ('Bohrium', 'physical', '{"bohrium_penalty": -3}', '["physical", "bohrium", "negative"]', 'common', -2),
        ('Seaborgium', 'physical', '{"seaborgium_penalty": -3}', '["physical", "seaborgium", "negative"]', 'common', -2),
        ('Dubnium', 'physical', '{"dubnium_penalty": -3}', '["physical", "dubnium", "negative"]', 'common', -2),
        ('Rutherfordium', 'physical', '{"rutherfordium_penalty": -3}', '["physical", "rutherfordium", "negative"]', 'common', -2),
        ('Lawrencium', 'physical', '{"lawrencium_penalty": -3}', '["physical", "lawrencium", "negative"]', 'common', -2),
        ('Nobelium', 'physical', '{"nobelium_penalty": -3}', '["physical", "nobelium", "negative"]', 'common', -2),
        ('Mendelevium', 'physical', '{"mendelevium_penalty": -3}', '["physical", "mendelevium", "negative"]', 'common', -2),
        ('Fermium', 'physical', '{"fermium_penalty": -3}', '["physical", "fermium", "negative"]', 'common', -2),
        ('Einsteinium', 'physical', '{"einsteinium_penalty": -3}', '["physical", "einsteinium", "negative"]', 'common', -2),
        ('Californium', 'physical', '{"californium_penalty": -3}', '["physical", "californium", "negative"]', 'common', -2),
        ('Berkelium', 'physical', '{"berkelium_penalty": -3}', '["physical", "berkelium", "negative"]', 'common', -2),
        ('Curium', 'physical', '{"curium_penalty": -3}', '["physical", "curium", "negative"]', 'common', -2),
        ('Americium', 'physical', '{"americium_penalty": -3}', '["physical", "americium", "negative"]', 'common', -2),
        ('Plutonium', 'physical', '{"plutonium_penalty": -25}', '["physical", "plutonium", "negative"]', 'common', -12),
        ('Neptunium', 'physical', '{"neptunium_penalty": -3}', '["physical", "neptunium", "negative"]', 'common', -2),
        ('Uranium', 'physical', '{"uranium_penalty": -20}', '["physical", "uranium", "negative"]', 'common', -10),
        ('Protactinium', 'physical', '{"protactinium_penalty": -3}', '["physical", "protactinium", "negative"]', 'common', -2),
        ('Thorium', 'physical', '{"thorium_penalty": -3}', '["physical", "thorium", "negative"]', 'common', -2),
        ('Actinium', 'physical', '{"actinium_penalty": -3}', '["physical", "actinium", "negative"]', 'common', -2),
        ('Radium', 'physical', '{"radium_penalty": -18}', '["physical", "radium", "negative"]', 'common', -9),
        ('Francium', 'physical', '{"francium_penalty": -15}', '["physical", "francium", "negative"]', 'common', -8),
        ('Radon', 'physical', '{"radon_penalty": -5}', '["physical", "radon", "negative"]', 'common', -3),
        ('Astatine', 'physical', '{"astatine_penalty": -3}', '["physical", "astatine", "negative"]', 'common', -2),
        ('Polonium', 'physical', '{"polonium_penalty": -22}', '["physical", "polonium", "negative"]', 'common', -11),
        ('Bismuth', 'physical', '{"bismuth_boost": 1}', '["physical", "bismuth", "strength"]', 'common', 1),
        ('Lead', 'physical', '{"lead_penalty": -5}', '["physical", "lead", "negative"]', 'common', -3),
        ('Thallium', 'physical', '{"thallium_penalty": -3}', '["physical", "thallium", "negative"]', 'common', -2),
        ('Mercury', 'physical', '{"mercury_penalty": -8}', '["physical", "mercury", "negative"]', 'common', -5),
        ('Gold', 'physical', '{"gold_boost": 20}', '["physical", "gold", "strength"]', 'epic', 24),
        ('Platinum', 'physical', '{"platinum_boost": 22}', '["physical", "platinum", "strength"]', 'epic', 26),
        ('Iridium', 'physical', '{"iridium_boost": 18}', '["physical", "iridium", "strength"]', 'rare', 20),
        ('Osmium', 'physical', '{"osmium_boost": 16}', '["physical", "osmium", "strength"]', 'rare', 18),
        ('Rhenium', 'physical', '{"rhenium_boost": 14}', '["physical", "rhenium", "strength"]', 'rare', 16),
        ('Tungsten', 'physical', '{"tungsten_boost": 17}', '["physical", "tungsten", "strength"]', 'rare', 19),
        ('Tantalum', 'physical', '{"tantalum_boost": 13}', '["physical", "tantalum", "strength"]', 'rare', 15),
        ('Hafnium', 'physical', '{"hafnium_boost": 11}', '["physical", "hafnium", "strength"]', 'rare', 13),
        ('Lutetium', 'physical', '{"lutetium_boost": 9}', '["physical", "lutetium", "strength"]', 'rare', 11),
        ('Ytterbium', 'physical', '{"ytterbium_boost": 7}', '["physical", "ytterbium", "strength"]', 'common', 8),
        ('Thulium', 'physical', '{"thulium_boost": 5}', '["physical", "thulium", "strength"]', 'common', 6),
        ('Erbium', 'physical', '{"erbium_boost": 3}', '["physical", "erbium", "strength"]', 'common', 4),
        ('Holmium', 'physical', '{"holmium_boost": 1}', '["physical", "holmium", "strength"]', 'common', 2),
        ('Dysprosium', 'physical', '{"dysprosium_boost": 1}', '["physical", "dysprosium", "strength"]', 'common', 1),
        ('Terbium', 'physical', '{"terbium_boost": 1}', '["physical", "terbium", "strength"]', 'common', 1),
        ('Gadolinium', 'physical', '{"gadolinium_boost": 1}', '["physical", "gadolinium", "strength"]', 'common', 1),
        ('Europium', 'physical', '{"europium_boost": 1}', '["physical", "europium", "strength"]', 'common', 1),
        ('Samarium', 'physical', '{"samarium_boost": 1}', '["physical", "samarium", "strength"]', 'common', 1),
        ('Promethium', 'physical', '{"promethium_penalty": -3}', '["physical", "promethium", "negative"]', 'common', -2),
        ('Neodymium', 'physical', '{"neodymium_boost": 1}', '["physical", "neodymium", "strength"]', 'common', 1),
        ('Praseodymium', 'physical', '{"praseodymium_boost": 1}', '["physical", "praseodymium", "strength"]', 'common', 1),
        ('Cerium', 'physical', '{"cerium_boost": 1}', '["physical", "cerium", "strength"]', 'common', 1),
        ('Lanthanum', 'physical', '{"lanthanum_boost": 1}', '["physical", "lanthanum", "strength"]', 'common', 1),
        ('Barium', 'physical', '{"barium_boost": 1}', '["physical", "barium", "strength"]', 'common', 1),
        ('Cesium', 'physical', '{"cesium_penalty": -12}', '["physical", "cesium", "negative"]', 'common', -7),
        ('Xenon', 'physical', '{"xenon_boost": 1}', '["physical", "xenon", "strength"]', 'common', 1),
        ('Iodine', 'physical', '{"iodine_boost": 1}', '["physical", "iodine", "strength"]', 'common', 1),
        ('Tellurium', 'physical', '{"tellurium_boost": 1}', '["physical", "tellurium", "strength"]', 'common', 1),
        ('Antimony', 'physical', '{"antimony_boost": 1}', '["physical", "antimony", "strength"]', 'common', 1),
        ('Tin', 'physical', '{"tin_boost": 1}', '["physical", "tin", "strength"]', 'common', 1),
        ('Indium', 'physical', '{"indium_boost": 1}', '["physical", "indium", "strength"]', 'common', 1),
        ('Cadmium', 'physical', '{"cadmium_penalty": -3}', '["physical", "cadmium", "negative"]', 'common', -2),
        ('Silver', 'physical', '{"silver_boost": 15}', '["physical", "silver", "strength"]', 'rare', 17),
        ('Palladium', 'physical', '{"palladium_boost": 19}', '["physical", "palladium", "strength"]', 'epic', 21),
        ('Rhodium', 'physical', '{"rhodium_boost": 21}', '["physical", "rhodium", "strength"]', 'epic', 23),
        ('Ruthenium', 'physical', '{"ruthenium_boost": 15}', '["physical", "ruthenium", "strength"]', 'rare', 17),
        ('Technetium', 'physical', '{"technetium_penalty": -3}', '["physical", "technetium", "negative"]', 'common', -2),
        ('Molybdenum', 'physical', '{"molybdenum_boost": 13}', '["physical", "molybdenum", "strength"]', 'rare', 15),
        ('Niobium', 'physical', '{"niobium_boost": 11}', '["physical", "niobium", "strength"]', 'rare', 13),
        ('Zirconium', 'physical', '{"zirconium_boost": 9}', '["physical", "zirconium", "strength"]', 'rare', 11),
        ('Yttrium', 'physical', '{"yttrium_boost": 7}', '["physical", "yttrium", "strength"]', 'common', 8),
        ('Strontium', 'physical', '{"strontium_boost": 5}', '["physical", "strontium", "strength"]', 'common', 6),
        ('Rubidium', 'physical', '{"rubidium_penalty": -10}', '["physical", "rubidium", "negative"]', 'common', -6),
        ('Krypton', 'physical', '{"krypton_boost": 1}', '["physical", "krypton", "strength"]', 'common', 1),
        ('Bromine', 'physical', '{"bromine_penalty": -3}', '["physical", "bromine", "negative"]', 'common', -2),
        ('Selenium', 'physical', '{"selenium_boost": 1}', '["physical", "selenium", "strength"]', 'common', 1),
        ('Arsenic', 'physical', '{"arsenic_penalty": -5}', '["physical", "arsenic", "negative"]', 'common', -3),
        ('Germanium', 'physical', '{"germanium_boost": 1}', '["physical", "germanium", "strength"]', 'common', 1),
        ('Gallium', 'physical', '{"gallium_boost": 1}', '["physical", "gallium", "strength"]', 'common', 1),
        ('Zinc', 'physical', '{"zinc_boost": 1}', '["physical", "zinc", "strength"]', 'common', 1),
        ('Copper', 'physical', '{"copper_boost": 7}', '["physical", "copper", "strength"]', 'common', 6),
        ('Nickel', 'physical', '{"nickel_boost": 1}', '["physical", "nickel", "strength"]', 'common', 1),
        ('Cobalt', 'physical', '{"cobalt_boost": 1}', '["physical", "cobalt", "strength"]', 'common', 1),
        ('Iron', 'physical', '{"iron_boost": 13}', '["physical", "iron", "strength"]', 'rare', 14),
        ('Manganese', 'physical', '{"manganese_boost": 1}', '["physical", "manganese", "strength"]', 'common', 1),
        ('Chromium', 'physical', '{"chromium_boost": 1}', '["physical", "chromium", "strength"]', 'common', 1),
        ('Vanadium', 'physical', '{"vanadium_boost": 1}', '["physical", "vanadium", "strength"]', 'common', 1),
        ('Titanium', 'physical', '{"titanium_boost": 14}', '["physical", "titanium", "strength"]', 'rare', 16),
        ('Scandium', 'physical', '{"scandium_boost": 1}', '["physical", "scandium", "strength"]', 'common', 1),
        ('Calcium', 'physical', '{"calcium_boost": 1}', '["physical", "calcium", "strength"]', 'common', 1),
        ('Potassium', 'physical', '{"potassium_boost": 5}', '["physical", "potassium", "strength"]', 'common', 4),
        ('Argon', 'physical', '{"argon_boost": 1}', '["physical", "argon", "strength"]', 'common', 1),
        ('Chlorine', 'physical', '{"chlorine_penalty": -3}', '["physical", "chlorine", "negative"]', 'common', -2),
        ('Sulfur', 'physical', '{"sulfur_boost": 1}', '["physical", "sulfur", "strength"]', 'common', 1),
        ('Phosphorus', 'physical', '{"phosphorus_boost": 1}', '["physical", "phosphorus", "strength"]', 'common', 1),
        ('Silicon', 'physical', '{"silicon_boost": 1}', '["physical", "silicon", "strength"]', 'common', 1),
        ('Aluminum', 'physical', '{"aluminum_boost": 8}', '["physical", "aluminum", "strength"]', 'common', 7),
        ('Magnesium', 'physical', '{"magnesium_boost": 1}', '["physical", "magnesium", "strength"]', 'common', 1),
        ('Sodium', 'physical', '{"sodium_boost": 4}', '["physical", "sodium", "strength"]', 'common', 3),
        ('Neon', 'physical', '{"neon_boost": 1}', '["physical", "neon", "strength"]', 'common', 1),
        ('Fluorine', 'physical', '{"fluorine_penalty": -3}', '["physical", "fluorine", "negative"]', 'common', -2),
        ('Oxygen', 'physical', '{"oxygen_boost": 1}', '["physical", "oxygen", "strength"]', 'common', 1),
        ('Nitrogen', 'physical', '{"nitrogen_boost": 1}', '["physical", "nitrogen", "strength"]', 'common', 1),
        ('Carbon', 'physical', '{"carbon_boost": 1}', '["physical", "carbon", "strength"]', 'common', 1),
        ('Boron', 'physical', '{"boron_boost": 1}', '["physical", "boron", "strength"]', 'common', 1),
        ('Beryllium', 'physical', '{"beryllium_boost": 1}', '["physical", "beryllium", "strength"]', 'common', 1),
        ('Lithium', 'physical', '{"lithium_boost": 3}', '["physical", "lithium", "strength"]', 'common', 2),
        ('Helium', 'physical', '{"helium_boost": 1}', '["physical", "helium", "strength"]', 'common', 1),
        ('Hydrogen', 'physical', '{"hydrogen_boost": 2}', '["physical", "hydrogen", "strength"]', 'common', 1),
    ]
    
    cursor.executemany('INSERT INTO modifiers (name, modifier_type, effect, synergy_tags, rarity, cost) VALUES (?, ?, ?, ?, ?, ?)', modifiers)
    
    conn.commit()
    conn.close()

def create_full_deck(initial_deck):
    """Create a 30-card deck from initial deck configuration"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    full_deck = []
    
    # Add players (multiple copies to reach 30 cards)
    for player_id in initial_deck['players']:
        cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
        player_data = cursor.fetchone()
        if player_data:
            # Add 3 copies of each player
            for _ in range(3):
                full_deck.append({
                    'id': player_data[0],
                    'type': 'player',
                    'data': {
                        'id': player_data[0],
                        'name': player_data[1],
                        'position': player_data[2],
                        'team': player_data[3],
                        'base_stats': json.loads(player_data[4]),
                        'synergy_tags': json.loads(player_data[5]),
                        'rarity': player_data[6],
                        'cost': player_data[7]
                    },
                    'synergy_tags': json.loads(player_data[5])
                })
    
    # Add plays (multiple copies)
    for play_id in initial_deck['plays']:
        cursor.execute('SELECT * FROM plays WHERE id = ?', (play_id,))
        play_data = cursor.fetchone()
        if play_data:
            # Add 4 copies of each play
            for _ in range(4):
                full_deck.append({
                    'id': play_data[0],
                    'type': 'play',
                    'data': {
                        'id': play_data[0],
                        'name': play_data[1],
                        'play_type': play_data[2],
                        'base_stats': json.loads(play_data[3]),
                        'synergy_tags': json.loads(play_data[4]),
                        'rarity': play_data[5],
                        'cost': play_data[6]
                    },
                    'synergy_tags': json.loads(play_data[4])
                })
    
    # Add modifiers (fewer copies)
    for modifier_id in initial_deck['modifiers']:
        cursor.execute('SELECT * FROM modifiers WHERE id = ?', (modifier_id,))
        modifier_data = cursor.fetchone()
        if modifier_data:
            # Add 2 copies of each modifier
            for _ in range(2):
                full_deck.append({
                    'id': modifier_data[0],
                    'type': 'modifier',
                    'data': {
                        'id': modifier_data[0],
                        'name': modifier_data[1],
                        'modifier_type': modifier_data[2],
                        'effect': json.loads(modifier_data[3]),
                        'synergy_tags': json.loads(modifier_data[4]),
                        'rarity': modifier_data[5],
                        'cost': modifier_data[6]
                    },
                    'synergy_tags': json.loads(modifier_data[4])
                })
    
    conn.close()
    
    # Shuffle the deck
    random.shuffle(full_deck)
    return full_deck

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game session"""
    data = request.get_json()
    player_name = data.get('player_name', 'Player')
    deck_type = data.get('deck_type', 'balanced_offense')
    
    # Get deck based on selected type
    initial_deck = get_deck_by_type(deck_type)
    
    # Create full deck (30 cards) from initial deck
    full_deck = create_full_deck(initial_deck)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_sessions (player_name, deck, deck_type, deck_cards)
        VALUES (?, ?, ?, ?)
    ''', (player_name, json.dumps(initial_deck), deck_type, json.dumps(full_deck)))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'session_id': session_id,
        'deck': initial_deck,
        'deck_cards': full_deck,
        'hand': [],
        'field': [],
        'bench': [],
        'discard_pile': [],
        'coaching_points': 0,
        'downs': 1,
        'distance': 0,
        'yards_to_go': 10,
        'pressure_level': 0,
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
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session state for defensive calculations
    cursor.execute('SELECT current_season, current_game FROM game_sessions WHERE id = ?', (session_id,))
    session_data = cursor.fetchone()
    game_state = {'season': session_data[0], 'game': session_data[1]} if session_data else None
    
    # Calculate drive score and results
    drive_result = calculate_drive_score(cards_played, game_state)
    
    # Get current session state
    cursor.execute('SELECT current_game, current_drive, game_progress, season_progress, downs, distance, yards_to_go FROM game_sessions WHERE id = ?', (session_id,))
    session_data = cursor.fetchone()
    
    if not session_data:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    current_game, current_drive, game_progress_json, season_progress_json, current_down, current_distance, yards_to_go = session_data
    game_progress = json.loads(game_progress_json)
    season_progress = json.loads(season_progress_json)
    
    # Update downs and distance based on drive result
    new_down = current_down + drive_result['downs_used']
    new_distance = current_distance + drive_result['yards_gained']
    
    # Check if we got a first down
    if drive_result['first_down'] or new_distance >= yards_to_go:
        # First down! Reset to 1st & 10
        new_down = 1
        new_distance = 0
        yards_to_go = 10
    elif new_down > 4:
        # Turnover on downs
        new_down = 1
        new_distance = 0
        yards_to_go = 10
        drive_result['drive_successful'] = False
        drive_result['turnover'] = True
    
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
            downs = ?,
            distance = ?,
            yards_to_go = ?,
            game_progress = ?,
            season_progress = ?
        WHERE id = ?
    ''', (drive_result['drive_score'], next_game, next_drive, new_down, new_distance, yards_to_go,
          json.dumps(game_progress), json.dumps(season_progress), session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'drive_result': drive_result,
        'game_progress': game_progress,
        'season_progress': season_progress,
        'next_game': next_game,
        'next_drive': next_drive,
        'downs': new_down,
        'distance': new_distance,
        'yards_to_go': yards_to_go
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
            'synergy_tags': json.loads(row[5]),
            'rarity': row[6],
            'cost': row[7]
        })
    conn.close()
    return jsonify(players)

@app.route('/api/game/<int:session_id>/draw-cards', methods=['POST'])
def draw_cards(session_id):
    """Draw N cards from deck to hand"""
    data = request.get_json()
    num_cards = data.get('num_cards', 5)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session state
    cursor.execute('SELECT deck_cards, hand FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    deck_cards = json.loads(result[0])
    hand = json.loads(result[1])
    
    # Draw cards (up to hand limit of 8)
    cards_to_draw = min(num_cards, 8 - len(hand), len(deck_cards))
    drawn_cards = deck_cards[:cards_to_draw]
    remaining_deck = deck_cards[cards_to_draw:]
    new_hand = hand + drawn_cards
    
    # Update session
    cursor.execute('''
        UPDATE game_sessions 
        SET deck_cards = ?, hand = ?
        WHERE id = ?
    ''', (json.dumps(remaining_deck), json.dumps(new_hand), session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'drawn_cards': drawn_cards,
        'hand': new_hand,
        'deck_remaining': len(remaining_deck)
    })

@app.route('/api/game/<int:session_id>/mulligan', methods=['POST'])
def mulligan(session_id):
    """Redraw hand at drive start"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session state
    cursor.execute('SELECT deck_cards, hand, discard_pile FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    deck_cards = json.loads(result[0])
    hand = json.loads(result[1])
    discard_pile = json.loads(result[2])
    
    # Put current hand into discard pile
    discard_pile.extend(hand)
    
    # Draw 5 new cards
    cards_to_draw = min(5, len(deck_cards))
    new_hand = deck_cards[:cards_to_draw]
    remaining_deck = deck_cards[cards_to_draw:]
    
    # Update session
    cursor.execute('''
        UPDATE game_sessions 
        SET deck_cards = ?, hand = ?, discard_pile = ?
        WHERE id = ?
    ''', (json.dumps(remaining_deck), json.dumps(new_hand), json.dumps(discard_pile), session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'hand': new_hand,
        'deck_remaining': len(remaining_deck)
    })

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
            'synergy_tags': json.loads(row[4]),
            'rarity': row[5],
            'cost': row[6]
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
            'synergy_tags': json.loads(row[4]),
            'rarity': row[5],
            'cost': row[6]
        })
    conn.close()
    return jsonify(modifiers)

@app.route('/api/game/<int:session_id>/shop', methods=['GET'])
def get_shop(session_id):
    """Get current shop inventory"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session
    cursor.execute('SELECT coaching_points FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    coaching_points = result[0]
    
    # Generate 6 random cards for shop
    shop_cards = []
    
    # Get all available cards
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()
    cursor.execute('SELECT * FROM plays')
    plays = cursor.fetchall()
    cursor.execute('SELECT * FROM modifiers')
    modifiers = cursor.fetchall()
    
    all_cards = []
    
    # Add players
    for player in players:
        all_cards.append({
            'id': player[0],
            'type': 'player',
            'data': {
                'id': player[0],
                'name': player[1],
                'position': player[2],
                'team': player[3],
                'base_stats': json.loads(player[4]),
                'synergy_tags': json.loads(player[5]),
                'rarity': player[6],
                'cost': player[7]
            },
            'synergy_tags': json.loads(player[5])
        })
    
    # Add plays
    for play in plays:
        all_cards.append({
            'id': play[0],
            'type': 'play',
            'data': {
                'id': play[0],
                'name': play[1],
                'play_type': play[2],
                'base_stats': json.loads(play[3]),
                'synergy_tags': json.loads(play[4]),
                'rarity': play[5],
                'cost': play[6]
            },
            'synergy_tags': json.loads(play[4])
        })
    
    # Add modifiers
    for modifier in modifiers:
        all_cards.append({
            'id': modifier[0],
            'type': 'modifier',
            'data': {
                'id': modifier[0],
                'name': modifier[1],
                'modifier_type': modifier[2],
                'effect': json.loads(modifier[3]),
                'synergy_tags': json.loads(modifier[4]),
                'rarity': modifier[5],
                'cost': modifier[6]
            },
            'synergy_tags': json.loads(modifier[4])
        })
    
    # Select 6 random cards for shop
    shop_cards = random.sample(all_cards, min(6, len(all_cards)))
    
    conn.close()
    
    return jsonify({
        'shop_cards': shop_cards,
        'coaching_points': coaching_points
    })

@app.route('/api/game/<int:session_id>/buy-card', methods=['POST'])
def buy_card(session_id):
    """Purchase a card from the shop"""
    data = request.get_json()
    card_to_buy = data.get('card')
    
    if not card_to_buy:
        return jsonify({'error': 'No card specified'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session
    cursor.execute('SELECT coaching_points, deck_cards FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    coaching_points, deck_cards_json = result
    deck_cards = json.loads(deck_cards_json)
    
    # Check if player has enough points
    card_cost = card_to_buy['data']['cost']
    if coaching_points < card_cost:
        conn.close()
        return jsonify({'error': 'Not enough coaching points'}), 400
    
    # Add card to deck
    deck_cards.append(card_to_buy)
    
    # Update session
    cursor.execute('''
        UPDATE game_sessions 
        SET coaching_points = coaching_points - ?, deck_cards = ?
        WHERE id = ?
    ''', (card_cost, json.dumps(deck_cards), session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'remaining_points': coaching_points - card_cost,
        'deck_size': len(deck_cards)
    })

@app.route('/api/game/<int:session_id>/sell-card', methods=['POST'])
def sell_card(session_id):
    """Remove a card from deck for 50% refund"""
    data = request.get_json()
    card_to_sell = data.get('card')
    
    if not card_to_sell:
        return jsonify({'error': 'No card specified'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session
    cursor.execute('SELECT coaching_points, deck_cards FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    coaching_points, deck_cards_json = result
    deck_cards = json.loads(deck_cards_json)
    
    # Find and remove card from deck
    card_found = False
    for i, card in enumerate(deck_cards):
        if card['id'] == card_to_sell['id'] and card['type'] == card_to_sell['type']:
            deck_cards.pop(i)
            card_found = True
            break
    
    if not card_found:
        conn.close()
        return jsonify({'error': 'Card not found in deck'}), 400
    
    # Calculate refund (50% of original cost)
    refund_amount = card_to_sell['data']['cost'] // 2
    
    # Update session
    cursor.execute('''
        UPDATE game_sessions 
        SET coaching_points = coaching_points + ?, deck_cards = ?
        WHERE id = ?
    ''', (refund_amount, json.dumps(deck_cards), session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'refund_amount': refund_amount,
        'remaining_points': coaching_points + refund_amount,
        'deck_size': len(deck_cards)
    })

@app.route('/api/game/<int:session_id>/draft-reward', methods=['GET'])
def get_draft_reward(session_id):
    """Get 3 random cards for draft pick after game win"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session
    cursor.execute('SELECT game_progress FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    game_progress = json.loads(result[0])
    
    # Check if player just won a game
    if game_progress.get('games_won', 0) == 0:
        conn.close()
        return jsonify({'error': 'No game win to reward'}), 400
    
    # Get all available cards
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()
    cursor.execute('SELECT * FROM plays')
    plays = cursor.fetchall()
    cursor.execute('SELECT * FROM modifiers')
    modifiers = cursor.fetchall()
    
    all_cards = []
    
    # Add players with weighted rarity
    for player in players:
        rarity = player[6]
        weight = {'common': 10, 'rare': 5, 'epic': 2, 'legendary': 1}.get(rarity, 1)
        for _ in range(weight):
            all_cards.append({
                'id': player[0],
                'type': 'player',
                'data': {
                    'id': player[0],
                    'name': player[1],
                    'position': player[2],
                    'team': player[3],
                    'base_stats': json.loads(player[4]),
                    'synergy_tags': json.loads(player[5]),
                    'rarity': player[6],
                    'cost': player[7]
                },
                'synergy_tags': json.loads(player[5])
            })
    
    # Add plays with weighted rarity
    for play in plays:
        rarity = play[5]
        weight = {'common': 10, 'rare': 5, 'epic': 2, 'legendary': 1}.get(rarity, 1)
        for _ in range(weight):
            all_cards.append({
                'id': play[0],
                'type': 'play',
                'data': {
                    'id': play[0],
                    'name': play[1],
                    'play_type': play[2],
                    'base_stats': json.loads(play[3]),
                    'synergy_tags': json.loads(play[4]),
                    'rarity': play[5],
                    'cost': play[6]
                },
                'synergy_tags': json.loads(play[4])
            })
    
    # Add modifiers with weighted rarity
    for modifier in modifiers:
        rarity = modifier[5]
        weight = {'common': 10, 'rare': 5, 'epic': 2, 'legendary': 1}.get(rarity, 1)
        for _ in range(weight):
            all_cards.append({
                'id': modifier[0],
                'type': 'modifier',
                'data': {
                    'id': modifier[0],
                    'name': modifier[1],
                    'modifier_type': modifier[2],
                    'effect': json.loads(modifier[3]),
                    'synergy_tags': json.loads(modifier[4]),
                    'rarity': modifier[5],
                    'cost': modifier[6]
                },
                'synergy_tags': json.loads(modifier[4])
            })
    
    # Select 3 random cards for draft
    draft_cards = random.sample(all_cards, min(3, len(all_cards)))
    
    conn.close()
    
    return jsonify({
        'draft_cards': draft_cards,
        'message': 'Choose 1 of 3 cards to add to your deck!'
    })

@app.route('/api/game/<int:session_id>/select-draft-card', methods=['POST'])
def select_draft_card(session_id):
    """Select a card from draft reward"""
    data = request.get_json()
    selected_card = data.get('card')
    
    if not selected_card:
        return jsonify({'error': 'No card specified'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current session
    cursor.execute('SELECT deck_cards FROM game_sessions WHERE id = ?', (session_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    deck_cards_json = result[0]
    deck_cards = json.loads(deck_cards_json)
    
    # Add selected card to deck
    deck_cards.append(selected_card)
    
    # Update session
    cursor.execute('''
        UPDATE game_sessions 
        SET deck_cards = ?
        WHERE id = ?
    ''', (json.dumps(deck_cards), session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'selected_card': selected_card,
        'deck_size': len(deck_cards)
    })

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

def calculate_drive_score(cards_played, game_state=None):
    """Calculate score and results for a drive based on cards played with defensive pressure and multipliers"""
    if not cards_played:
        return {
            'drive_score': 0,
            'cards_played': [],
            'drive_successful': False,
            'yards_gained': 0,
            'points_scored': 0,
            'turnover': False,
            'pressure_level': 0,
            'downs_used': 0,
            'first_down': False
        }
    
    # Initialize drive tracking
    total_yards = 0
    total_points = 0
    pressure_level = 0
    multiplier = 1.0
    turnover = False
    successful_plays = 0
    downs_used = 0
    first_down = False
    
    # Calculate defensive rating based on game progression
    defense_rating = 50  # Base defense
    if game_state:
        season = game_state.get('season', 1)
        game = game_state.get('game', 1)
        defense_rating += (season - 1) * 10 + (game - 1) * 5
    
    # Process each card played (each card = 1 down)
    for i, card in enumerate(cards_played):
        pressure_level += 5  # Pressure builds with each play
        downs_used += 1
        
        if card.get('type') == 'play':
            play_data = card.get('data', {})
            play_stats = play_data.get('base_stats', {})
            risk = play_stats.get('risk', 50)
            reward = play_stats.get('reward', 50)
            base_yards = play_stats.get('yards', 0)
            
            # Apply defensive pressure check
            success_chance = max(10, 100 - (risk * defense_rating / 100) - pressure_level)
            roll = random.randint(1, 100)
            
            if roll > success_chance:
                # Play failed - turnover!
                turnover = True
                break
            
            # Play succeeded - calculate yards with multipliers
            play_yards = base_yards * multiplier
            total_yards += play_yards
            successful_plays += 1
            
            # Check for scoring plays
            play_name = play_data.get('name', '').lower()
            if any(scoring_term in play_name for scoring_term in ['touchdown', 'field goal', 'hail mary']):
                if 'touchdown' in play_name:
                    total_points += 6
                elif 'field goal' in play_name:
                    total_points += 3
                elif 'hail mary' in play_name and play_yards >= 40:
                    total_points += 6
            
            # Apply synergy bonuses
            multiplier += calculate_synergy_bonus(card, cards_played[:i+1])
            
        elif card.get('type') == 'player':
            # Players provide stat bonuses to subsequent plays
            player_data = card.get('data', {})
            player_stats = player_data.get('base_stats', {})
            # Apply player bonuses to multiplier
            multiplier += 0.1  # Base player bonus
            
        elif card.get('type') == 'modifier':
            # Modifiers provide immediate effects
            modifier_data = card.get('data', {})
            effect = modifier_data.get('effect', {})
            
            if 'multiplier_boost' in effect:
                multiplier += effect['multiplier_boost']
            if 'scoring_multiplier' in effect:
                multiplier *= effect['scoring_multiplier']
    
    # Check for first down (10+ yards gained)
    if total_yards >= 10:
        first_down = True
    
    # Calculate final score
    base_score = successful_plays * 10
    yard_bonus = total_yards * multiplier
    point_bonus = total_points * 20
    
    # Drive is successful if we gain at least 10 yards, score points, or get a first down
    drive_successful = not turnover and (total_yards >= 10 or total_points > 0 or first_down)
    
    if drive_successful:
        final_score = base_score + yard_bonus + point_bonus
    else:
        final_score = 0  # Failed drives give no points
    
    return {
        'drive_score': int(final_score),
        'cards_played': cards_played,
        'drive_successful': drive_successful,
        'yards_gained': int(total_yards),
        'points_scored': total_points,
        'turnover': turnover,
        'pressure_level': pressure_level,
        'multiplier': multiplier,
        'successful_plays': successful_plays,
        'downs_used': downs_used,
        'first_down': first_down
    }

def calculate_synergy_bonus(card, all_cards_played):
    """Calculate synergy bonus for a card based on other cards played"""
    bonus = 0.0
    
    if not card.get('synergy_tags'):
        return bonus
    
    card_tags = card['synergy_tags']
    
    # Count matching synergy tags
    for other_card in all_cards_played[:-1]:  # Exclude current card
        if other_card.get('synergy_tags'):
            matching_tags = set(card_tags) & set(other_card['synergy_tags'])
            bonus += len(matching_tags) * 0.1  # 0.1x per matching tag
    
    # Position synergy bonuses
    if card.get('type') == 'play':
        play_type = card.get('data', {}).get('play_type', '')
        
        # Count players of matching positions
        qb_count = sum(1 for c in all_cards_played if c.get('type') == 'player' and c.get('data', {}).get('position') == 'QB')
        wr_count = sum(1 for c in all_cards_played if c.get('type') == 'player' and c.get('data', {}).get('position') == 'WR')
        rb_count = sum(1 for c in all_cards_played if c.get('type') == 'player' and c.get('data', {}).get('position') == 'RB')
        
        if play_type == 'passing' and qb_count > 0:
            bonus += 0.2 * qb_count
        if play_type == 'passing' and wr_count > 0:
            bonus += 0.15 * wr_count
        if play_type == 'rushing' and rb_count > 0:
            bonus += 0.2 * rb_count
    
    # Rarity bonuses
    rarity = card.get('data', {}).get('rarity', 'common')
    if rarity == 'epic':
        bonus += 0.3
    elif rarity == 'legendary':
        bonus += 0.5
    
    return bonus

if __name__ == '__main__':
    init_db()
    seed_initial_data()
    app.run(debug=True, port=5000)
