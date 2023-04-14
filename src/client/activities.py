from .client import NPClient
from .helpers import NPHelpers

class NPActivityClient(NPClient):
    def __init__(self, username: str = None, password: str = None, id: str = None, cookies: str = None, user_agent: str = None, proxy: str = None, proxy_manager=None):
        super().__init__(username, password, id, cookies, user_agent, proxy, proxy_manager)
    
    async def anchor_management(self):
        """Anchor Management Minigame
        
        
        """
        res = self.query.get('https://www.neopets.com/pirates/anchormanagement.phtml')
        msg = await self._get_text(res)

        if NPHelpers.contains('form-fire-cannon', msg):
            action = NPHelpers.search('<input name="action" type="hidden" value="(.*?)">', msg)[1]
            self.query.post('https://www.neopets.com/pirates/anchormanagement.phtml', params={
                'action': action
            })
            if NPHelpers.contains('prize-item-name', msg):
                prize = NPHelpers.search('<span class="prize-item-name">(.*?)</span>', msg)[1]
                print(f'Blasted krawken; got {prize}')
            else:
                print('Blasted krawken; got unknown prize')
        elif NPHelpers.contains('safe from sea monsters for one day', msg):
            print('Already did anchor management.')
        else:
            print("Couldn't find anchor management.")

    async def daily_puzzle(self):
        """TODO https://www.jellyneo.net/?go=dailypuzzle"""
        
    async def rich_slorg(self):
        """Rich Slorg Minigame
        
        Avg
        """
        pass

    async def wishing_well(self):
        """Wishing Well Minigame
        
        7 wishes / day 
        21 np / wish

        (small chance of big $)
        """
        # GET https://www.neopets.com/wishing.phtml
        # POST https://www.neopets.com/process_wishing.phtml donation: 21 wish: Graffiti Skateboard
        pass

    async def neggsweeper(self):
        """Neggsweeper Minigame TODO
        
        (3k/day)
        """
        pass

    async def cliffhanger(self):
        """Cliffhanger Minigame TODO
        
        (1500 NP/day)
        """