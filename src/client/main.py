import logging
import asyncio

from .activities import NPActivityClient
from .inventory_client import NPInventoryClient
from ..helpers import run_function
from .gen_info import NPGenerateInfo

class NPMainRunner(NPActivityClient, NPInventoryClient):
    def __init__(self, 
                 username: str=None, 
                 password: str=None, 
                 id: str=None, 
                 cookies: str=None, 
                 is_registered: bool=False,
                 is_activated: bool=False,
                 np: int=None,
                 client_type: str=None,
                 user_agent: str=None,
                 proxy: str=None, 
                 proxy_manager=None):
        super().__init__(username=username,
                         password=password, 
                         id=id, 
                         cookies=cookies,
                         is_registered=is_registered,
                         is_activated=is_activated,
                         np=np,
                         client_type=client_type,
                         user_agent=user_agent, 
                         proxy=proxy, 
                         proxy_manager=proxy_manager)
        self.gen = NPGenerateInfo(proxy=proxy)
    
    async def do_register(self, n: int=3):
        for i in range(n):
            try:
                user_info = await self.gen.gen_user_info()
                await self.register(**user_info)
                return user_info
            except Exception as e:
                logging.warning(f'(FeatureClient do_register) {e}')
                await asyncio.sleep(2)
        return None
    
    async def do_create_pet(self, n: int=3):
        for i in range(n):
            try:
                pet_info = self.gen.gen_pet_info()
                await self.create_pet(**pet_info)
                return pet_info
            except Exception as e:
                logging.warning(f'(FeatureClient do_create_pet) {e}')
                await asyncio.sleep(2)
        return None

    async def do_activate(self, n: int=3):
        for i in range(n):
            try:
                code = await self.gen.email_manager.get_code(self.email)
                await self.activate_code(code)
                return True
            except Exception as e:
                logging.warning(f'(FeatureClient do_activate) {e}')
                await asyncio.sleep(5)
        return None
    
    async def create_account(self, do_redeem:bool=True, do_activ:bool=True, get_np:bool=True):
        user_info = await self.do_register()

        if do_activ:
            await asyncio.sleep(2)
            pet_info = await self.do_create_pet()
            await asyncio.sleep(10)
            activated = await self.do_activate()
            await asyncio.sleep(2)

            if do_redeem:
                await self.claim_newbie_pack()

            if get_np:
                await self.get_np()

            return activated and pet_info and user_info
        
        return user_info

    async def do_dailies(self, paid:bool=False, safe:bool=True, cheap:bool=True, close:bool=False, minim:bool=False, random_wait:bool=True, client_db=None):
        results = {'username': self.username}

        if not (await self.check_cookie()):
            await self.login(random_wait=random_wait)

        # Free Dailies
        if minim:
            results['trudy'] = await run_function(self.claim_trudy())
            results['puzzle'] = await run_function(self.daily_puzzle(db=client_db))
        else:
            # Return if only want to do minimum activities
            results['slorg'] = await run_function(self.rich_slorg())
            results['anchor'] = await run_function(self.anchor_management())
            results['grumpy'] = await run_function(self.grumpy_king())
            results['potato'] = await run_function(self.potato_counter())
            results['plushie'] = await run_function(self.plushie())
            results['snowager'] = await run_function(self.snowager())
            results['tombola'] = await run_function(self.tombola())
            results['fruit'] = await run_function(self.fruit_machine())

            # Do Cheap Dailies
            if cheap:
                results['jelly'] = await run_function(self.jelly())
                results['springs'] = await run_function(self.healing_springs())
                results['lunar'] = await run_function(self.lunar_temple())
                results['omlette'] = await run_function(self.omlette())
                results['shrine'] = await run_function(self.shrine())

            # Do Unsafe Dailies
            if not safe:
                results['apple'] = await run_function(self.apple_bobbing())

            # Paid Dailies
            if paid:
                results['wishing'] = await run_function(self.wishing_well())
                results['lottery'] = await run_function(self.lottery())
                results['scratchcard'] = await run_function(self.scratchcard())

        if client_db is not None:
            await client_db.client_activity_db.update(self.username, results)

        # Close Client
        if close:
            await self.close()

        return results