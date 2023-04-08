import pytest
import os
import asyncio

from src import NPClient, NPGenerateInfo

@pytest.mark.asyncio
async def test_client_get_activation_code():
    # Checks authentication
    client = NPClient()

    code = await client.get_activation_code(os.getenv('NP_TEST_EMAIL'))
    assert code == 'X956K4M'

    await client.close()

@pytest.mark.asyncio
async def test_client_register():
    from dotenv import load_dotenv
    load_dotenv()

    # Registers
    client = NPClient()
    gen = NPGenerateInfo()

    username = gen.gen_username()
    password = gen.gen_password()
    email = username + '@mocvn.com'
    dob = gen.gen_dob()
    await client.register(username, password, email, dob=dob)

    # Creates pet
    pet_name = gen.gen_pet_name()
    await client.create_pet(pet_name)

    await client.donate(2500)
    await client.get_np()

    # # Uses auth code from email
    # await asyncio.sleep(7)
    # code = await client.get_activation_code(email)
    # await client.activate_code(code)

    # # Claims newbie pack
    # await asyncio.sleep(1)
    # await client.claim_newbie_pack()

    # # Claims trudy
    # await asyncio.sleep(1)
    # await client.claim_trudy()
    # await asyncio.sleep(10)

    print(username, password)

    await client.close()

