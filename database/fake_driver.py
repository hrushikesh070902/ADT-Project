from .abstract import AbstractDatabase

class FakeDatabase(AbstractDatabase):
    def __init__(self):
        self.inventory = {
            1: {"name": "Gloves", "stock": 100, "reorder_level": 50},
            2: {"name": "Syringe", "stock": 40, "reorder_level": 60},
            3: {"name": "IV Set", "stock": 30, "reorder_level": 25}
        }

    def connect(self):
        return True

    def list_inventory(self):
        return self.inventory

    def use_item(self, item_id, quantity):
        if item_id in self.inventory:
            self.inventory[item_id]["stock"] -= quantity

    def place_order(self, item_id, quantity):
        print(f"Fake order placed: {quantity} of {self.inventory[item_id]['name']}")
