"use client";
import { GameStateData } from "@/types/game";
import Token from "./Token";

export default function Board({ state, theme }: { state: GameStateData; theme?: any }) {
  if (!state) {
    return <div className="w-[600px] h-[600px] flex items-center justify-center bg-gray-200">Loading board...</div>;
  }

    // Board layout: 15x15 grid for classic Ludo visual
  const cellStyle = (color?: string) => ({
    background: color || "#eee",
    border: "1px solid #999",
  });

  return (
    <div
      className="grid grid-cols-15 gap-0 w-[600px] h-[600px] border-4 border-black relative"
      style={{ background: theme?.boardBackground || "#f0d9b5" }}
    >
      {state.players.map((player) =>
        player.tokens.map((token) => {
          if (token.position.type === "home") return null;

          const pos = token.position;
          let x = 0;
          let y = 0;

          if (pos.type === "base") {
            switch (player.color) {
              case "RED":
                x = 2;
                y = 2;
                break;
              case "GREEN":
                x = 12;
                y = 2;
                break;
              case "YELLOW":
                x = 12;
                y = 12;
                break;
              case "BLUE":
                x = 2;
                y = 12;
                break;
            }
          } else if (pos.type === "track") {
            const idx = pos.index ?? 0;
            x = 7 + (idx % 6);
            y = 7 + Math.floor(idx / 6);
          }

          return (
            <Token
              key={`${player.color}-${token.id}`}
              color={player.color}
              id={token.id}
              style={{ position: "absolute", left: `${x * 40}px`, top: `${y * 40}px` }}
              themeColor={theme?.tokenColors?.[player.color]}
            />
          );
        })
      )}
    </div>
  );
}