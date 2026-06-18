import json
from backend.curriculum import MODULES


def seed_curriculum(output_path=None):
    """Export curriculum data as JSON for external use or seed a database."""
    data = {
        "modules": MODULES,
        "total": len(MODULES)
    }
    if output_path:
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
    return data
