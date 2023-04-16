"""
 _____          _       ___ _ _            _   
/__   \___  ___| |_    / __\ (_) ___ _ __ | |_ 
  / /\/ _ \/ __| __|  / /  | | |/ _ \ '_ \| __|
 / / |  __/\__ \ |_  / /___| | |  __/ | | | |_ 
 \/   \___||___/\__| \____/|_|_|\___|_| |_|\__|
                                               
"""

import pytest
import os
import asyncio
import aiohttp
import pickle
import http
import json


from dotenv import load_dotenv
load_dotenv()

from fake_useragent import UserAgent

from src import NPClient, NPGenerateInfo, PetCreationError, RegisterError

# Helper function to register an account and return info
async def do_register(client, gen):
    for i in range(3):
        try:
            # username = gen.gen_username()
            # password = gen.gen_password()
            # email = username + "@cevipsa.com"
            # dob = gen.gen_dob()
            user_info = await gen.gen_user_info()
            await client.register(**user_info)

            return user_info
        except RegisterError as e:
            print(e)
            await asyncio.sleep(2)
    return None

# Helper function to register an account and return info
async def do_create_pet(client, gen):
    for i in range(10):
        try:
            pet_info = gen.gen_pet_info()
            await client.create_pet(**pet_info)
            return pet_info
        except PetCreationError as e:
            print(e)
            await asyncio.sleep(2)
    return None

# Activates account
async def do_activate(client, gen, user_info):
    try:
        code = await client.get_activation_code(user_info['email'])
        await client.activate_code(code)
        return True
    except Exception as e:
        print(e)
    return False


@pytest.mark.asyncio
async def test_client_get_activation_code():
    # Checks authentication
    client = NPClient()

    code = await client.get_activation_code(os.getenv('NP_TEST_EMAIL'))
    assert code == 'X956K4M'

    await client.close()

@pytest.mark.asyncio
async def test_aiohttp():
    gen = NPGenerateInfo()

    username = os.getenv('NP_TEST_USERNAME')
    password = os.getenv('NP_TEST_PASSWORD')
    proxy = os.getenv('PROXY_WEBSHARE')
    ua = UserAgent()

    async with aiohttp.ClientSession(headers={
        'User-Agent': ua.chrome
    }) as session:
        res = await session.post('https://www.neopets.com/login.phtml', data={
            'username': username,
            'password': password,
            'return_format': 'json'
        })
        jar_p = pickle.dumps(res.cookies, protocol=3)
        new_jar = pickle.loads(jar_p)

    async with aiohttp.ClientSession(headers={
        'User-Agent': ua.chrome,
    }, cookies=new_jar) as session:
        res = await session.post('https://www.neopets.com/process_donation.phtml', data={
            'donation': '100'
        })
        print(res)

    # print('test_client_cookie', pre_client.username, pre_client.password)
    print('test_client_cookie', username, password)

@pytest.mark.asyncio
async def test_login():
    gen = NPGenerateInfo()
    
    # Testing
    client = NPClient()
    username = os.getenv('NP_TEST_USERNAME')
    password = os.getenv('NP_TEST_PASSWORD')
    await client.login(username, password)

    js = await client.serialize_cookie_jar(client.query.client.cookie_jar)
    cookies = await client.deserialize_cookie_jar(json.loads(js))

    client_new = NPClient(cookies=cookies)
    
    # await client_new.cookie_test()
    donate_amount = 6
    init_np = await client_new.get_np()
    await client_new.donate(6)
    fin_np = await client_new.get_np()

    assert init_np-fin_np == donate_amount

    # print('test_client_cookie', pre_client.username, pre_client.password)
    print('test_client_cookie', username, password)

    await client.close()

@pytest.mark.asyncio
async def test_client_register():
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
    await asyncio.sleep(2)

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
    # await client.login(user_info['username'], user_info['password'])
    # await asyncio.sleep(1)
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
    assert user_info is not None
    await asyncio.sleep(1)
    pet_info = await do_create_pet(client, gen)
    assert pet_info is not None
    await asyncio.sleep(12)
    activated = await do_activate(client, gen, user_info)
    assert activated
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