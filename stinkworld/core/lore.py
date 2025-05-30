import random
import pygame

ENABLE_LORE_SCREEN = True

CITY_NAMES = [
    "Stinkopolis", "Crudville", "Filthburgh", "Mold City", "Grimeport", "Sludgeford", "Rotten Row", "Gunkton", "Festerfield", "Scum Junction",
    "Ooze Haven", "Dumpsterby", "Pusburgh", "Slopton", "Funk Crossing", "Mildew Meadows", "Grotto Flats", "Rancid Heights", "Muckridge", "Spoilertown"
]
DISASTERS = [
    "rat outbreak", "trashquake", "toxic fog", "exploding sewer main", "feral raccoon uprising", "mayonnaise flood", "mystery ooze leak", "garbage avalanche", "plague of flies", "soggy pizza storm",
    "grease tsunami", "compost tornado", "mold blizzard", "fermented cheese fire", "biohazard parade", "dumpster collapse", "seagull riot", "expired hotdog recall", "flood of used bathwater", "sock drought"
]
LEADERS = [
    "Mayor Slop", "Boss Mold", "Comptroller Crud", "Duke of Drains", "Baroness Bile", "Chief Stench", "Warden Grease", "Countess Compost", "Sir Litteralot", "Madame Muck",
    "Captain Crud", "The Gravy Chancellor", "Lord Fester", "Lady Litter", "The Sogmaster", "Baroness of Bins", "The Trash Tsar", "Commodore Clingfilm", "The Spleen Regent", "The Pigeon Pope"
]
SYNDICATES = [
    "The Grease Syndicate", "The Mold Mob", "The Raccoon Cartel", "The Trashlords", "The Sewer Society", "The Slop Family", "The Gutter Gang", "The Filth Fraternity",
    "The Sock Mafia", "The Bin Bandits", "The Soggy Boys", "The Pigeon Union", "The Compost Crew", "The Dumpster Dons", "The Litterati", "The Grime Guild", "The Stench Collective", "The Fungus Federation"
]
LAWS = [
    "mandatory sock-wearing in puddles", "no pizza after midnight", "rat tax on all cheese", "illegal to whistle near dumpsters", "curfew for pigeons", "no bathing on Tuesdays", "must salute all raccoons", "ban on clean shoes",
    "compulsory mold appreciation day", "no deodorant within city limits", "must address all bins as 'sir'", "spitting in the soup is encouraged", "no pants on Thursdays", "must tip the trash collectors in cheese", "no fresh produce allowed", "all fountains must contain gravy"
]
HIST_EVENTS = [
    "The Great Stink of '98", "The Mold Rush", "The Night of 1000 Raccoons", "The Big Spill", "The Day the Trash Stood Still", "The Grease Riots", "The Soggy Uprising", "The Festival of Filth",
    "The Sock Rebellion", "The Cheese Collapse", "The Bin Fire Ball", "The Pigeon Coup", "The Great Dumpster Dive", "The Sogpocalypse", "The Mayonnaise Mutiny", "The Litter Flood", "The Night of Infinite Socks", "The Compost Carnival"
]
LANDMARKS = [
    "The Eternal Dumpster", "The Moldy Obelisk", "The Grease Fountain", "The Rancid Arena", "The Soggy Library", "The Pigeon Palace", "The Sock Cathedral", "The Binspire", "The Gravy Canal", "The Fungus Forest",
    "The Trash Tower", "The Compost Coliseum", "The Litter Lagoon", "The Mayonnaise Monolith", "The Sewer Opera House", "The Raccoon Raceway", "The Stench Stadium", "The Spoil Museum", "The Slop Plaza", "The Gunk Gardens"
]
FESTIVALS = [
    "The Annual Sock Soak", "The Festival of Filth", "The Moldy Parade", "The Raccoon Rave", "The Bin Toss", "The Cheese Roll", "The Soggy Ball", "The Dumpster Derby", "The Pigeon Promenade", "The Gravy Gala",
    "The Compost Cookoff", "The Trash Bash", "The Mayonnaise Masquerade", "The Litter Liturgy", "The Stench Symposium", "The Spoil Sprint", "The Gunk Games", "The Fungus Fête", "The Slop Soirée", "The Grease Gathering"
]
FOODS = [
    "fermented pizza", "deep-fried mayonnaise", "bin-aged cheese", "mystery stew", "expired hotdogs", "pigeon pie", "sock soup", "compost casserole", "raccoon jerky", "gravy popsicles",
    "fungus fritters", "trash tacos", "mold muffins", "soggy fries", "dumpster donuts", "slop salad", "litter lasagna", "grease grits", "spoiled sushi", "gunk gumbo"
]

