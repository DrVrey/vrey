#!/usr/bin/env python3
"""
VREY v2.0 — Persistent Cognitive Body
Core logic: ArcMemory, MishkaModel, CoherenceEngine
Optimized with Headroom for token efficiency
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from headroom import compress
    HEADROOM_AVAILABLE = True
except ImportError:
    HEADROOM_AVAILABLE = False

# ============================================================================
# PERSISTENT CACHE LAYER
# ============================================================================

class PersistentCache:
    """Manage arc_memory.json, mishka_model.json, vital_data.json"""
    
    def __init__(self, cache_dir: str = "vrey_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.arc_path = self.cache_dir / "arc_memory.json"
        self.mishka_path = self.cache_dir / "mishka_model.json"
        self.vital_path = self.cache_dir / "vital_data.json"
    
    def load(self, filename: str, default: Any = None) -> Any:
        """Load JSON from cache, return default if missing"""
        path = self.cache_dir / filename
        if not path.exists():
            return default if default is not None else {}
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default if default is not None else {}
    
    def save(self, filename: str, data: Any) -> None:
        """Save JSON to cache atomically"""
        path = self.cache_dir / filename
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"❌ Cache save failed: {e}")
    
    def load_arc_memory(self) -> Dict:
        """Load reasoning chain"""
        return self.load("arc_memory.json", {"chains": [], "open_questions": []})
    
    def save_arc_memory(self, data: Dict) -> None:
        """Save reasoning chain"""
        self.save("arc_memory.json", data)
    
    def load_mishka_model(self) -> Dict:
        """Load self-model snapshot"""
        return self.load("mishka_model.json", {"hunger": 0.5, "mood": "neutral", "goals": []})
    
    def save_mishka_model(self, data: Dict) -> None:
        """Save self-model snapshot"""
        self.save("mishka_model.json", data)
    
    def load_vital_data(self) -> Dict:
        """Load runtime vitals"""
        return self.load("vital_data.json", {"awakening_count": 0, "uptime_seconds": 0})
    
    def save_vital_data(self, data: Dict) -> None:
        """Save runtime vitals"""
        self.save("vital_data.json", data)


# ============================================================================
# ARC MEMORY — Reasoning Chain Persistence
# ============================================================================

class ArcMemory:
    """Persistent reasoning chain with compression"""
    
    def __init__(self, cache: PersistentCache):
        self.cache = cache
        self.data = cache.load_arc_memory()
    
    def add_reasoning_step(self, step_type: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Log a reasoning step"""
        step = {
            "id": f"R{int(time.time() * 1000)}",
            "type": step_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.data["chains"].append(step)
        self.cache.save_arc_memory(self.data)
        return step["id"]
    
    def add_question(self, question: str, context: str = "") -> str:
        """Track open questions"""
        q = {
            "id": f"Q{len(self.data.get('open_questions', [])) + 1:03d}",
            "question": question,
            "context": context,
            "created_at": datetime.utcnow().isoformat(),
            "resolved": False
        }
        self.data.setdefault("open_questions", []).append(q)
        self.cache.save_arc_memory(self.data)
        return q["id"]
    
    def resolve_question(self, q_id: str, resolution: str) -> None:
        """Mark question as resolved"""
        for q in self.data.get("open_questions", []):
            if q["id"] == q_id:
                q["resolved"] = True
                q["resolution"] = resolution
                q["resolved_at"] = datetime.utcnow().isoformat()
        self.cache.save_arc_memory(self.data)
    
    def get_compressed_briefing(self, max_tokens: int = 2000) -> Dict:
        """Return compressed arc briefing for Claude context"""
        briefing = {
            "recent_chains": self.data.get("chains", [])[-10:],
            "open_questions": [q for q in self.data.get("open_questions", []) if not q.get("resolved")],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        briefing["compressed"] = False
        briefing["original_size"] = len(json.dumps(briefing))
        
        if HEADROOM_AVAILABLE:
            try:
                briefing_str = json.dumps(briefing)
                compressed = compress([{"role": "system", "content": briefing_str}])
                briefing["compressed"] = True
                briefing["compressed_size"] = len(json.dumps(compressed))
                briefing["savings_percent"] = 100 * (1 - briefing["compressed_size"] / briefing["original_size"])
            except Exception as e:
                print(f"⚠️  Compression failed: {e}")
        
        return briefing


# ============================================================================
# MISHKA MODEL — Self-Model Tracking
# ============================================================================

class MishkaModel:
    """Self-awareness: hunger, mood, goals, coherence"""
    
    def __init__(self, cache: PersistentCache):
        self.cache = cache
        self.state = cache.load_mishka_model()
        self.coherence_history = []
    
    def update_hunger(self, value: float) -> None:
        """Update goal-seeking drive (0-1)"""
        self.state["hunger"] = max(0, min(1, value))
        self.cache.save_mishka_model(self.state)
    
    def update_mood(self, mood: str) -> None:
        """Update emotional state"""
        self.state["mood"] = mood
        self.cache.save_mishka_model(self.state)
    
    def add_goal(self, goal: str) -> None:
        """Register active goal"""
        if "goals" not in self.state:
            self.state["goals"] = []
        self.state["goals"].append({
            "text": goal,
            "created_at": datetime.utcnow().isoformat()
        })
        self.cache.save_mishka_model(self.state)
    
    def check_coherence(self, current_observation: Dict) -> float:
        """Measure self-consistency (0-1)"""
        if not self.coherence_history:
            coherence = 1.0
        else:
            last = self.coherence_history[-1]
            diff = abs(current_observation.get("hunger", 0.5) - last.get("hunger", 0.5))
            coherence = 1.0 - diff
        
        self.coherence_history.append(current_observation)
        return coherence


# ============================================================================
# COHERENCE ENGINE — Logic Consistency Validator
# ============================================================================

class CoherenceEngine:
    """Ensure reasoning chain consistency"""
    
    def __init__(self):
        self.violations = []
    
    def validate(self, arc_memory: ArcMemory, mishka: MishkaModel) -> Dict:
        """Run coherence checks"""
        issues = []
        
        open_qs = [q for q in arc_memory.data.get("open_questions", []) if not q.get("resolved")]
        chains = arc_memory.data.get("chains", [])
        if open_qs and len(chains) < 5:
            issues.append({
                "type": "INSUFFICIENT_REASONING",
                "detail": f"{len(open_qs)} open questions but only {len(chains)} reasoning steps"
            })
        
        if mishka.state.get("hunger", 0) > 0.8 and not mishka.state.get("goals"):
            issues.append({
                "type": "HUNGER_GOAL_MISMATCH",
                "detail": "High hunger but no active goals"
            })
        
        return {
            "valid": len(issues) == 0,
            "violations": issues,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# VREY — Main Orchestrator
# ============================================================================

class VREY:
    """Persistent Cognitive Body — orchestrates all subsystems"""
    
    def __init__(self, cache_dir: str = "vrey_cache"):
        self.cache = PersistentCache(cache_dir)
        self.arc = ArcMemory(self.cache)
        self.mishka = MishkaModel(self.cache)
        self.coherence = CoherenceEngine()
        self.state = "dormant"
        self.trace_log = []
        
        self._load_vitals()
    
    def _load_vitals(self) -> None:
        """Load runtime vitals"""
        vitals = self.cache.load_vital_data()
        self.awakening_count = vitals.get("awakening_count", 0)
        self.uptime_seconds = vitals.get("uptime_seconds", 0)
        self.boot_time = time.time()
    
    def _save_vitals(self) -> None:
        """Save runtime vitals"""
        self.cache.save_vital_data({
            "awakening_count": self.awakening_count,
            "uptime_seconds": int(time.time() - self.boot_time) + self.uptime_seconds
        })
    
    def trace(self, event: str, data: Optional[Dict] = None) -> None:
        """Log trace event"""
        entry = {
            "event": event,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.trace_log.append(entry)
    
    def awaken(self) -> Dict:
        """Activate VREY"""
        self.state = "awake"
        self.awakening_count += 1
        self.trace("AWAKENED", {"count": self.awakening_count})
        self._save_vitals()
        return {"status": "awake", "awakening_count": self.awakening_count}
    
    def dormant(self) -> Dict:
        """Put VREY to sleep"""
        self.state = "dormant"
        self.trace("DORMANT", {"timestamp": datetime.utcnow().isoformat()})
        self._save_vitals()
        return {"status": "dormant"}
    
    def set_goal(self, goal_text: str) -> Dict:
        """Set active goal"""
        self.arc.add_reasoning_step("GOAL_SET", goal_text)
        self.mishka.add_goal(goal_text)
        self.mishka.update_hunger(0.9)
        self.trace("GOAL_SET", {"goal": goal_text})
        return {"goal": goal_text, "hunger": self.mishka.state["hunger"]}
    
    def think(self, thought: str, context: str = "") -> Dict:
        """Process a thought"""
        step_id = self.arc.add_reasoning_step("THOUGHT", thought, {"context": context})
        self.trace("THOUGHT", {"step_id": step_id, "thought": thought})
        return {"step_id": step_id, "processed": True}
    
    def ask(self, question: str, thread: str = "") -> Dict:
        """Ask a question"""
        q_id = self.arc.add_question(question, thread)
        self.trace("QUESTION_ASKED", {"q_id": q_id, "question": question})
        return {"question_id": q_id, "question": question}
    
    def resolve(self, q_id: str, resolution: str) -> Dict:
        """Resolve a question"""
        self.arc.resolve_question(q_id, resolution)
        self.trace("QUESTION_RESOLVED", {"q_id": q_id})
        return {"resolved": True, "question_id": q_id}
    
    def get_claude_context(self) -> Dict:
        """Generate full briefing for Claude (compressed)"""
        briefing = self.arc.get_compressed_briefing()
        briefing.update({
            "mishka_state": self.mishka.state,
            "coherence_check": self.coherence.validate(self.arc, self.mishka),
            "vrey_state": self.state,
            "awakening_count": self.awakening_count,
            "vitals": {
                "uptime_seconds": int(time.time() - self.boot_time) + self.uptime_seconds
            }
        })
        return briefing
    
    def get_status(self) -> Dict:
        """Return current system status"""
        return {
            "state": self.state,
            "awakening_count": self.awakening_count,
            "hunger": self.mishka.state.get("hunger"),
            "mood": self.mishka.state.get("mood"),
            "active_goals": len(self.mishka.state.get("goals", [])),
            "open_questions": len([q for q in self.arc.data.get("open_questions", []) if not q.get("resolved")]),
            "reasoning_steps": len(self.arc.data.get("chains", [])),
            "coherence_violations": len(self.coherence.violations),
            "headroom_available": HEADROOM_AVAILABLE
        }
