#
#     ___ _ _            _   
#    / __\ (_) ___ _ __ | |_ 
#   / /  | | |/ _ \ '_ \| __|
#  / /___| | |  __/ | | | |_ 
#  \____/|_|_|\___|_| |_|\__|
#                          
#

import logging
import os
import hashlib
import json
import functools
import re
import time
import asyncio
import aiohttp
import random

from http.cookies import SimpleCookie, Morsel
from typing import Optional

from ..query import NPQuery
from ..exceptions import *
from ..helpers import retry_decorator, NPHelpers

# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

class NPClient:
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
        self.username = username
        self.password = password
        self.cookies = cookies
        self.is_registered = is_registered
        self.is_activated = is_activated
        self.np = np
        self.client_type = client_type
        self.query = NPQuery(proxy=proxy, proxy_manager=proxy_manager, cookies=cookies, user_agent=user_agent)
        self._id = id

    # Checks if registered or logged in (only to be used after registration or login)
    async def check_has_auth(self) -> bool:
        session_token = self.query.client.cookie_jar.filter_cookies('http://neopets.com/').get('neologin')
        return session_token is not None and len(session_token.value) > 10
    
    @retry_decorator()
    async def cookie_test(self):
        res = await self.query.get('https://www.neopets.com/island/tradingpost.phtml')
    
    async def basic_proxy_test(self):
        res = await self.query.get('https://www.neopets.com/index.phtml')
        if res:
            return res.status == 200
        return False

    # Logs in user
    @retry_decorator()
    async def login(self, username: str=None, password: str=None, set_details: bool=True, random_wait:bool=False, remove_cookies:bool=True, db=None) -> None:
        try:
            return await self._login(username=username,
                                    password=password,
                                    set_details=set_details,
                                    random_wait=random_wait,
                                    remove_cookies=remove_cookies,
                                    db=db)
        except Exception as e:
            print(f"(_login) {e}")
            await self.query.report_proxy()
            raise e
    
    async def _login(self, username: str=None, password: str=None, set_details: bool=True, random_wait:bool=False, remove_cookies:bool=True, db=None) -> None:
        if random_wait:
            await asyncio.sleep(random.randint(1,10)+random.random())
        if remove_cookies:
            self.query.client.cookie_jar.clear()

        if not username or not password:
            username = self.username
            password = self.password
        
        pre_res = await self.query.get('https://www.neopets.com/login/',
                                    referer='https://www.neopets.com/index.phtml')
        pre_msg = await NPHelpers.get_text(pre_res)

        ref_ck = re.search(r'<input type="hidden" name="_ref_ck" value="(.*?)">', pre_msg).group(1)

        res = await self.query.post('https://www.neopets.com/login.phtml', data={
            'username': username,
            'password': password,
            'return_format': 'json',
            '_ref_ck': ref_ck
        }, referer='https://www.neopets.com/login/')
        res_msg = await res.text()

        if not await self.check_has_auth():
            await self.query.report_proxy()
            raise LoginError('Login failed -- No Auth')

        if set_details:
            self.username = username
            self.password = password
            if db is not None:
                await db.update(self)
    
    # Gets json from messages
    def _get_json(self, msg: str) -> Optional[str]:
        """Gets json from aiohttp responses
        
        Will only return json if there is json to return
        """
        try:
            return json.loads(self._fix_text(msg))
        except Exception as e:
            logging.warning(f'(Client _get_json) {e}')
        return None
    
    # Fixes text from messages
    def _fix_text(self, msg: str) -> Optional[str]:
        """Fixes text in messages that contain / or \\"""
        try:
            return msg.replace('\n', '').replace('\t', '').replace('\r', '').replace('\\', '')
        except Exception as e:
            logging.warning(f'(Client _fix_text) {e}')
        return None
    
    # Gets text from http response
    async def _get_text(self, res) -> Optional[str]:
        """Returns fixed text of a response"""
        try:
            msg = await res.text()
            fixed = self._fix_text(msg)
            return fixed
        except Exception as e:
            logging.warning(f'(Client _get_text) {e}')
        return None

    # Registers for an account
    @retry_decorator()
    async def register(self, 
                       username: str, 
                       password: str, 
                       email: str, 
                       dob: tuple=(1, 1, 2000), 
                       security: dict=None,
                       set_details: bool=True) -> None:
        try:
            res = await self._register(username,
                                        password,
                                        email,
                                        dob,
                                        security,
                                        set_details)
            return res
        except Exception as e:
            await self.query.report_proxy()
            raise e
        
    # Registers for account
    async def _register(self, 
                       username: str, 
                       password: str, 
                       email: str, 
                       dob: tuple=(1, 1, 2000), 
                       security: dict=None,
                       set_details: bool=True) -> None:
        """Registers for an account"""

        ### Resister Page (get cookies) -- https://www.neopets.com/signup/index.phtml
        res_1 = await self.query.post('https://www.neopets.com/signup/index.phtml')

        ### Name Availability (get ssoreserve) -- https://www.neopets.com/signup/ajax.phtml
        res_2 = await self.query.post('https://www.neopets.com/signup/ajax.phtml', data={
            'method': "checkAvailability",
            'username':	username
        })
        res_2_msg = self._get_json(await res_2.text())
        if res_2_msg is None:
            await self.query.report_proxy()
            raise RegisterError('Register Error -- Failed at Step 2')

        ### Register Step 1 -- https://www.neopets.com/signup/ajax.phtml
        res_3 = await self.query.post('https://www.neopets.com/signup/ajax.phtml', data={
            'method': "step1_2020",
            'username':	username,
            'password1': password,
            'password2': password,
            'terms': "true",
            'month': dob['month'],
            'day': dob['day'],
            'year': dob['year'],
            'email1': email,
            'email2': email,
            'optinNeopets':	"false",
            'destination':	""
        })
        res_3_msg = self._get_json(await res_3.text())
        if res_3_msg is None:
            await self.query.report_proxy()
            raise RegisterError('Register Error -- Failed at Step 3')

        ### Register Index Page again (don't know why)
        res_4 = await self.query.post('https://www.neopets.com/signup/index.phtml')

        ### Register Step 2
        res_5 = await self.query.post('https://www.neopets.com/signup/ajax.phtml', data={
            'method': "step2_2020",
            'gender': security['gender'] if security else "M",
            'question1': security['question1'] if security else "1",
            'question2': security['question2'] if security else "5",
            'answer1': security['answer1'] if security else "SmithStreet",
            'answer2': security['answer2'] if security else "Janitor",
            'country': security['country'] if security else "US",
            'usState': security['usState'] if security else "CA"
        })
        res_5_msg = self._get_json(await res_5.text())
        if res_5_msg is None:
            await self.query.report_proxy()
            raise RegisterError('Register Error -- Failed at Step 5')

        res_6 = await self.query.post('https://www.neopets.com/reg/page4.phtml')

        if not await self.check_has_auth():
            await self.query.report_proxy()
            raise RegisterError('Register failed -- No Auth')
        
        if set_details:
            self.username = username
            self.password = password
            self.email = email
            self.dob = dob
            self.is_registered = True

    # Get activation code from email given (tempmail)
    async def get_activation_code(self, email: str) -> str:
        """Gets activation code from email
        
        To be depricated once email services are created
        """
        email_hash = hashlib.md5(email.encode()).hexdigest()
        res = await self.query.get(
            f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{email_hash}/",
            query_headers={
                "X-RapidAPI-Key": os.getenv('API_TEMPMAIL'),
                "X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
            })

        if res.status != 200:
            raise Exception
        
        js = await res.json()
        txt = js[0]['mail_text']
        index = txt.find('?code=')+6
        code = txt[index:index+7]

        return code

    # Activates email with code from email
    @retry_decorator(3, 1)
    async def activate_code(self, code: str) -> None:
        """Activates account with code from email"""
        res = await self.query.get(f'https://www.neopets.com/activate.phtml?code={code}')

        self.is_activated = await self.check_activated()
        if not self.is_activated:
            raise ActivationError('Activation Error -- Not Activated')

    # Checks whether the account is activated
    @retry_decorator()
    async def check_activated(self) -> bool:
        return await self._check_activated()

    async def _check_activated(self) -> bool:
        """Checks whether account is activated by using the trading post"""
        res = await self.query.get('https://www.neopets.com/island/tradingpost.phtml')
        
        msg = self._fix_text(await res.text()).lower()
        
        ac = 'activate your account' not in msg

        return ac

    @retry_decorator()
    async def create_pet(self, 
                         pet_name='', 
                         pet_type='jubjub', 
                         selected_pet_colour='green', 
                         selected_item='',
                         gender='male',
                         terrain='0',
                         likes='0',
                         meetothers='0',
                         pet_stats_set='1',
                         gen=None) -> None:
        return await self._create_pet(pet_name, 
                                    pet_type, 
                                    selected_pet_colour, 
                                    selected_item,
                                    gender,
                                    terrain,
                                    likes,
                                    meetothers,
                                    pet_stats_set,
                                    gen)

    # Creates pet (after register)
    async def _create_pet(self, 
                         pet_name='', 
                         pet_type='jubjub', 
                         selected_pet_colour='green', 
                         selected_item='',
                         gender='male',
                         terrain='0',
                         likes='0',
                         meetothers='0',
                         pet_stats_set='1',
                         gen=None) -> None:
        res_1 = await self.query.get('https://www.neopets.com/reg/page4.phtml', referer='https://www.neopets.com/index.phtml')
        msg_1 = await self._get_text(res_1)
        species = re.findall(r"<div class='pet_thumb' id='([a-z]*)_thumb_border' class=>", msg_1)
        if pet_type not in list(species):
            pet_type = random.choice(list(species))

        """Creates pet, name is required"""
        res_2 = await self.query.post('https://www.neopets.com/reg/process_createpet.phtml', data={
            'neopet_name':	pet_name,
            'selected_pet':	pet_type,
            'selected_pet_colour': selected_pet_colour,
            'selected_item': selected_item,
            'gender': gender,
            'terrain': terrain,
            'likes': likes,
            'meetothers': meetothers,
            'pet_stats_set': pet_stats_set,
        })

        if await self._get_text(res_2) != 'feedback|pet_success2':
            raise PetCreationError('Pet Creation Error -- No Success Message')
    
    # Donates selected amount (no auth required)
    @retry_decorator()
    async def donate(self, amount) -> None:
        """Donates to wishing well selected amount"""
        res = await self.query.post('https://www.neopets.com/process_donation.phtml', data={
            'donation': str(amount)
        })
    
    async def check_cookie(self) -> bool:
        try:
            res = await self.get_np()
            return True
        except Exception as e:
            print('(check_cookie)', e)
            return False

    # Gets current neopoints amount
    @retry_decorator()
    async def get_np(self, db=None) -> int:
        """Gets amount of NP current account has"""
        res = await self.query.get("http://www.neopets.com")
        msg = await NPHelpers.get_text(res)
        np_match = re.search(r'<span id="npanchor" class="np-text__2020">(.*?)</span>', msg)
        if np_match:
            np = int(np_match.group(1).replace(',', ''))
            self.np = np

            if db is not None:
                await db.update_np(self.username, np)

            return np
        else:
            raise Exception("Failed to find NP amount on Neopets website")

    # Grabs Items From Money Tree #TODO
    @retry_decorator()
    async def get_items(self):
        res = await self.query.get('https://www.neopets.com/donations.phtml')

        mat = '<a href="takedonation_new.phtml?donation_id='
        l = 'takedonation_new.phtml?donation_id=2265265&xcn=e379688b5336db1e585fc8c5d5c94f53&location_id=0'
        msg = self._fix_text(await res.text())
        ind = msg.find(mat)+10
        item = msg[ind:ind+len(l)]

        res_2 = await self.query.get('https://www.neopets.com/' + item)

        print(res_2, msg)

    # Claims newbie pack (auth required)
    @retry_decorator()
    async def claim_newbie_pack(self):
        """Claims newbie pack"""
        res = await self.query.get('https://www.neopets.com/newbie_pack.phtml')

    # Claim Trudy's Prize (auth required)
    @retry_decorator()
    async def claim_trudy(self, client_db=None):
        """Claims Trudy's Prize"""
        res_1 = await self.query.get('https://www.neopets.com/allevents.phtml')
        msg_1 = await self._get_text(res_1)
        if 'You do not have any events queued up for you at this time.' in msg_1:
            return None
        if "Trudy's Surprise has reset" not in msg_1:
            return None
        else:
            res_2 = await self.query.get('https://www.neopets.com/trudys_surprise.phtml')
            res_3 = await self.query.post('https://www.neopets.com/trudydaily/ajax/claimprize.php', {
                'action': 'beginroll',
            })
            roll_res = self._get_json(await res_3.text())
            print(f"Trudy's Surprise: Won {roll_res['prizes'][0]['value']}. Now have {roll_res['adjustedNp']} NP.")
            await asyncio.sleep(0.7)
            res_4 = await self.query.post('https://www.neopets.com/trudydaily/ajax/claimprize.php', {
                'action': 'prizeclaimed',
            })
            res_5 = await self.query.get('https://www.neopets.com/trudys_surprise.phtml')

            await self.get_np(db=client_db)

            return roll_res['prizes'][0]['value']
    
    # Closes all resources the client was using
    async def close(self):
        """Closes and saves client resources"""
        await self.query.close()