"""
   ___ _ _            _   
  / __\ (_) ___ _ __ | |_ 
 / /  | | |/ _ \ '_ \| __|
/ /___| | |  __/ | | | |_ 
\____/|_|_|\___|_| |_|\__|
                          
"""

import os
import hashlib
import json
import functools
import time
import asyncio

import aiohttp
from http.cookies import SimpleCookie, Morsel
from typing import Optional

from ..query import NPQuery
from ..exceptions import *
from .helpers import retry_decorator

class NPClient:
    def __init__(self, 
                 username: str=None, 
                 password: str=None, 
                 id: str=None, 
                 cookies: str=None, 
                 user_agent: str=None,
                 proxy: str=None, 
                 proxy_manager=None):
        self.username = username
        self.password = password
        self.cookies = cookies
        self.query = NPQuery(proxy=proxy, proxy_manager=proxy_manager, cookies=cookies, user_agent=user_agent)
        self._id = id

    # Checks if registered or logged in (only to be used after registration or login)
    async def check_has_auth(self) -> bool:
        session_token = self.query.client.cookie_jar.filter_cookies('http://neopets.com/').get('neologin')
        return session_token is not None and len(session_token.value) > 10
    
    @retry_decorator()
    async def cookie_test(self):
        res = await self.query.get('https://www.neopets.com/island/tradingpost.phtml')

    # Serialize the aiohttp CookieJar to a JSON string
    async def serialize_cookie_jar(self, cookie_jar):
        cookies_list = [
            {
                "key": cookie.key,
                "value": cookie.value,
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", ""),
                "expires": cookie.get("expires", ""),
                "secure": cookie.get("secure", False),
                "httponly": cookie.get("httponly", False),
            }
            for cookie in cookie_jar
        ]
        return json.dumps(cookies_list)

    # Deserialize the JSON string to an aiohttp CookieJar
    async def deserialize_cookie_jar(self, cookies_list):
        cookie_jar = aiohttp.CookieJar()
        for cookie_dict in cookies_list:
            morsel = Morsel()
            morsel.set(cookie_dict["key"], cookie_dict["value"], cookie_dict["value"])
            morsel["domain"] = cookie_dict["domain"]
            morsel["path"] = cookie_dict["path"]
            morsel["expires"] = cookie_dict["expires"]
            morsel["secure"] = cookie_dict["secure"]
            morsel["httponly"] = cookie_dict["httponly"]

            # Create a SimpleCookie and add the Morsel to it
            cookie = SimpleCookie()
            cookie[morsel.key] = morsel

            # Add the deserialized cookie to the cookie jar
            cookie_jar.update_cookies(cookie)
        
        return cookie_jar

    # Logs in user
    @retry_decorator()
    async def login(self, username: str, password: str, set_details: bool=True) -> None:
        res = await self.query.post('https://www.neopets.com/login.phtml', data={
            'username': username,
            'password': password,
            'return_format': 'json'
        })
        res_msg = await res.text()

        if not await self.check_has_auth():
            await self.query.report_proxy()
            raise LoginError('Login failed -- No Auth')

        if set_details:
            self.username = username
            self.password = password
    
    # Gets json from messages
    def _get_json(self, msg: str) -> Optional[str]:
        """Gets json from aiohttp responses
        
        Will only return json if there is json to return
        """
        try:
            return json.loads(self._fix_text(msg))
        except Exception as e:
            print(e)
        return None
    
    # Fixes text from messages
    def _fix_text(self, msg: str) -> Optional[str]:
        """Fixes text in messages that contain / or \\"""
        try:
            return msg.replace('/', '').replace('\n', '').replace('\t', '').replace('\r', '').replace('\\', '')
        except Exception as e:
            print(e)
        return None
    
    # Gets text from http response
    async def _get_text(self, res) -> Optional[str]:
        """Returns fixed text of a response"""
        try:
            return self._fix_text(await res.text())
        except Exception as e:
            print(e)
        return None

    # Registers for account
    @retry_decorator()
    async def register(self, 
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
    @retry_decorator(5, 3)
    async def activate_code(self, code: str) -> None:
        """Activates account with code from email"""
        res = await self.query.get(f'https://www.neopets.com/activate.phtml?code={code}')

        is_activated = await self.check_activated()
        if not is_activated:
            raise ActivationError('Activation Error -- Not Activated')

    # Checks whether the account is activated
    @retry_decorator()
    async def check_activated(self) -> bool:
        """Checks whether account is activated by using the trading post"""
        res = await self.query.get('https://www.neopets.com/island/tradingpost.phtml')
        
        msg = self._fix_text(await res.text())
        return '<b>Activate Your Account</b>' not in msg

    # Creates pet (after register)
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
        """Creates pet, name is required"""
        res = await self.query.post('https://www.neopets.com/reg/process_createpet.phtml', data={
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

        if self._fix_text(await res.text()) != 'feedback|pet_success2':
            raise PetCreationError('Pet Creation Error -- No Success Message')
    
    # Donates selected amount (no auth required)
    @retry_decorator()
    async def donate(self, amount) -> None:
        """Donates to wishing well selected amount"""
        res = await self.query.post('https://www.neopets.com/process_donation.phtml', data={
            'donation': str(amount)
        })
    
    # Gets current neopoints amount
    @retry_decorator()
    async def get_np(self) -> int:
        """Gets amount of NP current account has"""
        res = await self.query.get('https://www.neopets.com/userinfo.phtml')
        # self.cookies.import_from_response(res)

        mat = '<a> <span style="font-weight: normal;">|<span> NP: <a id=\'npanchor\' href="inventory.phtml">'
        msg = self._fix_text(await res.text())
        ind = msg.find(mat)+len(mat)
        ind_end = msg[ind:].find('<')

        if ind < 1000:
            await self.query.report_proxy()
            raise ValueError('NP Error')
        
        return int(msg[ind:ind+ind_end].replace(',', ''))

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
    async def claim_trudy(self):
        """Claims Trudy's Prize"""
        res_1 = await self.query.get('https://www.neopets.com/allevents.phtml')
        msg = await self._get_text(res_1)
        if not msg.find("Trudy's Surprise has reset") >= 0:
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
            return roll_res['prizes'][0]['value']
    
    # Closes all resources the client was using
    async def close(self):
        """Closes and saves client resources"""
        await self.query.close()