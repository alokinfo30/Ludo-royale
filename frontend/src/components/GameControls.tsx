"use client";
import { GameStateData } from "@/types/game";
import Dice from "./Dice";
import PlayerPanel from "./PlayerPanel";
import ChatBox from "./ChatBox";

export default function GameControls({ state, messages, sendAction }: { state: GameStateData | null, messages: any[], sendAction: (action: string, payload?: any) => void }) {
  const handleRoll = () => sendAction("roll_dice");

  // UI to select valid moves (simplified)
  const validMoves = /* get from state or WS message */ [];

  return (
    <div className="flex flex-col items-center space-y-4">
      <Dice value={state?.dice_value ?? null} onRoll={handleRoll} />
      {state?.players && (
        <div className="grid grid-cols-2 gap-2">
          {state.players.map((p) => (
            <PlayerPanel key={p.color} player={p} isCurrent={p.color === state.players[state.current_player_index]?.color} />
          ))}
        </div>
      )}
      <ChatBox messages={messages} />
      {/* Move buttons generated from validMoves */}
    </div>
  );
}