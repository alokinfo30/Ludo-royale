"use client";
import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import LudoBoard from "@/components/game/LudoBoard";
import DiceRoller from "@/components/game/DiceRoller";
import PlayerInfo from "@/components/game/PlayerInfo";
import GameChat from "@/components/game/GameChat";
import MoveHistory from "@/components/game/MoveHistory";
import GameOverModal from "@/components/game/GameOverModal";
import Timer from "@/components/game/Timer";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useSound } from "@/hooks/useSound";
import { GameState, PlayerColor } from "@/types/game";

export default function GamePage() {
  const params = useParams();
  const gameId = params.gameId as string;
  const userId = "player_" + Math.random().toString(36).substr(2, 9);
  
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [showGameOver, setShowGameOver] = useState(false);
  
  const { playSound } = useSound();
  
  const handleGameMessage = useCallback((message: any) => {
    switch (message.type) {
      case "game_state":
        setGameState(message.data);
        break;
      case "dice_rolled":
        playSound("dice-roll");
        break;
      case "move_made":
        if (message.data.captured) {
          playSound("token-cut");
        } else if (message.data.gameOver) {
          playSound("victory");
        } else {
          playSound("token-move");
        }
        if (message.data.gameOver) {
          setTimeout(() => setShowGameOver(true), 2000);
        }
        break;
      case "chat":
        // Handle chat messages
        break;
    }
  }, [playSound]);
  
  const { sendMessage, isConnected } = useWebSocket(
    gameId,
    userId,
    handleGameMessage
  );
  
  const handleRollDice = () => {
    sendMessage({ action: "roll_dice" });
  };
  
  const handleTokenClick = (color: PlayerColor, tokenId: number) => {
    if (!gameState || gameState.currentTurn !== color) return;
    
    // Check if token has valid move
    const hasValidMove = gameState.validMoves?.some(
      (move: any) => move.tokenId === tokenId
    );
    
    if (hasValidMove) {
      sendMessage({ action: "make_move", tokenId });
    }
  };
  
  if (!gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl font-bold">Loading game...</div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-indigo-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold text-white">
            Ludo Royale
          </h1>
          <div className="text-white">
            Game Code: <span className="font-bold text-yellow-400">{gameId}</span>
          </div>
        </div>
        
        {/* Main Game Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Panel - Player Info */}
          <div className="space-y-4">
            {gameState.players && Object.entries(gameState.players).map(([color, player]: [string, any]) => (
              <PlayerInfo
                key={color}
                color={color as PlayerColor}
                player={player}
                isCurrentTurn={gameState.currentTurn === color}
                isActive={true}
              />
            ))}
          </div>
          
          {/* Center - Board */}
          <div className="lg:col-span-2">
            <div className="flex flex-col items-center space-y-4">
              {/* Timer */}
              <Timer
                timeLeft={gameState.turnTimeLeft || 30}
                isActive={gameState.phase === "rolling" || gameState.phase === "moving"}
              />
              
              {/* Board */}
              <LudoBoard
                gameState={gameState}
                onTokenClick={handleTokenClick}
                currentPlayer={gameState.currentTurn}
              />
              
              {/* Dice Roller */}
              <DiceRoller
                diceValue={gameState.diceValue}
                isRolling={gameState.phase === "rolling"}
                canRoll={gameState.phase === "rolling" && 
                         gameState.currentTurn === userId}
                onRoll={handleRollDice}
                consecutiveSixes={gameState.players?.[gameState.currentTurn]?.consecutiveSixes || 0}
              />
            </div>
          </div>
        </div>
        
        {/* Bottom Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
          <MoveHistory moves={gameState.moveHistory || []} />
          <GameChat
            gameId={gameId}
            userId={userId}
            messages={gameState.chatMessages || []}
            onSendMessage={(msg) => sendMessage({ action: "chat_message", message: msg })}
          />
        </div>
      </div>
      
      {/* Game Over Modal */}
      {showGameOver && gameState.winner && (
        <GameOverModal
          winner={gameState.winner}
          players={gameState.players}
          onClose={() => setShowGameOver(false)}
          onPlayAgain={() => {/* Handle play again */}}
        />
      )}
    </div>
  );
}