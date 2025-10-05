import os
import html as html_lib
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import threading

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API (Free-tier)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API key configured successfully.")
else:
    print("⚠️ GEMINI_API_KEY missing! Please set it in your .env file.")

# Initialize FastAPI
app = FastAPI(title="Gemini Chat API with Context Memory + Canvas")

# Allow all CORS origins for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Pydantic Schemas
# ---------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # session identifier for memory (if omitted, server creates a transient one)
    memory_size: Optional[int] = 6    # how many recent turns to include (default 6)
    system: Optional[str] = None      # optional system prompt/instruction for this session (stored as system role)

class ChatResponse(BaseModel):
    response: str                       # plain text response
    model: str
    html: Optional[str] = None
    markdown: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[str] = None
    session_id: Optional[str] = None    # session id used (if any)
    canvas_script: Optional[str] = None # JS function body string to render into a <canvas>

class MemoryItem(BaseModel):
    role: str    # "user" or "assistant" or "system"
    text: str
    timestamp: str

# ---------------------------
# Conversation memory manager
# ---------------------------
class ConversationMemory:
    """
    Simple thread-safe in-memory store for conversation history.
    Stores a list of message dicts per session_id:
      [{"role": "user", "text": "...", "timestamp": "..."}, ...]
    """

    def __init__(self):
        self._store: Dict[str, List[Dict[str, str]]] = {}
        self._lock = threading.Lock()

    def add_message(self, session_id: str, role: str, text: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        item = {"role": role, "text": text, "timestamp": ts}
        with self._lock:
            if session_id not in self._store:
                self._store[session_id] = []
            self._store[session_id].append(item)

    def get_recent(self, session_id: str, limit: int = 6) -> List[Dict[str, str]]:
        with self._lock:
            items = list(self._store.get(session_id, []))
        # return last `limit` *turns* (turn == single message). Keep chronological order
        return items[-limit:] if limit and len(items) > limit else items

    def get_all(self, session_id: str) -> List[Dict[str, str]]:
        with self._lock:
            return list(self._store.get(session_id, []))

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)

    def sessions(self) -> List[str]:
        with self._lock:
            return list(self._store.keys())

# global conversation memory instance
memory = ConversationMemory()

