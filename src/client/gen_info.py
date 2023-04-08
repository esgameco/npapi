from faker import Faker
import random

class NPGenerateInfo:
    def __init__(self):
        self.fake = Faker()
    
    def gen_username(self):
        return self.fake.user_name() + str(random.randint(99, 999))
    
    def gen_password(self):
        return self.fake.password() + str(random.randint(99, 999))

    def gen_dob(self):
        return {
            'month': str(random.randint(1, 12)),
            'day': str(random.randint(1, 28)),
            'year': str(random.randint(1960, 2000))
        }

    def gen_pet_name(self):
        return self.fake.user_name() + str(random.randint(99, 999))

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
