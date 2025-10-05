## Gemini Chatbot (FastAPI + React + Tailwind)

### Prereqs
- Python 3.10+
- Node 18+

### Backend setup
```bash
cd backend
copy .env.example .env   # or create .env and add GEMINI_API_KEY=...
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Frontend proxy forwards /api to http://localhost:8000.

### Embed on any website
Add this script tag to your site’s HTML (change the data-origin to your deployed frontend origin):

```html
<script src="/chat-widget.js" data-origin="http://localhost:5173"></script>
```

It renders a floating orange chat button; clicking opens a panel with the app embedded.

### How it works
- POST /api/chat { message }
- FastAPI calls Google Gemini (gemini-1.5-flash) and returns { response }
- React stores messages in localStorage, animates new messages, and keeps input sticky

### Files
- backend/main.py – FastAPI server with CORS and Gemini integration
- backend/requirements.txt – Python deps
- frontend/ – Vite React app with Tailwind and Framer Motion
- tailwind.config.js – Tailwind scan paths