# ---------------------------
# Canvas script builder
# ---------------------------
def build_canvas_script(
    canvas_w: int = 600,
    canvas_h: int = 160,
    bg: str = "#0f172a",
    bubble: str = "#ffffff",
    text_color: str = "#0b1220",
    author_badge: str = "Assistant",
    font_family: str = "16px Arial",
    line_height: int = 22,
    typing_speed: int = 40          # characters per second (rough)
) -> str:
    """
    Returns a JS function body (string). The client will run:
      const fn = new Function('canvas','textData', script);
      fn(canvas, { text: '...' });
    The script reads textData.text and renders a wrapped, animated typed text inside a bubble.
    """
    js = f"""
// canvas, textData => render typed bubble
(function(){{ 
  const CANVAS_W = {canvas_w}, CANVAS_H = {canvas_h};
  const BACKGROUND = "{bg}";
  const BUBBLE = "{bubble}";
  const TEXTCOLOR = "{text_color}";
  const AUTHOR = "{author_badge}";
  const FONT = "{font_family}";
  const LINEHEIGHT = {line_height};
  const SPEED = {typing_speed}; // chars/sec

  // DPR scaling
  const DPR = window.devicePixelRatio || 1;
  canvas.width = CANVAS_W * DPR; canvas.height = CANVAS_H * DPR;
  canvas.style.width = CANVAS_W + 'px'; canvas.style.height = CANVAS_H + 'px';
  const ctx = canvas.getContext('2d');
  ctx.scale(DPR, DPR);
  ctx.textBaseline = 'top';
  ctx.font = FONT;

  // utility: draw rounded rect (path)
  function roundRectPath(x,y,w,h,r) {{
    ctx.beginPath();
    ctx.moveTo(x+r,y);
    ctx.arcTo(x+w,y,x+w,y+h,r);
    ctx.arcTo(x+w,y+h,x,y+h,r);
    ctx.arcTo(x,y+h,x,y,r);
    ctx.arcTo(x,y,x+w,y,r);
    ctx.closePath();
  }}

  // wrap text into lines given width
  function wrapText(text, maxWidth) {{
    const words = text.split(/(\\s+)/); // keep whitespace tokens
    const lines = [];
    let cur = '';
    for (let i=0;i<words.length;i++){{
      const test = cur + words[i];
      const metrics = ctx.measureText(test);
      if (metrics.width > maxWidth && cur.length>0) {{
        lines.push(cur.trimEnd());
        cur = words[i];
      }} else {{
        cur = test;
      }}
    }}
    if (cur.trim().length) lines.push(cur.trim());
    return lines;
  }}

  const padding = 14;
  const bubble_w = CANVAS_W - padding*2;
  const bubble_h = CANVAS_H - padding*2;

  // source text (safe): caller provides it via textData
  const rawText = (textData && typeof textData.text === 'string') ? textData.text : '';
  // limit length to avoid infinite animations
  const safeText = rawText.length > 2000 ? rawText.slice(0,2000) + '…' : rawText;

  // build lines — measure with a temporary font
  ctx.font = FONT;
  const maxInnerW = bubble_w - 20;
  const lines = wrapText(safeText.replace(/\\t/g,'    '), maxInnerW);

  // typing variables
  const totalChars = safeText.replace(/\\n/g,' ').length;
  let shownChars = 0;
  const intervalMs = 1000 / Math.max(1, SPEED);

  // animation loop
  let last = performance.now();
  function step(now) {{
    const dt = now - last;
    last = now;
    // advance characters based on elapsed time
    shownChars += dt * (SPEED / 1000) * 1000 / 1000; // approximate (keeps smooth)
    if (shownChars > totalChars) shownChars = totalChars;

    // background clear
    ctx.clearRect(0,0,CANVAS_W,CANVAS_H);

    // bubble shadow + bg
    ctx.fillStyle = BACKGROUND;
    ctx.fillRect(0,0,CANVAS_W,CANVAS_H);

    // bubble
    ctx.save();
    ctx.fillStyle = BUBBLE;
    ctx.shadowColor = 'rgba(2,6,23,0.15)';
    ctx.shadowBlur = 10;
    roundRectPath(padding, padding, bubble_w, bubble_h, 14);
    ctx.fill();
    ctx.restore();

    // author badge
    ctx.fillStyle = TEXTCOLOR;
    ctx.font = '12px Arial';
    ctx.fillText(AUTHOR, padding + 8, padding + 6);

    // draw typed text
    ctx.font = FONT;
    ctx.fillStyle = TEXTCOLOR;
    const txt = safeText;
    let charCount = Math.floor(shownChars);
    let y = padding + 30;
    // naive per-line slicing
    for (let i=0;i<lines.length;i++) {{
      const ln = lines[i];
      const draw = ln.slice(0, Math.max(0, Math.min(charCount, ln.length)));
      ctx.fillText(draw, padding + 12, y);
      y += LINEHEIGHT;
      charCount -= ln.length;
      if (charCount <= 0 && shownChars < totalChars) break;
    }}

    // cursor when still typing
    if (shownChars < totalChars) {{
      const lastLine = lines[Math.max(0, Math.min(lines.length-1, Math.floor(shownChars / Math.max(1, Math.floor(maxInnerW / 8)))))];
      const cursorX = padding + 12 + ctx.measureText(lastLine ? lastLine.slice(0, Math.max(0, Math.min(Math.floor(shownChars), lastLine.length))) : '').width;
      const cursorY = y - LINEHEIGHT;
      const on = Math.floor(now / 500) % 2 === 0;
      if (on) {{
        ctx.fillRect(cursorX, cursorY, 8, 2);
      }}
    }}

    // done?
    if (shownChars < totalChars) {{
      requestAnimationFrame(step);
    }}
  }}

  // start animation
  requestAnimationFrame(step);
}})();
"""
    return js

# ---------------------------
# Utility helpers
# ---------------------------
def build_visual_payload(text: str) -> Dict[str, Any]:
    if text is None:
        text = ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if "\n\n" in text:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    else:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    html_parts = []
    segments = []
    for p in paragraphs:
        safe = html_lib.escape(p)
        safe = safe.replace("\n", "<br>")
        html_parts.append(f"<p>{safe}</p>")
        segments.append({"type": "paragraph", "text": p})

    html = "\n".join(html_parts) if html_parts else "<p>(empty)</p>"
    markdown = "\n\n".join(paragraphs) if paragraphs else ""
    return {"html": html, "markdown": markdown, "segments": segments}

def build_prompt_with_context(session_id: Optional[str], user_message: str, memory_size: int) -> str:
    """
    Build a prompt that includes recent context for Gemini.
    Order:
      1) System messages (oldest first)
      2) Conversation history (oldest first)
      3) New user message
      4) Assistant:
    """
    parts = []

    # include system messages first (if any)
    if session_id:
        all_items = memory.get_all(session_id)
        system_msgs = [it for it in all_items if it["role"] == "system"]
        if system_msgs:
            parts.append("System instructions:")
            for it in system_msgs:
                parts.append(it["text"].strip())
            parts.append("")  # blank line

    # include recent conversation turns (user/assistant)
    if session_id:
        recent = memory.get_recent(session_id, limit=memory_size)
        if recent:
            parts.append("Conversation history (oldest → newest):")
            for item in recent:
                role = item["role"].capitalize()
                # skip system entries here (we already included them)
                if item["role"] == "system":
                    continue
                text = item["text"].strip()
                parts.append(f"{role}: {text}")
            parts.append("")  # blank line

    # Add new user message
    parts.append("User: " + user_message.strip())
    parts.append("Assistant:")
    return "\n".join(parts)

