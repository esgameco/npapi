"""
 _____          _       __                _ _ 
/__   \___  ___| |_    /__\ __ ___   __ _(_) |
  / /\/ _ \/ __| __|  /_\| '_ ` _ \ / _` | | |
 / / |  __/\__ \ |_  //__| | | | | | (_| | | |
 \/   \___||___/\__| \__/|_| |_| |_|\__,_|_|_|
 
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

from src import NPClient, NPGenerateInfo, PetCreationError, RegisterError, NPEmailManager
from .test_client import do_register, do_create_pet

@pytest.mark.asyncio
async def test_code_activation():
    gen = NPGenerateInfo()
    client = NPClient()

    await do_register(client, gen)
    await asyncio.sleep(1)
    await do_create_pet(client, gen)
    await asyncio.sleep(10)
    code = await gen.email_manager.get_code(client.email)
    await client.activate_code(code)
    
    assert await client.check_activated()

    print('test_code_activation', client.username, client.password)

    await client.close()