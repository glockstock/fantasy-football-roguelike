export interface Player {
  id: number;
  name: string;
  position: string;
  team: string;
  base_stats: {
    [key: string]: number;
  };
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  cost: number;
}

export interface Play {
  id: number;
  name: string;
  play_type: string;
  base_stats: {
    risk: number;
    reward: number;
    yards: number;
  };
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  cost: number;
}

export interface Modifier {
  id: number;
  name: string;
  modifier_type: string;
  effect: {
    [key: string]: number;
  };
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  cost: number;
}

export interface Card {
  id: number;
  type: 'player' | 'play' | 'modifier';
  data: Player | Play | Modifier;
}

export interface GameState {
  session_id: number;
  deck: {
    players: number[];
    plays: number[];
    modifiers: number[];
  };
  season: number;
  run: number;
  score: number;
  hand?: Card[];
  field?: Card[];
  career_level: CareerLevel;
  career_progress: CareerProgress;
}

export interface CareerLevel {
  level: 'high_school' | 'college' | 'nfl' | 'hall_of_fame';
  name: string;
  description: string;
  required_score: number;
  next_level?: string;
}

export interface CareerProgress {
  current_level: string;
  total_score: number;
  championships_won: number;
  super_bowls_won: number;
  hall_of_fame_points: number;
}

export interface DeckType {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  cards: {
    players: number[];
    plays: number[];
    modifiers: number[];
  };
  unlock_requirement?: {
    career_level?: string;
    score_threshold?: number;
  };
}

export interface AppState {
  currentScreen: 'splash' | 'deck_selection' | 'game';
  selectedDeckType?: string;
  playerName?: string;
}

export interface RunResult {
  run_score: number;
  cards_played: Card[];
  valid_run: boolean;
}
