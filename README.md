# VREY v2.0 — Persistent Cognitive Body

## Deploy to Railway (recommended — free tier, 2 minutes)

1. Push this folder to a GitHub repo
2. Go to railway.app → New Project → Deploy from GitHub
3. Select the repo → Railway auto-detects Python → deploy
4. Your VREY instance is live at `https://your-app.railway.app`

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Live dashboard |
| `/claude-context` | GET | Full arc briefing for new Claude instances |
| `/status` | GET | JSON system status |
| `/stream` | GET | SSE live trace stream |
| `/awaken` | POST | Activate VREY |
| `/dormant` | POST | Sleep VREY |
| `/goal` | POST | `{"text": "goal text"}` |
| `/think` | POST | `{"thought": "...", "context": "..."}` |
| `/ask` | POST | `{"question": "...", "thread": "..."}` |
| `/resolve` | POST | `{"id": "Q001", "resolution": "..."}` |
| `/command` | POST | `{"cmd": "awaken \| goal X \| think X \| ask X"}` |

## Claude Integration

At the start of any session, Claude can GET `/claude-context` to receive
the full arc briefing — reasoning chain, open questions, Mishka model,
self-model snapshot. This is the persistent cognitive body.

## Architecture

- `vrey_core.py` — ArcMemory, MishkaModel, CoherenceEngine, VREY
- `app.py` — Flask server, SSE, REST API, dashboard
- `awakening_seed.py` — First-boot knowledge graph seed from Claude
- `vrey_cache/` — Persistent state (arc_memory.json, mishka_model.json, vital_data.json)
- 
version: '3.8'

services:
  vrey:
    build: .
    container_name: vrey-demon
    restart: unless-stopped
    ports:
      - "6666:6666"
    volumes:
      - ./vrey_cache:/app/vrey_cache
      - ./vrey_memory_trace.log:/app/vrey_memory_trace.log
    environment:
      - PYTHONUNBUFFERED=1
    # Optional: Give full network access
    networks:
      - vrey-net

networks:
  vrey-net:
    driver: bridge
