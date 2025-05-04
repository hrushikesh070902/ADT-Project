def get_inventory(db):
    return db.list_inventory()

def use_item(db, item_id, quantity):
    db.use_item(item_id, quantity)

def place_order(db, item_id, quantity):
    db.place_order(item_id, quantity)
