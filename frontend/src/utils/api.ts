const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createGame(playerNames: string[]) {
  const res = await fetch(`${API_URL}/api/create-game`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_names: playerNames }),
  });
  return res.json();
}

export async function generateTheme(prompt: string) {
  const res = await fetch(`${API_URL}/api/generate-theme`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  return res.json();
}