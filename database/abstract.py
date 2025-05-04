class AbstractDatabase:
    def connect(self):
        raise NotImplementedError

    def list_inventory(self):
        raise NotImplementedError

    def use_item(self, item_id, quantity):
        raise NotImplementedError

    def place_order(self, item_id, quantity):
        raise NotImplementedError
