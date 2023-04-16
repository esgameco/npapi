"""
   ___               _        __       
  / _ \___ _ __     (_)_ __  / _| ___  
 / /_\/ _ \ '_ \    | | '_ \| |_ / _ \ 
/ /_\\  __/ | | |   | | | | |  _| (_) |
\____/\___|_| |_|___|_|_| |_|_|  \___/ 
               |_____|                 
"""

from faker import Faker
import random

from ..email import NPEmailManager

class NPGenerateInfo:
    def __init__(self):
        self.fake = Faker()
        self.email_provider = "@cevipsa.com"
        self.email_manager = NPEmailManager()
    
    async def gen_user_info(self):
        username = self.gen_username()
        return {
            'username': self.gen_username(),
            'password': self.gen_password(),
            'email': await self.gen_email(),
            'dob': self.gen_dob()
        }
    
    def gen_username(self):
        return self.fake.user_name() + str(random.randint(99, 999))
    
    def gen_password(self):
        return self.fake.password() + str(random.randint(99, 999))

    async def gen_email(self):
        # return self.gen_username() + self.email_provider
        return await self.email_manager.gen_email()

    def gen_dob(self):
        return {
            'month': str(random.randint(1, 12)),
            'day': str(random.randint(1, 28)),
            'year': str(random.randint(1960, 2000))
        }
    
    def gen_pet_info(self):
        return {
            'pet_name': self.gen_pet_name(), 
            'pet_type': self.gen_pet_type(), 
            'selected_pet_colour': self.gen_pet_color(), 
            'selected_item': random.choice(['', '81976', '81975', '81974', '81973']),
            'gender': random.choice(['male', 'female']),
            'terrain': str(random.randint(1, 7)),
            'likes': str(random.randint(1, 5)),
            'meetothers': str(random.randint(1, 7)),
            'pet_stats_set': str(random.randint(1, 3))
        }

    def gen_pet_name(self):
        return self.fake.user_name() + str(random.randint(9999, 9999999))
    
    def gen_pet_color(self):
        return random.choice(['blue', 'green', 'red', 'yellow'])

    def gen_pet_type(self):
        return random.choice(['Nimmo',
                            'Scorchio',
                            'JubJub',
                            'Grarrl',
                            'Skeith',
                            'Korbat',
                            'Lenny',
                            'Wocky',
                            'Bruce',
                            'Kiko',
                            'Kau',
                            'Usul',
                            'Aisha',
                            'Chia',
                            'Eyrie',
                            'Tuskaninny',
                            'Flotsam',
                            'Jetsam',
                            'Kacheek',
                            'Uni',
                            'Buzz',
                            'Lupe',
                            'Elephante',
                            'Gelert',
                            'Mynci',
                            'Kyrii',
                            'Peophin',
                            'Quiggle',
                            'Shoyru',
                            'Acara',
                            'Zafara',
                            'Blumaroo',
                            'Techo',
                            'Moehog',
                            'Cybunny',
                            'Poogle',
                            'Kougra',
                            'Grundo',
                            'Koi',
                            'Meerca',
                            'Chomby',
                            'Pteri',
                            'Krawk',
                            'Tonu',
                            'Draik',
                            'Ixi',
                            'Yurble',
                            'Ruki',
                            'Bori',
                            'Hissi',
                            'Lutari',
                            'Xweetok',
                            'Ogrin',
                            'Gnorbu']).lower()
