import pytest
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()

from src import NPClient, NPGenerateInfo

# Helper function to register an account and return info
async def do_register(client, gen):
    username = gen.gen_username()
    password = gen.gen_password()
    email = username + "@cevipsa.com"
    dob = gen.gen_dob()
    await client.register(username, password, email, dob=dob)

    return { 'username': username, 'password': password, 'email': email, 'dob': dob }

# Helper function to register an account and return info
async def do_create_pet(client, gen):
    pet_name = gen.gen_pet_name()
    pet_type = gen.gen_pet_type()
    await client.create_pet(pet_name, pet_type)

    return { 'pet_name': pet_name, 'pet_type': pet_type }

# Activates account
async def do_activate(client, gen, user_info):
    code = await client.get_activation_code(user_info['email'])
    await client.activate_code(code)

@pytest.mark.asyncio
async def test_client_get_activation_code():
    # Checks authentication
    client = NPClient()

    code = await client.get_activation_code(os.getenv('NP_TEST_EMAIL'))
    assert code == 'X956K4M'

    await client.close()

@pytest.mark.asyncio
async def test_client_register():
    # Registers
    client = NPClient()
    gen = NPGenerateInfo()

    # Pre-Testing
    user_info = await do_register(client, gen)
    await asyncio.sleep(1)
    
    # Testing
    assert await client.check_has_auth()

    print('test_client_register', user_info['username'], user_info['password'])

    await client.close()

@pytest.mark.asyncio
async def test_client_create_pet():
    client = NPClient()
    gen = NPGenerateInfo()

    # Pre-Testing
    user_info = await do_register(client, gen)
    await asyncio.sleep(1)

    # Testing
    pet_info = await do_create_pet(client, gen)
    await asyncio.sleep(1)

    # TODO: Check pet is created

    print('test_client_create_pet', user_info['username'], user_info['password'])

    await client.close()

@pytest.mark.asyncio
async def test_client_donate():
    client = NPClient()
    gen = NPGenerateInfo()

    # Pre-Testing
    user_info = await do_register(client, gen)
    await asyncio.sleep(1)

    # Testing
    await client.donate(2000)
    await asyncio.sleep(1)
    pet_info = await do_create_pet(client, gen)
    await asyncio.sleep(1)

    # Verify
    np = await client.get_np()
    assert np == 500

    print('test_client_donate', user_info['username'], user_info['password'])

    await client.close()

@pytest.mark.asyncio
async def test_client_activates():
    client = NPClient()
    gen = NPGenerateInfo()

    # Pre-Testing
    user_info = await do_register(client, gen)
    await asyncio.sleep(1)
    pet_info = await do_create_pet(client, gen)
    await asyncio.sleep(12)

    # Testing
    await do_activate(client, gen, user_info)
    await asyncio.sleep(1)

    # TODO: Check activated

    print('test_client_register', user_info['username'], user_info['password'])

    await client.close()

@pytest.mark.asyncio
async def test_client_newbie_pack():
    client = NPClient()
    gen = NPGenerateInfo()

    # Pre-Testing
    user_info = await do_register(client, gen)
    await asyncio.sleep(1)
    pet_info = await do_create_pet(client, gen)
    await asyncio.sleep(7)
    await do_activate(client, gen, user_info)
    await asyncio.sleep(1)

    # Testing
    await client.claim_newbie_pack()
    await asyncio.sleep(1)

    # TODO: Check have items

    print('test_client_newbie_pack', user_info['username'], user_info['password'])

    await client.close()

@pytest.mark.asyncio
async def test_client_trudy():
    client = NPClient()
    gen = NPGenerateInfo()

    # Pre-Testing
    user_info = await do_register(client, gen)
    await asyncio.sleep(1)
    pet_info = await do_create_pet(client, gen)
    await asyncio.sleep(12)
    await do_activate(client, gen, user_info)
    await asyncio.sleep(1)
    await client.claim_newbie_pack()
    await asyncio.sleep(1)

    # Testing
    await client.claim_trudy()
    await asyncio.sleep(12)

    # Veryify
    np = await client.get_np()
    assert np > 2500

    print('test_client_trudy', user_info['username'], user_info['password'])

    await client.close()