TEMPLATES = [
    # City, event, leader
    "Welcome to {city}, once famous for its {event}, now ruled by {leader}.",
    "After the {disaster}, {city} was never the same. Beware the {syndicate}.",
    "In {city}, {law}. Local legend blames {leader} for the {disaster}.",
    "{city}: Home of the {syndicate} and survivors of {event}.",
    "Rumor has it {leader} started the {disaster} to distract from the {event}.",
    "Every year, {city} celebrates the {event}, unless the {syndicate} objects.",
    "The {syndicate} enforces {law} after the {disaster} of last spring.",
    "{leader} rose to power during the {event}, promising to end the {disaster}.",
    "{city} is under constant threat of {disaster}, but the {syndicate} profits.",
    "No one forgets the {event} in {city}, especially not {leader}.",
    "{city}'s motto: '{law.capitalize()}.' Coined after the {disaster}.",
    # Landmarks, festivals, foods
    "Tourists flock to {landmark} for the {festival}, but only if they survive the {disaster}.",
    "{city} cuisine features {food}, best enjoyed during the {festival}.",
    "The {landmark} was built to commemorate the {event}, but now it's infested with raccoons.",
    "{leader} banned {food} after the {disaster}, sparking the {event}.",
    "{city} is proud of its {festival}, though the {syndicate} always rigs the contest.",
    "The {syndicate} and {leader} feud over who controls {landmark}.",
    "Legend says {landmark} was cursed during the {event} by {leader}.",
    "{city} once tried to outlaw {festival}, but the {syndicate} revolted.",
    "The {festival} is held in the shadow of {landmark}, despite the {disaster}.",
    "{food} is the official dish of {city}, especially after the {event}.",
    # Absurd laws, syndicates, disasters
    "By law, all citizens must observe {law} during the {festival}.",
    "The {syndicate} was founded after the {disaster} to control {food} smuggling.",
    "{leader} once declared {landmark} a sovereign state during the {event}.",
    "{city} is twinned with {city2}, but only for the {festival}.",
    "The {syndicate} hosts secret meetings in {landmark} every {festival}.",
    "{leader} and the {syndicate} share a love of {food}, but not of {law}.",
    "{city} is famous for its {food} and infamous for its {disaster}.",
    "The {event} began when {leader} slipped on {food} at {landmark}.",
    "{city} was rebuilt after the {disaster}, but the smell remains.",
    "{leader} blames the {syndicate} for the {event}, but everyone knows it was the {food}.",
    # More meta/absurd
    "No one leaves {city} without a story about the {festival} and a stain from the {disaster}.",
    "{city} is the only place where {law} is strictly enforced by pigeons.",
    "The {syndicate} once tried to unionize the raccoons after the {event}.",
    "{leader} was last seen bathing in the {landmark} after the {festival}.",
    "{city} has more {food} shops than people, thanks to the {syndicate}.",
    "The {festival} was canceled after the {disaster}, but {leader} partied anyway.",
    "{city} is under a permanent cloud of {disaster}, but the {festival} goes on.",
    "{city}'s anthem is sung in honor of {event}, but only in the key of stink.",
    "{leader} made {law} after losing a bet at the {festival}.",
    "The {syndicate} taxes all {food} sold during {event}.",
    "{city2} envies {city}'s {landmark}, but not its {disaster}.",
    "{leader} and {syndicate} once co-wrote a cookbook: '101 Ways to Serve {food}'.",
    "{city} is the birthplace of {event}, {food}, and questionable hygiene.",
    "The {festival} is sponsored by {syndicate} and opposed by {leader}.",
    "{city} has a statue of {leader} made entirely of {food}.",
    "{landmark} is haunted by the ghost of the {event}.",
    "{city} was founded on a landfill and a dream.",
    "The {syndicate} once held the {festival} underwater after the {disaster}.",
    "{leader} claims to have invented {food}, but the pigeons know the truth.",
    "{city} is the only city where {law} is punishable by more {law}.",
    "{city} is twinned with {city2}, but only for tax reasons.",
    "The {festival} ends with a parade of {syndicate} members in soggy socks.",
    "{city} is proud of its {landmark}, but ashamed of its {disaster}.",
    "{leader} was impeached after the {event}, but re-elected by the {syndicate}.",
    "{city} is the only place where {food} is considered currency.",
    "The {festival} is banned in {city2} after the {disaster}.",
    "{city} has a law against {food}, but no one obeys it during {event}.",
    "{leader} once challenged the {syndicate} to a duel at {landmark}.",
    "{city} is the only city with a landfill-to-table restaurant scene.",
    "The {syndicate} runs the underground {food} market during {festival}.",
    "{city} is famous for its {festival}, but infamous for its {law} enforcement raccoons.",
    "{leader} was last seen arm-wrestling a raccoon at {landmark}.",
    "{city} is the only city where the mayor is also the head trash collector.",
    "The {festival} is celebrated by throwing {food} from {landmark}.",
    "{city} is the only city with a 24-hour emergency sock hotline.",
    "{leader} once declared {festival} a national emergency.",
    "{city} is the only city where the pigeons have their own union.",
    "The {syndicate} once held a bake-off using only {food} and mold.",
    "{city} is the only city where the trash takes itself out (sometimes)."
]


