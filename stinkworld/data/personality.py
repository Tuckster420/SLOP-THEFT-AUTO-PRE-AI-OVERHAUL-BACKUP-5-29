from stinkworld.utils.debug import debug_log

"""Personality data for NPCs."""

PERSONALITY_FLAVOR = {
    'friendly': {
        'greeting': "Hey there, friend!",
        'talk': "I love meeting new people!",
        'farewell': "Take care, buddy!"
    },
    'grumpy': {
        'greeting': "What do you want?",
        'talk': "*grumbles*",
        'farewell': "Finally, some peace..."
    },
    'timid': {
        'greeting': "Oh! Um... hi...",
        'talk': "*nervously fidgets*",
        'farewell': "I should... um... go..."
    },
    'aggressive': {
        'greeting': "You looking for trouble?",
        'talk': "*cracks knuckles*",
        'farewell': "Better watch your back."
    },
    'forgiving': {
        'greeting': "Welcome, welcome!",
        'talk': "Everyone deserves a second chance.",
        'farewell': "No hard feelings!"
    },
    'grudgeful': {
        'greeting': "I remember what you did.",
        'talk': "*glares intensely*",
        'farewell': "I won't forget this."
    },
    'chatty': {
        'greeting': "Oh my gosh, hi! How are you? I was just thinking about...",
        'talk': "*talks non-stop*",
        'farewell': "And then I... oh, you're going? Okay, bye!"
    },
    'quiet': {
        'greeting': "*nods*",
        'talk': "...",
        'farewell': "*waves silently*"
    }
}