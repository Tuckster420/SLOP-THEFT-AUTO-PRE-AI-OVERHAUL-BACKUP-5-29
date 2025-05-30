import warnings
from collections import defaultdict
import logging

# Set up logging
logger = logging.getLogger('npc_ai')

# Track already warned NPC IDs
_missing_npc_warnings = defaultdict(bool)

# Default NPC definition template
DEFAULT_NPC_TEMPLATE = {
    "behavior": "idle",
    "speed": 1.0,
    "dialogue": ["..."],
    "texture": "default_npc.png",
    "job": "unemployed",
    "home": [0, 0],
    "family": [],
    "relationships": {}
}

def load_npc_ai(npc_id, npc_definitions):
    """
    Load AI for an NPC with graceful fallback to defaults.
    Args:
        npc_id: The ID of the NPC to load
        npc_definitions: Dictionary of all NPC definitions
    Returns:
        The NPC definition (either specific or default)
    """
    # Try to get specific definition
    npc_def = npc_definitions.get(npc_id)
    
    # Fallback to default if not found
    if npc_def is None:
        if not _missing_npc_warnings[npc_id]:
            logger.warning(
                f"NPC definition not found for ID: {npc_id}. Generating default definition."
            )
            _missing_npc_warnings[npc_id] = True
        
        # Create a complete default definition
        npc_def = DEFAULT_NPC_TEMPLATE.copy()
        npc_def["id"] = npc_id  # Preserve original ID
        npc_def["name"] = f"Unknown NPC {npc_id}"
    
    return npc_def 