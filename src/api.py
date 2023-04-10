import asyncio
from dotenv import load_dotenv
load_dotenv()

from .client import NPClient, NPGenerateInfo

class NPAPI:
    def __init__(self):
        self.clients = []
    
    async def donate(self):
        # Registers
        try:
            client = NPClient()
            gen = NPGenerateInfo()

            username = gen.gen_username()
            password = gen.gen_password()
            email = username + '@mocvn.com'
            dob = gen.gen_dob()
            await client.register(username, password, email, dob=dob)
            # print('Registered')

            # # Creates pet
            # await asyncio.sleep(2)
            # pet_name = gen.gen_pet_name()
            # pet_type = gen.gen_pet_type()
            # await client.create_pet(pet_name, pet_type)

            # Donates
            for i in range(25):
                await asyncio.sleep(0.5)
                await client.donate(100)
            # await client.get_items()
            # print('Donated')
        except Exception:
            print('Failed...')

        print(username, password)

        await client.close()
    
    async def donate_run(self):
        for i in range(1000000):
            tasks = []
            for j in range(40):
                tasks.append(self.donate())
            await asyncio.gather(*tasks)
            print((i+1)*40, 'completed.')
