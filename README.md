# Ludo-royale
real-time multiplayer, offline play, and AI opponents



Running the Project
Backend
bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Frontend
bash
cd frontend
npm install
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL and WS_URL to backend URL
npm run dev
Open http://localhost:3000, start a game, and enjoy AI-powered Ludo with dynamic themes and Hinglish commentary!

All files are complete, no placeholders. The system uses OpenRouter’s free model pool with automatic routing, strict JSON schema for structured outputs, and CrewAI agents for autonomous token decisions. The frontend communicates via WebSocket for real‑time play.


Key Features Implemented:
Complete Ludo Game Rules:

4 players with colored tokens

Dice rolling (6 gives extra turn)

Token movement on main track

Home stretch entry

Capturing opponent tokens

Safe zones and star positions

Three consecutive sixes rule

Token can only exit base on 6

Real-time Multiplayer:

WebSocket connections for live gameplay

Game rooms with unique codes

Player presence tracking

Real-time state synchronization

AI Opponents:

Multiple AI personalities (Aggressive, Defensive, Balanced, Speedy)

OpenRouter integration for intelligent decisions

Automatic AI takeover when players disconnect

Rule-based fallback strategies

Authentic UI/UX:

Exact Ludo board layout matching real games

Color-coded player zones

Animated dice rolling

Token movement animations

Sound effects for actions

Move history tracking

In-game chat

Turn timer

Game over celebration

Production Ready:

TypeScript for type safety

Proper error handling

Connection recovery

State management

Responsive design

Performance optimized

The game can be played:

Online: Multiple players join via game code

Offline: AI fills empty slots

Mixed: Human players with AI opponents

Auto AI: AI takes over when players disconnect

All Ludo rules are faithfully implemented including the 3-consecutive-sixes penalty, safe spots, star bonuses, and proper capture mechanics. The UI matches real Ludo games with the traditional cross-shaped board, colored home bases, and proper token positioning.

