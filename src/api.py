import asyncio
from dotenv import load_dotenv
load_dotenv()

from .client import NPClient, NPGenerateInfo

class NPAPI:
    def __init__(self):
        self.clients = []
    
    async def donate(self):
        # Registers
        client = NPClient()
        gen = NPGenerateInfo()

        username = gen.gen_username()
        password = gen.gen_password()
        email = username + '@mocvn.com'
        dob = gen.gen_dob()
        await client.register(username, password, email, dob=dob)
        # print('Registered')

        # Creates pet
        pet_name = gen.gen_pet_name()
        await client.create_pet(pet_name)

        # Donates
        # for i in range(5):
        await client.donate(2500)
        # await client.get_items()
        # print('Donated')

        await client.close()
    
    async def donate_run(self):
        for i in range(1000000):
            tasks = []
            for j in range(40):
                try:
                    tasks.append(self.donate())
                except Exception:
                    print('Failed...')
            await asyncio.gather(*tasks)
            print((i+1)*40, 'completed.')
