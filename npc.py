class NPC:
    def __init__(self, npc_id, npc_definitions):
        from npc_ai_loader import load_npc_ai
        from npc_definitions import DEFAULT_NPC_DEFINITION
        
        self.definition = load_npc_ai(npc_id, npc_definitions)
        self.load_behavior()
    
    def load_behavior(self):
        """Load behavior based on definition with fallback to idle."""
        behavior_type = self.definition.get("behavior", "idle")
        
        if behavior_type == "wander":
            from ai.wander import WanderAI
            self.ai = WanderAI(self)
        else:  # Default to idle behavior
            from ai.idle import IdleAI
            self.ai = IdleAI(self)
        
        # Set movement speed (with fallback to default)
        self.speed = self.definition.get("speed", DEFAULT_NPC_DEFINITION["speed"]) 