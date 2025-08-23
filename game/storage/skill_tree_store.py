import json, os
from copy import deepcopy

DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "skill_nodes.json")
SAVES_DIR  = os.path.join(os.path.dirname(__file__), "..", "..", "saves")

def _save_path(profile_id: str) -> str:
    os.makedirs(SAVES_DIR, exist_ok=True)
    return os.path.join(SAVES_DIR, f"skill_tree_profile_{profile_id}.json")

def load_catalog() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_player_state(profile_id: str) -> dict:
    path = _save_path(profile_id)
    if not os.path.exists(path):
        return {"profile_id": profile_id, "nodes": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_player_state(profile_id: str, state: dict) -> None:
    path = _save_path(profile_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def build_merged_nodes(profile_id: str) -> tuple[list[dict], dict]:
    """
    Returns (merged_nodes, state). merged_nodes is the catalog with
    'owned' and 'node_level' injected from player state.
    """
    catalog = load_catalog()
    state   = load_player_state(profile_id)
    progress = state.get("nodes", {})

    merged = []
    for n in catalog:
        m = deepcopy(n)
        p = progress.get(n["id"], {})
        # defaults
        m["owned"] = bool(p.get("owned", n.get("core", False)))
        m["node_level"] = int(p.get("node_level", 1 if n.get("core", False) else 0))
        m["max_level"]  = int(m.get("max_level", 1))
        merged.append(m)
    return merged, state

def update_progress_from_nodes(state: dict, nodes: list[dict]) -> dict:
    """
    Writes current 'owned' and 'node_level' of nodes back into state.
    """
    progress = state.setdefault("nodes", {})
    for n in nodes:
        nid = n["id"]
        progress[nid] = {
            "owned": bool(n.get("owned", False)),
            "node_level": int(n.get("node_level", 0))
        }
    return state
