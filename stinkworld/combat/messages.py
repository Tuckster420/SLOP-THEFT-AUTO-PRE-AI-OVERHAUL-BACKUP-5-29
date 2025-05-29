from stinkworld.utils.debug import debug_log
import random

def npc_combat_message(damage, part, npc_hp, name, fatal=False, knocked_out=False):
    if fatal:
        msg = f"You deal a fatal blow to {name}'s {part}! {name} dies instantly!"
    elif knocked_out:
        msg = f"You knock {name} out with a hit to the {part}!"
    elif damage >= 6:
        msg = f"You smash {name} in the {part}! Bone cracks loudly!"
    elif damage >= 4:
        msg = f"You strike {name}'s {part} with great force! It's badly injured."
    elif damage == 3:
        msg = f"You hit {name} in the {part}. It bruises deeply."
    elif damage == 2:
        msg = f"You punch {name}'s {part}. It's a solid blow."
    elif damage == 1:
        msg = f"You graze {name}'s {part}."
    else:
        msg = f"You miss {name}'s {part}."
    return msg

def npc_attack_player(npc, player):
    part = random.choice(["head", "arm", "leg", "chest", "abdomen"])
    attack = npc.strength + random.randint(0, npc.speed)
    defense = player.defense + random.randint(0, player.speed)
    damage = max(0, attack - defense + random.randint(-1, 2))
    if damage > 0:
        player.hp -= damage
        msg = f"{npc.name} hits you in the {part} for {damage} damage!"
    else:
        msg = f"{npc.name} swings at you but misses!"
    return msg

def car_combat_message(damage, part, car_hp):
    if damage >= 6:
        msg = f"You smash the car's {part}! Metal and glass fly everywhere!"
    elif damage >= 4:
        msg = f"You dent the car's {part} with a loud crunch!"
    elif damage == 3:
        msg = f"You leave a big scratch on the car's {part}."
    elif damage == 2:
        msg = f"You scuff the car's {part}."
    elif damage == 1:
        msg = f"You barely mark the car's {part}."
    else:
        msg = f"You swing at the car's {part}, but nothing happens."
    if car_hp <= 0:
        msg += " The car is wrecked and won't move again!"
    return msg

"""Combat message templates."""

COMBAT_MESSAGES = {
    'attack': {
        'normal': [
            "{attacker} hits {defender} for {damage} damage!",
            "{attacker} strikes {defender}, dealing {damage} damage!",
            "{attacker} lands a hit on {defender} for {damage} damage!"
        ],
        'critical': [
            "Critical hit! {attacker} deals {damage} damage to {defender}!",
            "{attacker} lands a devastating blow on {defender} for {damage} damage!",
            "A powerful strike! {attacker} hits {defender} for {damage} damage!"
        ],
        'miss': [
            "{attacker}'s attack misses {defender}!",
            "{defender} dodges {attacker}'s attack!",
            "{attacker} fails to hit {defender}!"
        ]
    },
    'status': {
        'knockout': [
            "{target} has been knocked out!",
            "{target} falls unconscious!",
            "{target} collapses from their injuries!"
        ],
        'death': [
            "{target} has been defeated!",
            "{target} falls to the ground, lifeless!",
            "{target} succumbs to their injuries!"
        ],
        'heal': [
            "{target} recovers {amount} health!",
            "{target} feels better, healing {amount} HP!",
            "{target} regains {amount} health points!"
        ],
        'revive': [
            "{target} regains consciousness!",
            "{target} staggers back to their feet!",
            "{target} wakes up, ready to fight again!"
        ]
    },
    'taunt': [
        "Come on, is that all you've got?",
        "You'll have to do better than that!",
        "I've had worse paper cuts!",
        "My grandmother hits harder than you!"
    ],
    'surrender': [
        "I yield! Please stop!",
        "Enough! I give up!",
        "You win! I surrender!",
        "No more! I submit!"
    ]
}

def get_combat_message(category, subcategory, **kwargs):
    """Get a random combat message from the specified category."""
    if category in COMBAT_MESSAGES and subcategory in COMBAT_MESSAGES[category]:
        message = random.choice(COMBAT_MESSAGES[category][subcategory])
        return message.format(**kwargs)
    return "Combat continues..."