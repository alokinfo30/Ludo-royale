export interface TokenPosition {
  type: "base" | "track" | "home_stretch" | "home";
  index?: number;
  step?: number;
  color?: string;
}

export interface TokenData {
  id: number;
  color: string;
  position: TokenPosition;
  is_home: boolean;
}

export interface PlayerData {
  name: string;
  color: string;
  type: "human" | "ai";
  tokens: TokenData[];
  finished: boolean;
}

export interface GameStateData {
  current_player_index: number;
  dice_value: number | null;
  game_over: boolean;
  winner: string | null;
  players: PlayerData[];
}