# ---------------------------
# Routes
# ---------------------------
@app.get("/health")
def health():
    """Health check endpoint"""
    return {"ok": True}

@app.get("/api/models")
def models():
    """List available Gemini models"""
    return {"models": ["gemini-2.5-flash"]}

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Chat endpoint to interact with Gemini and session memory"""
    # choose or create session id
    session_id = req.session_id or f"session-{int(datetime.now(timezone.utc).timestamp()*1000)}"
    # clamp memory_size
    memory_size = req.memory_size if (req.memory_size and req.memory_size > 0) else 6

    # if provided, store system instruction (will be placed at top of prompt)
    if req.system:
        memory.add_message(session_id, "system", req.system)

    if not GEMINI_API_KEY:
        canvas_script = build_canvas_script(
            canvas_w=520, canvas_h=140, bg="#0f172a", bubble="#fff3f0",
            text_color="#6b2800", author_badge="Server"
        )
        return ChatResponse(
            response="Server is missing GEMINI_API_KEY. Please set it in .env.",
            model="gemini-2.5-flash",
            html="<p><strong>Server is missing GEMINI_API_KEY.</strong> Please set it in .env.</p>",
            markdown="**Server is missing GEMINI_API_KEY.** Please set it in .env.",
            segments=[{"type": "error", "text": "Server is missing GEMINI_API_KEY. Please set it in .env."}],
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            canvas_script=canvas_script
        )

    # store user's message in memory
    memory.add_message(session_id, "user", req.message)

    try:
        # BUG FIX / IMPORTANT: always pass the active session_id so memory is included
        prompt = build_prompt_with_context(session_id, req.message, memory_size)

        # Call Gemini (SDK usage kept simple)
        model = genai.GenerativeModel("gemini-2.5-flash")
        result = model.generate_content(prompt)

        # Extract text safely
        text = getattr(result, "text", None)
        if not text and getattr(result, "candidates", None):
            first = result.candidates[0]
            # defensively get nested text
            text = getattr(first, "content", None) or getattr(first, "text", None)
            if text and getattr(text, "parts", None):
                try:
                    text = text.parts[0].text
                except Exception:
                    text = str(text)

        if not text:
            text = "(empty response)"

        # store assistant's response in memory
        memory.add_message(session_id, "assistant", text)

        # Build visual result
        visual = build_visual_payload(text)

        # canvas script generated server-side (script body only). Client should run it with:
        # const fn = new Function('canvas','textData', canvasScript); fn(canvas, { text: assistantText });
        canvas_script = build_canvas_script(
            canvas_w=520,
            canvas_h=180,
            bg="#0f172a",
            bubble="#ffffff",
            text_color="#0b1220",
            author_badge="Assistant",
            font_family="16px Inter, Arial",
            line_height=20,
            typing_speed=45
        )

        return ChatResponse(
            response=text,
            model="gemini-2.5-flash",
            html=visual["html"],
            markdown=visual["markdown"],
            segments=visual["segments"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            canvas_script=canvas_script
        )

    except Exception as e:
        err_text = f"Error communicating with Gemini API: {e}"
        memory.add_message(session_id, "assistant", err_text)
        visual = build_visual_payload(err_text)
        canvas_script = build_canvas_script(
            canvas_w=520, canvas_h=140, bg="#0f172a", bubble="#fff7f7",
            text_color="#7a1f1f", author_badge="Assistant"
        )
        return ChatResponse(
            response=err_text,
            model="gemini-2.5-flash",
            html=visual["html"],
            markdown=visual["markdown"],
            segments=visual["segments"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            canvas_script=canvas_script
        )

# ---------------------------
# Memory management endpoints
# ---------------------------
@app.get("/api/memory/{session_id}", response_model=List[MemoryItem])
def get_memory(session_id: str):
    """Return the full memory for a session (chronological)"""
    items = memory.get_all(session_id)
    return [MemoryItem(**it) for it in items]

@app.delete("/api/memory/{session_id}")
def clear_memory(session_id: str):
    """Clear memory for a session"""
    memory.clear(session_id)
    return {"ok": True, "message": f"Cleared memory for session {session_id}"}

@app.get("/api/memory")
def list_sessions():
    """List session ids currently stored"""
    return {"sessions": memory.sessions()}

# ---------------------------
# Run the FastAPI server
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
