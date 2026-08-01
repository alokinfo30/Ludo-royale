import { useEffect, useRef, useState } from "react";
import { GameStateData } from "@/types/game";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useGameSocket(gameId: string | null) {
  const [state, setState] = useState<GameStateData | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!gameId) return;
    const ws = new WebSocket(`${WS_URL}/ws/${gameId}`);
    wsRef.current = ws;

    ws.onopen = () => console.log("WS connected");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "state") {
        setState(data.payload);
      } else if (data.type === "message") {
        setMessages((prev) => [...prev, data.payload.commentary || ""]);
      }
    };
    ws.onclose = () => console.log("WS disconnected");

    return () => {
      ws.close();
    };
  }, [gameId]);

  const sendAction = (action: string, payload?: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action, ...payload }));
    }
  };

  return { state, messages, sendAction };
}