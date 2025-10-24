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
  synergy_tags?: string[];
  multiplier_effect?: number;
  combo_trigger?: ComboCondition;
}

export interface ComboCondition {
  type: 'position_count' | 'play_chain' | 'rarity_match';
  condition: any;
  bonus: number;
}

export interface GameState {
  session_id: number;
  deck: {
    players: number[];
    plays: number[];
    modifiers: number[];
  };
  season: number;
  game: number;
  drive: number;
  score: number;
  hand: Card[];
  field: Card[];
  deck_cards: Card[];
  bench: Card[];
  discard_pile: Card[];
  coaching_points: number;
  downs: number;
  distance: number;
  yards_to_go: number;
  pressure_level: number;
  career_level: CareerLevel;
  career_progress: CareerProgress;
  game_progress: GameProgress;
  season_progress: SeasonProgress;
}

export interface GameProgress {
  current_game: number;
  current_drive: number;
  drives_completed: number;
  games_won: number;
  total_drives_in_game: number;
  total_games_in_season: number;
}

export interface SeasonProgress {
  current_season: number;
  games_won: number;
  seasons_won: number;
  total_games_in_season: number;
  total_seasons: number;
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

export interface DriveResult {
  drive_score: number;
  cards_played: Card[];
  drive_successful: boolean;
  yards_gained: number;
  points_scored: number;
}

export interface GameResult {
  game_won: boolean;
  total_score: number;
  drives_completed: number;
  final_drive_result?: DriveResult;
}

export interface SeasonResult {
  season_won: boolean;
  games_won: number;
  total_score: number;
  championship_earned: boolean;
}
