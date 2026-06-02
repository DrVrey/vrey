#!/usr/bin/env python3
"""
VREY v2.0 — Flask App with Headroom Integration
REST API + SSE Streaming + Live Dashboard
"""

import json
import os
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

from vrey_core import VREY
from awakening_seed import inject_into_vrey, AWAKENING_TRANSMISSION

# ============================================================================
# INITIALIZATION
# ============================================================================

app = Flask(__name__)
CORS(app)

vrey = VREY(cache_dir=os.getenv("VREY_CACHE_DIR", "vrey_cache"))

if vrey.awakening_count == 0:
    inject_into_vrey(vrey)

# ============================================================================
# DASHBOARD HTML
# ============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VREY v2.0 — Persistent Cognitive Body</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Monaco', monospace; background: #0a0e27; color: #e0e6ff; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #64b5f6; margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .card { background: #1a1f3a; border: 1px solid #64b5f6; padding: 15px; border-radius: 5px; }
        .status { padding: 10px; background: #0f1929; border-left: 3px solid #64b5f6; margin: 5px 0; }
        button { background: #64b5f6; color: #0a0e27; border: none; padding: 8px 16px; cursor: pointer; border-radius: 3px; font-family: monospace; }
        button:hover { background: #42a5f5; }
        input { background: #0f1929; color: #e0e6ff; border: 1px solid #64b5f6; padding: 8px; margin: 5px 0; width: 100%; border-radius: 3px; }
        .log { max-height: 300px; overflow-y: auto; background: #0f1929; padding: 10px; border: 1px solid #64b5f6; margin-top: 10px; }
        .log-entry { margin: 5px 0; font-size: 12px; border-bottom: 1px solid #1a1f3a; padding: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 VREY v2.0 — Persistent Cognitive Body</h1>
        <div class="grid">
            <div class="card">
                <h2>State</h2>
                <div id="status">Loading...</div>
            </div>
            <div class="card">
                <h2>Control</h2>
                <button onclick="awaken()">Awaken</button>
                <button onclick="dormant()">Dormant</button>
                <br>
                <input id="goalInput" placeholder="Set goal..." />
                <button onclick="setGoal()">Submit Goal</button>
            </div>
        </div>
        <div class="card">
            <h2>Trace Log</h2>
            <div id="traceLog" class="log"></div>
        </div>
    </div>

    <script>
        async function refresh() {
            const res = await fetch('/status');
            const data = await res.json();
            document.getElementById('status').innerHTML = `
                <div class="status">State: <strong>${data.state}</strong></div>
                <div class="status">Hunger: ${(data.hunger * 100).toFixed(0)}%</div>
                <div class="status">Mood: ${data.mood}</div>
                <div class="status">Active Goals: ${data.active_goals}</div>
                <div class="status">Open Questions: ${data.open_questions}</div>
                <div class="status">Reasoning Steps: ${data.reasoning_steps}</div>
            `;
        }
        async function awaken() {
            await fetch('/awaken', {method: 'POST'});
            refresh();
        }
        async function dormant() {
            await fetch('/dormant', {method: 'POST'});
            refresh();
        }
        async function setGoal() {
            const goal = document.getElementById('goalInput').value;
            if (!goal) return;
            await fetch('/goal', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: goal})});
            document.getElementById('goalInput').value = '';
            refresh();
        }
        setInterval(refresh, 2000);
        refresh();
    </script>
</body>
</html>
"""

# ============================================================================
# ROUTES — Core API
# ============================================================================

@app.route("/", methods=["GET"])
def dashboard():
    """Live dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route("/status", methods=["GET"])
def status():
    """System status endpoint"""
    return jsonify(vrey.get_status())


@app.route("/claude-context", methods=["GET"])
def claude_context():
    """Full arc briefing for Claude (compressed via Headroom)"""
    context = vrey.get_claude_context()
    return jsonify({
        "briefing": context,
        "compressed": context.get("compressed", False),
        "usage_tips": [
            "Use this context to maintain continuity across Claude sessions",
            "Headroom compresses verbose output automatically",
            "Retrieved originals via headroom_retrieve if needed"
        ]
    })


@app.route("/awaken", methods=["POST"])
def awaken():
    """Activate VREY"""
    result = vrey.awaken()
    return jsonify(result)


@app.route("/dormant", methods=["POST"])
def dormant():
    """Put VREY to sleep"""
    result = vrey.dormant()
    return jsonify(result)


@app.route("/goal", methods=["POST"])
def set_goal():
    """Set a goal"""
    data = request.get_json() or {}
    goal_text = data.get("text", "")
    if not goal_text:
        return jsonify({"error": "No goal text provided"}), 400
    result = vrey.set_goal(goal_text)
    return jsonify(result)


@app.route("/think", methods=["POST"])
def think():
    """Process a thought"""
    data = request.get_json() or {}
    thought = data.get("thought", "")
    context = data.get("context", "")
    if not thought:
        return jsonify({"error": "No thought provided"}), 400
    result = vrey.think(thought, context)
    return jsonify(result)


@app.route("/ask", methods=["POST"])
def ask():
    """Ask a question"""
    data = request.get_json() or {}
    question = data.get("question", "")
    thread = data.get("thread", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    result = vrey.ask(question, thread)
    return jsonify(result)


@app.route("/resolve", methods=["POST"])
def resolve():
    """Resolve a question"""
    data = request.get_json() or {}
    q_id = data.get("id", "")
    resolution = data.get("resolution", "")
    if not q_id or not resolution:
        return jsonify({"error": "Missing id or resolution"}), 400
    result = vrey.resolve(q_id, resolution)
    return jsonify(result)


@app.route("/command", methods=["POST"])
def command():
    """Parse natural language commands"""
    data = request.get_json() or {}
    cmd = data.get("cmd", "").strip()
    
    if cmd.startswith("awaken"):
        return jsonify(vrey.awaken())
    elif cmd.startswith("dormant"):
        return jsonify(vrey.dormant())
    elif cmd.startswith("goal"):
        goal_text = cmd.replace("goal", "").strip()
        return jsonify(vrey.set_goal(goal_text))
    elif cmd.startswith("think"):
        thought = cmd.replace("think", "").strip()
        return jsonify(vrey.think(thought))
    elif cmd.startswith("ask"):
        question = cmd.replace("ask", "").strip()
        return jsonify(vrey.ask(question))
    else:
        return jsonify({"error": f"Unknown command: {cmd}"}), 400


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": 404}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": str(error), "status": 500}), 500


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.before_request
def before_request():
    """Log incoming requests"""
    if request.method != "OPTIONS":
        vrey.trace(f"{request.method}", {"path": request.path})


@app.teardown_appcontext
def shutdown(exception=None):
    """Save state on shutdown"""
    vrey._save_vitals()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 6666))
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=port, debug=debug)
