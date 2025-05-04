from .fake_driver import FakeDatabase

def get_database_driver(config):
    if config["USE_FAKE_DB"]:
        return FakeDatabase()
