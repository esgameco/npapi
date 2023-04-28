from .auth import NPAuthRunner
from .inventory import NPInventoryRunner
from .main import NPMainRunner

class NPClientRunner:
    """
        NPClientRunner

        Performs the functions of a client
    """
    def __init__(self, client_db=None) -> None:
        self.client_db = client_db
        self.auth_runner = NPAuthRunner(client_db)
        # self.inventory_runner
    

