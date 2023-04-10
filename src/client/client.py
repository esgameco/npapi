import os
import hashlib

from ..query import NPQuery, NPCookieJar

class NPClient:
    def __init__(self, username=None, password=None, text_cookie=None):
        self.username = username
        self.password = password
        self.cookies = NPCookieJar(text_cookie)
        self.query = NPQuery(os.getenv('PROXY_WEBSHARE'))

    # Registers for account
    async def register(self, username, password, email, dob=None, security=None):
        ### Resister Page (get cookies) -- https://www.neopets.com/signup/index.phtml
        # 
        res_1 = await self.query.post('https://www.neopets.com/signup/index.phtml')
        self.cookies.import_from_response(res_1)

        ### Name Availability (get ssoreserve) -- https://www.neopets.com/signup/ajax.phtml
        # method	"checkAvailability"
        # username	"***"
        res_2 = await self.query.post('https://www.neopets.com/signup/ajax.phtml', data={
            'method': "checkAvailability",
            'username':	username
        }, cookies=self.cookies.get_all())
        self.cookies.import_from_response(res_2)
        # query_headers={
        #     'Accept': 'application/json, text/javascript, */*; q=0.01',
        #     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #     'Referer': 'https://www.neopets.com/signup/index.phtml',
        #     'Sec-Fetch-Dest': 'empty',
        #     'Sec-Fetch-Mode': 'cors',
        #     'Sec-Fetch-Site': 'same-origin',
        #     "X-Requested-With": "XMLHttpRequest"
        # }

        ### Register Step 1 -- https://www.neopets.com/signup/ajax.phtml
        # method	"step1_2020"
        # username	"***"
        # password1	"***"
        # password2	"***"
        # terms	"true"
        # month	"10"
        # day	"05"
        # year	"2000"
        # email1	"***@mocvn.com"
        # email2	"***@mocvn.com"
        # optinNeopets	"false"
        # destination	""
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
        }, cookies=self.cookies.get_all())
        self.cookies.import_from_response(res_3)

        ### Register Index Page again (don't know why)
        res_4 = await self.query.post('https://www.neopets.com/signup/index.phtml',
                                      cookies=self.cookies.get_all())
        self.cookies.import_from_response(res_4)

        ### Register Step 2
        # method	"step2_2020"
        # gender	"M"
        # question1	"1"
        # question2	"5"
        # answer1	"***"
        # answer2	"***"
        # country	"US"
        # usState	"CA"
        res_5 = await self.query.post('https://www.neopets.com/signup/ajax.phtml', data={
            'method': "step2_2020",
            'gender': security['gender'] if security else "M",
            'question1': security['question1'] if security else "1",
            'question2': security['question2'] if security else "5",
            'answer1': security['answer1'] if security else "SmithStreet",
            'answer2': security['answer2'] if security else "Janitor",
            'country': security['country'] if security else "US",
            'usState': security['usState'] if security else "CA"
        }, cookies=self.cookies.get_all())
        self.cookies.import_from_response(res_5)

        res_6 = await self.query.post('https://www.neopets.com/reg/page4.phtml',
                                      cookies=self.cookies.get_all())
        self.cookies.import_from_response(res_6)

    # Get activation code from email given (tempmail)
    async def get_activation_code(self, email):
        email_hash = hashlib.md5(email.encode()).hexdigest()
        res = await self.query.get(
            f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{email_hash}/",
            query_headers={
                "X-RapidAPI-Key": os.getenv('API_TEMPMAIL'),
                "X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
            })

        if res.status_code != 200:
            raise Exception
        
        txt = res.json()[0]['mail_text']
        index = txt.find('?code=')+6
        code = txt[index:index+7]

        return code

    # Activates email with code from email
    async def activate_code(self, code):
        res = await self.query.get(f'https://www.neopets.com/activate.phtml?code={code}',
                                   cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)

    # Creates pet (after register)
    async def create_pet(self, pet_name, pet_type):
        ### Step 1 -- https://www.neopets.com/reg/process_createpet.phtml
        # neopet_name	"***"
        # selected_pet	"tuskaninny"
        # selected_pet_colour	"green"
        # selected_item	""
        # gender	"male"
        # terrain	"4"
        # likes	"5"
        # meetothers	"3"
        # pet_stats_set	"3"

        res = await self.query.post('https://www.neopets.com/reg/process_createpet.phtml', data={
            'neopet_name':	pet_name,
            'selected_pet':	pet_type,
            'selected_pet_colour':	"green",
            'selected_item':	"",
            'gender':	"male",
            'terrain':	"4",
            'likes':	"5",
            'meetothers':	"3",
            'pet_stats_set':	"3",
        }, cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)
    
    # Donates selected amount (no auth required)
    async def donate(self, amount):
        res = await self.query.post('https://www.neopets.com/process_donation.phtml', data={
            'donation': str(amount)
        }, cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)
    
    # Gets current neopoints amount (TODO: FIX)
    async def get_np(self):
        res = await self.query.get('https://www.neopets.com/objects.phtml', 
                                   cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)

        mat = '<span id="npanchor" class="np-text__2020">'
        ind = res.text.find(mat)+len(mat)
        ind_end = res.text[ind:].find('<')
        
        return res.text[ind:ind+ind_end].replace(',', '')

    # Grabs Items From Money Tree
    async def get_items(self):
        res = await self.query.get('https://www.neopets.com/donations.phtml', 
                                   cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)

        mat = '<a href="takedonation_new.phtml?donation_id='
        l = 'takedonation_new.phtml?donation_id=2265265&xcn=e379688b5336db1e585fc8c5d5c94f53&location_id=0'
        ind = res.text.find(mat)+10
        item = res.text[ind:ind+len(l)]

        res_2 = await self.query.get('https://www.neopets.com/' + item, 
                                   cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)

        print(res_2, res_2.text)

    # Claims newbie pack (auth required)
    async def claim_newbie_pack(self):
        res = await self.query.get('https://www.neopets.com/newbie_pack.phtml', 
                                   cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)
    
    # Checks authentication using cookie
    async def check_auth(self):
        return None

    # Claim Trudy's Prize (auth required)
    async def claim_trudy(self):
        res = await self.query.get('https://www.neopets.com/trudydaily/ajax/claimprize.php', 
                                   cookies=self.cookies.get_all())
        self.cookies.import_from_response(res)
    
    # Closes all resources the client was using
    async def close(self):
        await self.query.close()