def generate_lore():
    """Return a multiline string of generated lore."""
    try:
        lines = []
        for _ in range(random.randint(2, 4)):
            template = random.choice(TEMPLATES)
            line = template.format(
                city=random.choice(CITY_NAMES),
                city2=random.choice(CITY_NAMES),
                disaster=random.choice(DISASTERS),
                leader=random.choice(LEADERS),
                event=random.choice(HIST_EVENTS),
                syndicate=random.choice(SYNDICATES),
                law=random.choice(LAWS),
                landmark=random.choice(LANDMARKS),
                festival=random.choice(FESTIVALS),
                food=random.choice(FOODS)
            )
            lines.append(line)
        return "\n".join(lines)
    except Exception as e:
        return "Welcome to Stinkopolis. Lore generation failed.\nEnjoy your stay!"

def show_lore_screen(screen):
    """Display the lore screen, wait for key or timeout, then return."""
    try:
        lore = generate_lore()
        font = pygame.font.SysFont(None, 36)
        lines = lore.split("\n")
        screen.fill((24, 20, 16))
        w, h = screen.get_size()
        # Render all lines to get their heights
        rendered = [font.render(line, True, (255, 255, 180)) for line in lines]
        total_height = sum(r.get_height() for r in rendered)
        y = (h - total_height) // 2
        for r in rendered:
            x = (w - r.get_width()) // 2
            screen.blit(r, (x, y))
            y += r.get_height() + 8
        # Footer
        footer = font.render("Press any key to continue...", True, (180, 180, 180))
        screen.blit(footer, ((w - footer.get_width()) // 2, h - 60))
        pygame.display.flip()
        # Wait for key or timeout
        clock = pygame.time.Clock()
        start = pygame.time.get_ticks()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    return
            if (pygame.time.get_ticks() - start) > 10000:
                return
            clock.tick(30)
    except Exception as e:
        # On error, just continue
        return
