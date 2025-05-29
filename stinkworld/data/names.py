"""Name data for NPCs."""

from stinkworld.utils.debug import debug_log
import random

FIRST_NAMES_FEM = [
    "Aaren","Abbey","Abby","Ada","Adah","Adaline","Adan","Adda","Addie","Adela",
    "Adelaide","Adele","Adeline","Adella","Adelle","Adina","Adora","Adrian","Adriana","Adrienne",
    "Afton","Agatha","Agnes","Aida","Aileen","Aimee","Ainsley","Aisha","Aja","Alaina",
    "Alana","Alanna","Alayna","Alberta","Aleah","Alejandra","Alexa","Alexandra","Alexis","Alice",
    "Alicia","Alina","Alisa","Alisha","Alison","Alissa","Allie","Allison","Ally","Alma"
]

FIRST_NAMES_MASC = [
    "Aaron","Adam","Adrian","Aidan","Aiden","Alan","Albert","Alec","Alex","Alexander",
    "Alfred","Ali","Allen","Alvin","Amir","Andre","Andrew","Andy","Angel","Anthony",
    "Antonio","Arthur","Asher","Austin","Avery","Axel","Barry","Ben","Benjamin","Bennett",
    "Billy","Blake","Brad","Bradley","Brady","Brandon","Brendan","Brian","Bruce","Bryan",
    "Caleb","Cameron","Carl","Carlos","Carter","Casey","Charles","Charlie","Chase","Chris"
]

FIRST_NAMES_NB = [
    "Alex","Avery","Bailey","Blair","Casey","Charlie","Dakota","Devon","Drew","Eden",
    "Emerson","Finley","Harley","Hayden","Jamie","Jesse","Jordan","Kai","Kendall","Lane",
    "Logan","Morgan","Parker","Quinn","Reese","Riley","River","Rowan","Sage","Skyler"
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","AdAMS","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts"
]

def random_name(gender=None):
    """Return a random full name. Gender can be 'M', 'F', or 'NB'. If None, pick randomly."""
    if gender is None:
        gender = random.choice(['M', 'F', 'NB'])
    if gender == 'M':
        first = random.choice(FIRST_NAMES_MASC)
    elif gender == 'F':
        first = random.choice(FIRST_NAMES_FEM)
    else:
        first = random.choice(FIRST_NAMES_NB)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"