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

