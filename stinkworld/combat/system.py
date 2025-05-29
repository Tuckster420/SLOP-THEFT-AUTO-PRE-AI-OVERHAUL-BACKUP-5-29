import random
from stinkworld.combat.injuries import BODY_PARTS, add_injury, process_injuries, INJURY_TYPES

def start_combat(game, npc):
    """Turn-based combat system with injury, bleeding, and limping."""
    player = game.player
    if not hasattr(player, "injuries"):
        player.injuries = {}
    if not hasattr(npc, "injuries"):
        npc.injuries = {}

    combat_over = False
    while not combat_over:
        # Process injuries for both
        p_bleed, p_limp, p_bleed_amt = process_injuries(player)
        n_bleed, n_limp, n_bleed_amt = process_injuries(npc)

        # Show HP and injuries
        status = (
            f"Your HP: {player.hp}/{player.max_hp} | "
            f"Injuries: {', '.join([f'{k}({v['type']})' for k,v in player.injuries.items()]) or 'None'}"
            f"{' | Bleeding!' if p_bleed else ''}{' | Limping!' if p_limp else ''}\n"
            f"{npc.name} HP: {npc.hp}/10 | "
            f"Injuries: {', '.join([f'{k}({v['type']})' for k,v in npc.injuries.items()]) or 'None'}"
            f"{' | Bleeding!' if n_bleed else ''}{' | Limping!' if n_limp else ''}"
        )
        game.show_message_and_wait(status)

        # Player turn
        actions = ["Punch", "Kick", "Targeted Attack", "Taunt", "Flee"]
        while True:
            choice = game.show_menu_and_wait("Choose your action:", actions)
            if actions[choice] == "Flee":
                game.message_to_show = "You run away!"
                combat_over = True
                break
            elif actions[choice] == "Targeted Attack":
                part_idx = game.show_menu_and_wait("Target which body part?", BODY_PARTS)
                target_part = BODY_PARTS[part_idx]
                attack_type = "targeted"
                break
            elif actions[choice] == "Taunt":
                taunts = [
                    "You're slower than a parked car!",
                    "Is that all you've got?",
                    "I've seen puddles with more fight than you!",
                    "You call that a punch? My grandma hits harder!",
                    "You're about as sharp as a marble!",
                    "Did you forget your brain at home today?",
                    "You're not even worth my time!",
                    "You look like you lost a fight with a mop!",
                    "I've met friendlier rats in the sewer!",
                    "You couldn't win a staring contest with a goldfish!",
                    "You fight like a dairy farmer!",
                    "Your breath could knock out a skunk!",
                    "I've seen bread with more backbone!",
                    "You look like you eat soup with a fork!",
                    "You're about as scary as a kitten in a tutu!",
                    "If brains were dynamite, you couldn't blow your nose!",
                    "You're the reason the gene pool needs a lifeguard!",
                    "You couldn't pour water out of a boot with instructions on the heel!",
                    "You're the human equivalent of a participation trophy!",
                    "If I wanted to hear from you, I'd rattle your cage!"
                ]
                taunt = random.choice(taunts)
                if not hasattr(npc, 'taunted') or not npc.taunted:
                    npc.strength = max(1, getattr(npc, 'strength', 5) - 2)
                    npc.defense = max(0, getattr(npc, 'defense', 2) - 1)
                    npc.taunted = True
                    debuff_msg = f"{npc.name}'s strength and defense are lowered!"
                else:
                    debuff_msg = f"{npc.name} is already demoralized."
                game.show_message_and_wait(f"You taunt {npc.name}: '{taunt}'\n{debuff_msg}")
                # Do not end turn, allow player to pick another action
                continue
            else:
                target_part = random.choice(BODY_PARTS)
                attack_type = actions[choice].lower()
                break

        # Calculate hit/miss/crit
        hit_roll = random.random()
        if hit_roll < 0.1:
            game.show_message_and_wait("You miss!")
        else:
            crit = hit_roll > 0.95
            base_damage = player.strength + random.randint(0, player.street_smarts)
            damage = base_damage * (2 if crit else 1)
            # Injury logic
            injury = None
            if attack_type == "targeted" or crit or damage > 6:
                # Choose injury type
                if damage > 12 or crit:
                    injury_type = random.choice(["fracture", "deep wound"])
                elif damage > 8:
                    injury_type = random.choice(["sprain", "cut"])
                else:
                    injury_type = "bruise"
                add_injury(npc, target_part, injury_type)
                injury = f" and cause a {injury_type} to their {target_part}!"
            npc.hp -= damage
            msg = f"You {attack_type} {npc.name}'s {target_part} for {damage} damage"
            if injury:
                msg += injury
            if crit:
                msg += " (Critical!)"
            game.show_message_and_wait(msg)
            if npc.hp <= 0:
                game.show_message_and_wait(f"{npc.name} is knocked out!")
                npc.is_knocked_out = True
                combat_over = True
                break

        # NPC turn (skip if KO)
        if npc.hp > 0:
            npc_action = random.choice(["punch", "kick", "target"])
            if npc_action == "target":
                npc_part = random.choice(BODY_PARTS)
                npc_msg = f"{npc.name} targets your {npc_part}!"
            else:
                npc_part = random.choice(BODY_PARTS)
                npc_msg = f"{npc.name} tries to {npc_action} you!"
            hit_roll = random.random()
            if hit_roll < 0.1:
                game.show_message_and_wait(npc_msg + " But they miss!")
            else:
                crit = hit_roll > 0.95
                base_damage = npc.strength + random.randint(0, npc.speed)
                damage = base_damage * (2 if crit else 1)
                injury = None
                if npc_action == "target" or crit or damage > 6:
                    if damage > 12 or crit:
                        injury_type = random.choice(["fracture", "deep wound"])
                    elif damage > 8:
                        injury_type = random.choice(["sprain", "cut"])
                    else:
                        injury_type = "bruise"
                    add_injury(player, npc_part, injury_type)
                    injury = f" and causes a {injury_type} to your {npc_part}!"
                player.hp -= damage
                msg = f"{npc.name} hits your {npc_part} for {damage} damage"
                if injury:
                    msg += injury
                if crit:
                    msg += " (Critical!)"
                game.show_message_and_wait(msg)
                if player.hp <= 0:
                    game.show_message_and_wait("You are knocked out!")
                    game.player_is_knocked_out = True
                    combat_over = True
                    break