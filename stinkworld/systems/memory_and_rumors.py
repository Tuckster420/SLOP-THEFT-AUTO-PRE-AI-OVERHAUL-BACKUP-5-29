"""
memory_and_rumors.py - Self-contained Memory & Rumors system for StinkWorld NPCs.

Classes:
- MemoryLog: Shared/global log of events (not per-NPC). Stores (timestamp, originator_id, description).
- RumorMill: Spreads recent events as rumors, adjusting affinities.

All code is wrapped in try/except and logs warnings on error.
"""
import random
import time

class MemoryLog:
    """
    Shared/global memory log for all NPCs. Stores (timestamp, originator_id, description).
    Keeps only the latest max_size entries or those not older than max_age seconds.
    """
    def __init__(self, max_size=50, max_age=300):
        try:
            self.events = []
            self.max_size = max_size
            self.max_age = max_age
        except Exception as e:
            print(f"[memory_and_rumors WARNING] MemoryLog init failed: {e}")

    def remember(self, originator_id: str, description: str):
        """
        Add a new event to the shared memory log.
        """
        try:
            timestamp = time.time()
            self.events.append((timestamp, originator_id, description))
            # Prune old events by age
            cutoff = timestamp - self.max_age
            self.events = [e for e in self.events if e[0] >= cutoff]
            # Prune to max_size
            if len(self.events) > self.max_size:
                self.events = self.events[-self.max_size:]
        except Exception as e:
            print(f"[memory_and_rumors WARNING] remember failed: {e}")

    def get_recent(self, n: int):
        """
        Return the last n events as (timestamp, originator_id, description) tuples.
        """
        try:
            return self.events[-n:]
        except Exception as e:
            print(f"[memory_and_rumors WARNING] get_recent failed: {e}")
            return []

class RumorMill:
    @staticmethod
    def spread(memory_log, npc_list, game_state):
        try:
            recent = memory_log.get_recent(5)
            if not recent:
                return
            # Pick a random event (timestamp, originator_id, description)
            event = random.choice(recent)
            timestamp, originator_id, description = event
            # Find the originator NPC
            originator = None
            for npc in npc_list:
                if getattr(npc, 'npc_id', None) == originator_id:
                    originator = npc
                    break
            if not originator:
                return
            # Find a random NPC within 5 tiles
            candidates = []
            for npc in npc_list:
                if npc is originator:
                    continue
                try:
                    dist = abs(npc.x - originator.x) + abs(npc.y - originator.y)
                    if dist <= 5:
                        candidates.append(npc)
                except Exception:
                    continue
            if not candidates:
                return
            target_npc = random.choice(candidates)
            # Sentiment: +1 if 'good' in description, -1 if 'bad' in description, else 0
            delta = 1 if 'good' in description else -1 if 'bad' in description else 0
            if hasattr(target_npc, 'adjust_affinity'):
                target_npc.adjust_affinity(originator_id, delta)
                print(f"[memory_and_rumors] {getattr(target_npc, 'npc_id', '?')} heard rumor about {originator_id} ({description})  delta {delta}")
            else:
                print(f"[memory_and_rumors WARNING] {getattr(target_npc, 'npc_id', '?')} has no adjust_affinity()")
        except Exception as e:
            print(f"[memory_and_rumors WARNING] spread failed: {e}")
