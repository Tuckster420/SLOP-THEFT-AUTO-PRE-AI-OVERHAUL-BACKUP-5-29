from stinkworld.utils.debug import debug_log

"""Conversation data for NPCs."""

CONVERSATIONS = [
    {
        "prompt": "How's your day going?",
        "responses": [
            "Great, thanks for asking!",
            "Could be better...",
            "Just another day in StinkWorld."
        ]
    },
    {
        "prompt": "Have you heard any interesting news?",
        "responses": [
            "Nothing much happening around here.",
            "Actually, I did hear something...",
            "I try not to listen to gossip."
        ]
    },
    {
        "prompt": "What do you think about this neighborhood?",
        "responses": [
            "It's pretty nice, all things considered.",
            "Could use some cleaning up.",
            "I've seen better places."
        ]
    },
    {
        "prompt": "Do you know where I can find work?",
        "responses": [
            "The shops are always hiring.",
            "Try the industrial district.",
            "I hear there's good money in... less legal work."
        ]
    },
    {
        "prompt": "What's your favorite place around here?",
        "responses": [
            "The park is nice and peaceful.",
            "I like hanging out at the shops.",
            "My home is my favorite place."
        ]
    },
    {
        "prompt": "Have you seen anything suspicious lately?",
        "responses": [
            "Now that you mention it...",
            "I mind my own business.",
            "You might want to be careful around here."
        ]
    },
    {
        "prompt": "What do you do for fun?",
        "responses": [
            "I enjoy walking in the park.",
            "Shopping is my favorite pastime.",
            "Just trying to survive, really."
        ]
    },
    {
        "prompt": "How long have you lived here?",
        "responses": [
            "Born and raised here.",
            "Moved here recently.",
            "Long enough to know the place well."
        ]
    }
]

# Special conversation responses based on relationship level
RELATIONSHIP_RESPONSES = {
    'high': {
        'greeting': [
            "Hey, my friend!",
            "So good to see you!",
            "I was hoping to run into you!"
        ],
        'farewell': [
            "Take care, friend!",
            "See you soon!",
            "Don't be a stranger!"
        ]
    },
    'medium': {
        'greeting': [
            "Hello there.",
            "Nice to see you.",
            "How are you?"
        ],
        'farewell': [
            "Goodbye.",
            "Take care.",
            "Have a good one."
        ]
    },
    'low': {
        'greeting': [
            "What do you want?",
            "*grumbles*",
            "Oh, it's you."
        ],
        'farewell': [
            "Finally...",
            "Just leave me alone.",
            "*turns away*"
        ]
    }
}

# Combat-related dialogue
COMBAT_DIALOGUE = {
    'taunt': [
        "You're going to regret this!",
        "Is that all you've got?",
        "Come on, show me what you can do!",
        "You picked the wrong person to mess with!"
    ],
    'surrender': [
        "Okay, okay, I give up!",
        "Please, no more!",
        "I yield! I yield!",
        "You win, just stop!"
    ],
    'victory': [
        "That'll teach you!",
        "Don't mess with me!",
        "And stay down!",
        "Next time, think twice!"
    ],
    'defeat': [
        "Ugh... you got me...",
        "This isn't over...",
        "I'll remember this...",
        "*groans in pain*"
    ]
}

# Shop dialogue
SHOP_DIALOGUE = {
    'greeting': [
        "Welcome! Take a look around.",
        "What can I get for you?",
        "Looking for anything specific?"
    ],
    'farewell': [
        "Come back soon!",
        "Thanks for shopping!",
        "Have a great day!"
    ],
    'haggle': [
        "That's my final offer.",
        "I might be able to work something out...",
        "Quality comes at a price."
    ],
    'no_money': [
        "Sorry, no credit.",
        "Come back when you have the money.",
        "I can't give this away for free."
    ]
}