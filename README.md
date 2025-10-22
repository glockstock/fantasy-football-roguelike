# Fantasy Football Roguelike Deckbuilder

A roguelike deckbuilding game that combines fantasy football mechanics with card game elements, inspired by Balatro but with football themes.

## Game Concept

Players build decks of football players, plays, and modifiers to score points through "runs" - sequences of cards that represent football drives. Each run must end with a scoring play (touchdown, field goal, etc.) to be valid.

## Core Mechanics

- **Deck Building**: Collect and upgrade football players, plays, and modifiers
- **Runs**: Play sequences of cards representing football drives
- **Scoring**: Complete runs to score points and advance through seasons
- **Roguelike Elements**: Procedural generation, permadeath, and meta-progression

## Tech Stack

- **Frontend**: React with TypeScript
- **Backend**: Python Flask with SQLite
- **Styling**: Tailwind CSS
- **State Management**: React Context + useReducer

## Getting Started

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Project Structure

```
fantasy-football-roguelike/
├── backend/           # Python Flask API
├── frontend/          # React application
├── shared/           # Shared types and constants
└── README.md
```
