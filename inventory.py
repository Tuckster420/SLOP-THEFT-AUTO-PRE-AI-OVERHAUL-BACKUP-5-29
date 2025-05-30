from typing import Dict, List, Optional


class Inventory:
    """
    Manages the player's inventory and equipped items.
    """
    def __init__(self):
        self.items: List[Item] = []
        self.equipped: Dict[str, Optional[Item]] = {
            "head": None,
            "hands": None,
            "body": None,
            "feet": None
        }

    def add_item(self, item: Item) -> None:
        """
        Adds an item to the inventory.
        """
        self.items.append(item)

    def remove_item(self, item: Item) -> bool:
        """
        Removes an item from the inventory if it exists.
        Returns True if successful, False otherwise.
        """
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def use_item(self, item: Item) -> bool:
        """
        Uses an item (e.g., consumes a healing item).
        Returns True if successful, False otherwise.
        """
        if item not in self.items:
            return False

        if item.type == "healing":
            # Example: Apply healing effect
            print(f"Used {item.name} to restore {item.properties.get('healing_amount', 0)} health.")
            self.remove_item(item)
            return True

        # Add other item type logic here
        return False

    def equip_item(self, item: Item, slot: str) -> bool:
        """
        Equips an item to a specified slot (e.g., "hands").
        Returns True if successful, False otherwise.
        """
        if item not in self.items or not item.equippable or slot not in self.equipped:
            return False

        # Unequip any item in the slot first
        if self.equipped[slot] is not None:
            self.unequip_item(slot)

        self.equipped[slot] = item
        self.remove_item(item)
        return True

    def unequip_item(self, slot: str) -> bool:
        """
        Unequips an item from a specified slot.
        Returns True if successful, False otherwise.
        """
        if slot not in self.equipped or self.equipped[slot] is None:
            return False

        item = self.equipped[slot]
        self.add_item(item)
        self.equipped[slot] = None
        return True

    def get_equipped(self, slot: str) -> Optional[Item]:
        """
        Returns the equipped item in the specified slot, or None if empty.
        """
        return self.equipped.get(slot, None)

    def get_item_description(self, item: Item) -> str:
        """
        Returns a formatted description of the item for UI tooltips.
        """
        return f"{item.name}\nType: {item.type}\n{item.description}"

    def get_inventory_items(self) -> List[Item]:
        """
        Returns a list of all items in the inventory for UI display.
        """
        return self.items

    def get_equipped_items(self) -> Dict[str, Optional[Item]]:
        """
        Returns a dictionary of equipped items for UI display.
        """
        return self.equipped

    def __str__(self) -> str:
        """
        Returns a string representation of the inventory and equipped items.
        """
        inventory_str = "Inventory:\n" + "\n".join([str(item) for item in self.items])
        equipped_str = "\n\nEquipped:\n" + "\n".join(
            [f"{slot}: {item.name if item else 'None'}" for slot, item in self.equipped.items()]
        )
        return inventory_str + equipped_str


# Example usage for integration with the UI:
# 1. Import the Inventory class and items:
# from inventory import Inventory
# from items import ITEMS

# 2. Create and populate an inventory:
# player_inventory = Inventory()
# player_inventory.add_item(ITEMS["Bandage"])
# player_inventory.add_item(ITEMS["Knife"])

# 3. Access inventory data for UI display:
# inventory_items = player_inventory.get_inventory_items()
# equipped_items = player_inventory.get_equipped_items()

# 4. Handle UI interactions:
# player_inventory.use_item(selected_item)  # Triggered by UI
# player_inventory.equip_item(selected_item, "hands")  # Triggered by UI 