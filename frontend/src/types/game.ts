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
}

export interface RunResult {
  run_score: number;
  cards_played: Card[];
  valid_run: boolean;
}
