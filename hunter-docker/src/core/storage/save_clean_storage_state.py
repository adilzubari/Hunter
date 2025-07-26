import json
import asyncio

async def save_clean_storage_state(context, path="auth.json"):
    """Save only cookies and localStorage to a JSON file, stripping tabs/session data."""
    state = await context.storage_state()
    clean_state = {
        "cookies": state.get("cookies", []),
        "origins": [
            {
                "origin": o["origin"],
                "localStorage": o.get("localStorage", [])
            }
            for o in state.get("origins", [])
        ]
    }
    with open(path, "w") as f:
        json.dump(clean_state, f)
