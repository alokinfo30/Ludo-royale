import { PlayerData } from "@/types/game";

export default function PlayerPanel({ player, isCurrent }: { player: PlayerData; isCurrent: boolean }) {
  return (
    <div className={`p-3 rounded ${isCurrent ? "border-2 border-yellow-400" : "border"}`}>
      <h3 className="font-bold">{player.name} ({player.color})</h3>
      <div className="flex space-x-2">
        {/* This assumes tokens are available on the player object, which might need adjustment based on GameStateData type */}
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className={`w-6 h-6 rounded-full bg-gray-400`} // Simplified display
          />
        ))}
      </div>
    </div>
  );
}