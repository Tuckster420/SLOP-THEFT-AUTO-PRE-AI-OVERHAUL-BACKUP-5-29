from typing import Dict
from stinkworld.utils.debug import debug_log

INJURY_TYPES = {
    "bruise": {"severity": 1, "heal_turns": 30, "bleed": False, "limp": False},
    "sprain": {"severity": 2, "heal_turns": 100, "bleed": False, "limp": True},
    "fracture": {"severity": 3, "heal_turns": 200, "bleed": False, "limp": True},
    "cut": {"severity": 2, "heal_turns": 60, "bleed": True, "limp": False},
    "deep wound": {"severity": 3, "heal_turns": 150, "bleed": True, "limp": True},
}

BODY_PARTS = [
    "head", "left arm", "right arm", "left leg", "right leg", "chest", "abdomen"
]

def add_injury(entity, part: str, injury_type: str):
    """Add an injury to an entity."""
    if not hasattr(entity, "injuries"):
        entity.injuries = {}
    entity.injuries[part] = {
        "type": injury_type,
        "turns": INJURY_TYPES[injury_type]["heal_turns"],
        "bleed": INJURY_TYPES[injury_type]["bleed"],
        "limp": INJURY_TYPES[injury_type]["limp"],
        "severity": INJURY_TYPES[injury_type]["severity"],
    }

def process_injuries(entity):
    """Process injury effects each turn (bleeding, limping, healing)."""
    bleeding = False
    limping = False
    hp_loss = 0
    if not hasattr(entity, "injuries"):
        entity.injuries = {}
    for part, info in list(entity.injuries.items()):
        info["turns"] -= 1
        if info["bleed"]:
            bleeding = True
            hp_loss += info["severity"]
        if info["limp"]:
            limping = True
        if info["turns"] <= 0:
            del entity.injuries[part]
    if bleeding:
        entity.hp = max(0, entity.hp - hp_loss)
    return bleeding, limping, hp_loss