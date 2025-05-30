class Item:
    """
    Represents an item in the game with attributes like name, type, and description.
    """
    def __init__(self, name, item_type, description, equippable=False, **kwargs):
        self.name = name
        self.type = item_type
        self.description = description
        self.equippable = equippable
        self.properties = kwargs  # Additional properties like healing amount, damage, etc.

    def __str__(self):
        return f"{self.name} ({self.type}): {self.description}"


# Example items for the game
ITEMS = {
    # Healing items
    "Bandage": Item(
        name="Bandage",
        item_type="healing",
        description="A basic bandage that restores 10 health.",
        healing_amount=10
    ),
    "Medkit": Item(
        name="Medkit",
        item_type="healing",
        description="A medkit that restores 50 health.",
        healing_amount=50
    ),

    # Weapons/Tools
    "Knife": Item(
        name="Knife",
        item_type="weapon",
        description="A sharp knife for self-defense.",
        equippable=True,
        damage=15
    ),
    "Crowbar": Item(
        name="Crowbar",
        item_type="weapon",
        description="A sturdy crowbar for prying and smashing.",
        equippable=True,
        damage=25
    ),

    # Crafting materials
    "Scrap Metal": Item(
        name="Scrap Metal",
        item_type="material",
        description="Used for crafting tools and weapons."
    ),
    "Cloth": Item(
        name="Cloth",
        item_type="material",
        description="Used for crafting bandages and clothing."
    ),
    "Stick": Item(
        name="Stick",
        item_type="material",
        description="A simple stick, useful for crafting."
    ),
    "Stone": Item(
        name="Stone",
        item_type="material",
        description="A small stone, useful for crafting."
    ),

    # Utility items
    "Flashlight": Item(
        name="Flashlight",
        item_type="utility",
        description="A basic flashlight for seeing in the dark.",
        equippable=True
    ),
    "Lockpick": Item(
        name="Lockpick",
        item_type="utility",
        description="A set of lockpicks for opening locked doors."
    ),
    "Rope": Item(
        name="Rope",
        item_type="utility",
        description="A sturdy rope for climbing or tying things."
    ),

    # Miscellaneous
    "Key": Item(
        name="Key",
        item_type="misc",
        description="A mysterious key. It might unlock something important."
    ),
    "Coin": Item(
        name="Coin",
        item_type="misc",
        description="A shiny coin. Maybe it has some value."
    ),
    "Note": Item(
        name="Note",
        item_type="misc",
        description="A crumpled note with illegible writing."
    )
} 