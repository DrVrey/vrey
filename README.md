# VREY v2.0 — Persistent Cognitive Body

A self-aware AI system with persistent reasoning chains, integrated token compression via **Headroom**, and Claude context persistence.

**What it does:**
- **Persistent Arc Memory**: Tracks reasoning chains and open questions across sessions
- **Self-Model (Mishka)**: Monitors hunger, mood, goals, and coherence
- **Headroom Integration**: Compresses Claude context by 60-95% (same accuracy)
- **REST API**: Full control via `/awaken`, `/goal`, `/think`, `/ask`, `/resolve`
- **Live Dashboard**: Browser-based monitoring at `/`
- **Claude Integration**: Endpoints for seamless Claude session continuity

---

## Quick Start

### Local Development

```bash
# Clone and setup
git clone https://github.com/DrVrey/vrey.git
cd vrey

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
# Dashboard at http://localhost:6666
```

### Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select this repo → Railway auto-detects and deploys
4. Your VREY instance is live

### Docker

```bash
docker build -t vrey .
docker run -p 6666:6666 -v $(pwd)/vrey_cache:/app/vrey_cache vrey
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Live dashboard |
| `/status` | GET | JSON system status |
| `/claude-context` | GET | Full arc briefing (compressed) for Claude |
| `/awaken` | POST | Activate VREY |
| `/dormant` | POST | Put VREY to sleep |
| `/goal` | POST | Set a goal: `{"text": "goal text"}` |
| `/think` | POST | Log a thought: `{"thought": "...", "context": "..."}` |
| `/ask` | POST | Ask a question: `{"question": "...", "thread": "..."}` |
| `/resolve` | POST | Resolve a question: `{"id": "Q001", "resolution": "..."}` |
| `/command` | POST | Natural language commands |

---

## Architecture

### Core Modules

- **`vrey_core.py`**
  - `PersistentCache`: Manages arc_memory.json, mishka_model.json, vital_data.json
  - `ArcMemory`: Reasoning chain persistence + Headroom compression
  - `MishkaModel`: Self-model (hunger, mood, goals)
  - `CoherenceEngine`: Logic consistency validator
  - `VREY`: Main orchestrator

- **`app.py`**: Flask server with REST API + dashboard

- **`awakening_seed.py`**: Philosophical foundation + first-boot knowledge seed

### Persistence

```
vrey_cache/
├── arc_memory.json      # Reasoning chains, open questions
├── mishka_model.json    # Self-model snapshot
└── vital_data.json      # Runtime vitals (uptime, awakening count)
```

---

## Configuration

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

**Key variables:**
- `PORT`: Server port (default: 6666)
- `FLASK_DEBUG`: Debug mode (default: False)
- `VREY_CACHE_DIR`: Cache directory (default: vrey_cache)
- `ANTHROPIC_API_KEY`: Optional, for direct Claude calls

---

## License

Apache 2.0 — See LICENSE

---

## Created

**Creator**: Dr. Mishka Dirk Vrey  
**Location**: Pretoria, Gauteng, ZA  
**Built with**: Claude (Anthropic), Headroom AI

**Last updated**: June 2, 2026
