"use client";
import { useState } from "react";
import Board from "@/components/Board";
import GameControls from "@/components/GameControls";
import { useGameSocket } from "@/hooks/useGameSocket";
import ThemeCustomizer from "@/components/ThemeCustomizer";
import { createGame } from "@/utils/api";

export default function Home() {
  const [gameId, setGameId] = useState<string | null>(null);
  const [theme, setTheme] = useState<any>(null);
  // Lift the game socket hook to the parent component
  const { state, messages, sendAction } = useGameSocket(gameId);

  const startGame = async () => {
    const data = await createGame(["Human", "Aggressor AI", "Safe AI", "Random AI"]);
    setGameId(data.game_id);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 space-y-6">
      <h1 className="text-4xl font-bold">Ludo AI 🎲</h1>
      {!gameId ? (
        <button onClick={startGame} className="bg-green-600 text-white px-6 py-3 rounded-xl">
          Start New Game
        </button>
      ) : (
        <>
          <ThemeCustomizer onApply={setTheme} />
          {state ? (
            <div className="flex space-x-8">
              <Board state={state} theme={theme} />
              <GameControls state={state} messages={messages} sendAction={sendAction} />
            </div>
          ) : (
            <p className="text-gray-400">Connecting to the game server...</p>
          )}
        </>
      )}
    </main>
  );
}