from stinkworld.utils.debug import debug_log
from stinkworld.entities.appearance import SKIN_TONES
import random

# Lists for biography generation
OCCUPATIONS = [
    "shopkeeper", "teacher", "office worker", "artist", "musician",
    "chef", "mechanic", "doctor", "lawyer", "student",
    "writer", "programmer", "athlete", "police officer", "firefighter",
    "librarian", "taxi driver", "journalist", "scientist", "entrepreneur"
]

LIFE_EVENTS = [
    "recently moved to the city",
    "lost their job",
    "got promoted",
    "won a small lottery",
    "survived a difficult illness",
    "graduated from university",
    "started their own business",
    "got married",
    "got divorced",
    "adopted a pet",
    "published a book",
    "learned to play an instrument",
    "traveled around the world",
    "inherited a house",
    "changed careers"
]

INTERESTS = [
    "reading", "painting", "music", "cooking", "gardening",
    "photography", "sports", "video games", "hiking", "dancing",
    "collecting stamps", "astronomy", "chess", "fishing", "woodworking",
    "martial arts", "yoga", "bird watching", "writing poetry", "meditation"
]

PHYSICAL_TRAITS = [
    "tall and lean",
    "short and stocky",
    "average height and build",
    "muscular",
    "slender",
    "broad-shouldered",
    "petite",
    "athletic",
    "round and jolly",
    "lanky"
]

PERSONALITY_DESCRIPTIONS = {
    'friendly': "They have a warm and welcoming demeanor that puts others at ease.",
    'grumpy': "They tend to be irritable and often complain about minor inconveniences.",
    'timid': "They are shy and prefer to avoid confrontation or attention.",
    'aggressive': "They have a forceful personality and aren't afraid to speak their mind.",
    'forgiving': "They are quick to forgive and rarely hold grudges.",
    'grudgeful': "They have a long memory for perceived slights and insults.",
    'chatty': "They love to talk and can strike up a conversation with anyone.",
    'quiet': "They are reserved and prefer to listen rather than speak."
}

def generate_biography(appearance):
    """Generate a detailed biography for an NPC based on their appearance."""
    occupation = random.choice(OCCUPATIONS)
    life_event = random.choice(LIFE_EVENTS)
    interests = random.sample(INTERESTS, k=random.randint(1, 3))
    # Use actual appearance fields for description
    hair_style = appearance.get('hair_style', 'short')
    hair_color = appearance.get('hair_color', 'brown')
    face_shape = appearance.get('face_shape', 'round')
    eye_type = appearance.get('eye_type', 'bright')
    clothes = appearance.get('clothes', 'casual')
    skin_tone = appearance.get('skin_tone', (224, 172, 105))
    vitiligo = appearance.get('vitiligo', 0.0)
    # Convert skin_tone tuple to a readable string using SKIN_TONES
    skin_tone_str = None
    for k, v in SKIN_TONES.items():
        if v == skin_tone:
            skin_tone_str = k.replace('_', ' ')
            break
    if not skin_tone_str:
        skin_tone_str = str(skin_tone)
    # Build the biography
    bio_parts = []
    bio_parts.append(f"A {face_shape} face, {eye_type} eyes, {hair_style} {hair_color} hair, wearing {clothes} clothes.")
    bio_parts.append(f"Skin tone: {skin_tone_str}.")
    if vitiligo and vitiligo > 0:
        bio_parts.append("Has visible vitiligo patches.")
    # Occupation
    bio_parts.append(f"Works as a {occupation}.")
    # Life event
    bio_parts.append(f"Recently {life_event}.")
    # Interests
    if len(interests) == 1:
        bio_parts.append(f"Enjoys {interests[0]}.")
    else:
        interests_str = ", ".join(interests[:-1]) + f" and {interests[-1]}"
        bio_parts.append(f"Interested in {interests_str}.")
    # Combine all parts
    biography = " ".join(bio_parts)
    
    return biography