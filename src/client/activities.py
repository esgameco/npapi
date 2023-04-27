#
#     _        _   _       _ _   _           
#    /_\   ___| |_(_)_   _(_) |_(_) ___  ___ 
#   //_\\ / __| __| \ \ / / | __| |/ _ \/ __|
#  /  _  \ (__| |_| |\ V /| | |_| |  __/\__ \
#  \_/ \_/\___|\__|_| \_/ |_|\__|_|\___||___/
#                                          
#

#
#   Note
# 
#   Most activities here are taken from other github projects. I try to make them work with my system
#   but more often than not they break in translation. 
#

import datetime
import re
import random
import asyncio

from .client import NPClient
from ..helpers import NPHelpers

class NPActivityClient(NPClient):
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
        super().__init__(username=username,
                         password=password, 
                         id=id, 
                         cookies=cookies,
                         is_registered=is_registered,
                         is_activated=is_activated,
                         np=np,
                         client_type=client_type,
                         user_agent=user_agent, 
                         proxy=proxy, 
                         proxy_manager=proxy_manager)
    
    async def anchor_management(self):
        """Anchor Management Minigame
        
        Gives unknown
        (unknown np / day)
        """
        res_1 = await self.query.get('https://www.neopets.com/pirates/anchormanagement.phtml')
        msg_1 = await self._get_text(res_1)

        if NPHelpers.contains('form-fire-cannon', msg_1):
            action = NPHelpers.search('<input name="action" type="hidden" value="(.*?)">', msg_1)[1]
            res_2 = await self.query.post('https://www.neopets.com/pirates/anchormanagement.phtml', params={
                'action': action
            })
            msg_2 = await self._get_text(res_2)

            if NPHelpers.contains('prize-item-name', msg_2):
                prize = NPHelpers.search('<span class="prize-item-name">(.*?)</span>', msg_2)
                print(f'Blasted krawken; got {prize}')
            else:
                print('Blasted krawken; got unknown prize')
        elif NPHelpers.contains('safe from sea monsters for one day', msg_2):
            print('Already did anchor management.')
        else:
            print("Couldn't find anchor management.")

    async def daily_puzzle(self, correct_answer:str=None, db=None):
        """Daily Puzzle
        
        Gives NP
        (300-500 np / day)
        """

        # """TODO https://www.jellyneo.net/?go=dailypuzzle"""
        # if not correct_answer:
        # res = await self.query.get('https://www.jellyneo.net/?go=dailypuzzle')
        # msg = await res.text()

        # NPHelpers.search('<strong>Prize:</strong> .* NP</p>', msg)
        
        if db:
            correct_answer = await db.activity_info_db.get_info('daily_puzzle')

        res_1 = await self.query.get('https://www.neopets.com/community/index.phtml')
        msg_1 = await NPHelpers.get_text(res_1)

        if 'option' not in msg_1.lower():
            return False

        regex_res = re.findall(r"<option.*?>(.*?)</option>", msg_1, re.DOTALL)
        all_options = [x.lower() for x in regex_res]

        data = {
            'trivia_date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'trivia_response': all_options.index(correct_answer.lower()),
            'submit': 'Submit'
        }

        res_2 = await self.query.post('https://www.neopets.com/community/index.phtml', data=data, referer='https://www.neopets.com/community/index.phtml')
        msg_2 = await NPHelpers.get_text(res_2)

        if 'you have been awarded' not in msg_2.lower():
            # raise ValueError('Not awarded')
            return False

        return True

    async def rich_slorg(self) -> bool:
        """Rich Slorg Minigame
        
        Gives NP
        (avg 50 np / day)
        """
        res = await self.query.get("https://www.neopets.com/shop_of_offers.phtml?slorg_payout=yes")
        msg = await self._get_text(res)

        return 'Something is happening...' not in msg

    async def wishing_well(self) -> int:
        """Wishing Well Minigame (PAID)
        
        7 wishes / day 
        21 np / wish

        returns number of wishing well successful attempts

        Gives very rare items
        (small chance of big $)
        """
        for i in range(20):
            res_1 = await self.query.get('https://www.neopets.com/wishing.phtml')
            msg_1 = await res_1.text()
            if "You can only make 7 wishes a day" in msg_1:
                print("You are out of wishes for today.")
                return i
            res_2 = await self.query.post('https://www.neopets.com/process_wishing.phtml', data={
                'donation': 21, 
                'wish': 'Graffiti Skateboard'
            })
            msg_2 = await res_2.text()
        return 20
    
    async def apple_bobbing(self):
        """Apple Bobbing Minigame (UNSAFE)
        
        Gives random items
        (unknown np / day)
        """
        res_1 = await self.query.get('https://www.neopets.com/halloween/applebobbing.phtml')
        msg_1 = await res_1.text()

        if NPHelpers.contains('Give it a shot!', msg_1):
            res_2 = await self.query.get('https://www.neopets.com/halloween/applebobbing.phtml', params={
                'bobbing': 1
            })
            msg_2 = await res_2.text()
            message = NPHelpers.search("<div id='bob_middle'>(.*?)</div>", msg_2)[1].strip()
            print(message)
            return message
        elif NPHelpers.contains('blind underneath this hat', msg_1):
            print('Already apple bobbed today.')
            return None
        else:
            print("Couldn't find apple bobbing.")
            return None
    
    async def jelly(self):
        """Giant Jelly Minigame
        
        Gives random jelly
        (unknown np / day)
        """
        res_1 = await self.query.get('https://www.neopets.com/jelly/jelly.phtml')
        msg_1 = await res_1.text()

        res_2 = await self.query.post('https://www.neopets.com/jelly/jelly.phtml', params={
            'type': 'get_jelly'
        })
        msg_2 = await res_2.text()
        if NPHelpers.contains('You take some', msg_2):
            prize = NPHelpers.search(r'You take some <b>(.*?)</b>', msg_2)
            print(f"Giant Jelly: Got {prize}")
            return prize
        elif NPHelpers.contains('You cannot take more than one', msg_2):
            print("Already got jelly today.")
            return None
        else:
            print("Error getting giant jelly.")
            return None
    
    async def healing_springs(self):
        """Healing Springs
        
        Gives random health potion
        (unknown np / day)
        """
        res_1 = await self.query.get('https://www.neopets.com/faerieland/springs.phtml')
        msg_1 = await res_1.text()

        res_2 = await self.query.post('https://www.neopets.com/faerieland/springs.phtml', params={
            'type': 'heal'
        })
        msg_2 = await res_2.text()

        result = NPHelpers.search(r'''\n<center>(.*?)<br clear="all">''', msg_2)

        print(f'Healing springs: {result}')
        return result
    
    def _gk_make_params(self, parts):
        """Grumpy King helper function"""
        fixed_parts = dict(zip(
            (f'qp{n}' for n in range(1, 11)),
            'What,do,you do if,,fierce,Peophins,,has eaten too much,,tin of olives'.split(',')
        ))

        params = []
        for qa, n, options in parts:
            options = re.findall(r'<option value="(.*?)"', options)
            options.remove('none')
            name = f'{qa}p{n}'
            choice = fixed_parts.get(name)
            if choice == None:
                choice = random.choice(options)
            params.append(f'{name}={choice}')
        return params

    async def grumpy_king(self):
        """Grumpy King
        
        Gives random item or NP
        (200-800 np / day)
        """
        for _ in range(2):
            res_1 = await self.query.get('https://www.neopets.com/medieval/grumpyking.phtml')
            msg_1 = await self._get_text(res_1)

            if NPHelpers.contains('try back in an hour', msg_1):
                print(f'Grumpy King: At lunch.')
                return None
            
            parts = re.findall(r'<div id="(.)p(\d+)Div">(.*?)</div>', msg_1)
            params = self._gk_make_params(parts)
            params_hum = ' '.join(p.split('=')[1] for p in params)
            print(f'Grumpy King: Asking: {params_hum}')

            res_2 = await self.query.post('https://www.neopets.com/medieval/grumpyking2.phtml?' + '&'.join(params))
            msg_2 = await self._get_text(res_2)

            result = NPHelpers.search(r'''<div align='center'>(.*?)<br clear="all">''', msg_2)
            print(f'Grumpy King: {result}')
            if 'already told me a joke today' in result:
                return None

            return result

    async def lottery(self):
        """Lottery (PAID)
        
        20 tickets / day 
        100 np / tickets

        returns number of lottery successful attempts

        Gives NP
        (small chance of big $)
        """
        res_1 = await self.query.get('https://www.neopets.com/games/lottery.phtml', referer="https://thedailyneopets.com/dailies")
        msg_1 = await res_1.text()

        np = await self.get_np()

        if np < 500:
            return 0
        
        game_hash = self.functions.get_between(msg_1, "_ref_ck' value='", "'>")

        numbers = [random.randint(1, 31) for i in range(6)]
        res_2 = await self.query.post("games/process_lottery.phtml", data={
            "_ref_ck": game_hash, 
            "one": numbers[0], 
            "two": numbers[1], 
            "three": numbers[2], 
            "four": numbers[3], 
            "five": numbers[4], 
            "six": numbers[5]
        }, 
            referer="http://www.neopets.com/games/lottery.phtml")
        msg_2 = await res_2.text()

        if "you cannot buy any more" in msg_2:
            print('No more lottery tickets')
            return 0
        
        return await self.lottery() + 1
    
    async def potato_counter(self):
        """Potato Counter Minigame
        
        returns number of times won

        Gives NP
        (225 np / day)
        """
        res_1 = await self.query.get("http://www.neopets.com/medieval/potatocounter.phtml", referer="https://thedailyneopets.com/dailies")

        for i in range(3):
            res_2 = await self.query.get("http://www.neopets.com/medieval/potatocounter.phtml")
            msg_2 = await self._get_text(res_2)

            potatos = NPHelpers.get_between(msg_2, "potato_think.gif", "form action='potatocounter")
            total_potatos = len(re.findall(r"potato\d.gif", potatos))
            if total_potatos > 0:
                await asyncio.sleep(random.randint(5, 10))
                res_3 = await self.query.post("http://www.neopets.com/medieval/potatocounter.phtml", data={
                    "type": "guess", 
                    "guess": total_potatos
                }, referer=res_2.url)
                msg_3 = await self._get_text(res_3)
            
            if "me potatoes three times a day" in msg_3:
                return i+1
        
        return 3

    async def lunar_temple(self):
        """Lunar Temple Puzzle
        
        Gives Items
        (unknown np / day)
        """
        res_1 = await self.query.get("http://www.neopets.com/shenkuu/lunar/", referer="https://thedailyneopets.com/dailies")
        msg_1 = await self._get_text(res_1)
        
        await asyncio.sleep(1)

        res_2 = await self.query.get("http://www.neopets.com/shenkuu/lunar/?show=puzzle")
        msg_2 = await self._get_text(res_2)

        await asyncio.sleep(1)

        if NPHelpers.contains('once per day', msg_2):
            print('Already did lunar temple.')
            return None

        angle_kreludor = int(NPHelpers.search(r'angleKreludor=(\d+)', msg_2)[1])
        phase = int(((angle_kreludor + 191) % 360) / 22.5)
        print(f'Lunar temple: Phase {phase}. ', end='')

        res_3 = await self.query.post('http://www.neopets.com/shenkuu/lunar/results.phtml', params={
            'submitted': 'true', 
            'phase_choice': 'phase'
        })
        msg_3 = await self._get_text(res_3)

        if NPHelpers.contains('That is the correct answer', msg_3):
            prize = NPHelpers.search(r'Here is a fantastic reward .*?images.neopets.com/items/(.*?)\'', msg_3)
            print(f'Got item with image {prize}')
            return prize
        else:
            print('Error. TODO')
        return None
    
    async def omlette(self):
        """Omlette Minigame
        
        Gives items
        (unknown np / day)
        """
        res_1 = await self.query.get("http://www.neopets.com/prehistoric/omelette.phtml", referer="https://thedailyneopets.com/dailies")
        msg_1 = await self._get_text(res_1)

        if NPHelpers.contains('The Omelette has Gone!!!', msg_1):
            print('Omelette: Gone!!!')
            return None
        
        res_2 = await self.query.post("http://www.neopets.com/prehistoric/omelette.phtml", params={
            'type': 'get_omlette'
        })
        msg_2 = await self._get_text(res_2)

        if NPHelpers.contains('You cannot take more than', msg_2):
            print('Omelette: Already took today.')
        elif NPHelpers.contains('You approach'):
            prize = NPHelpers.search(r'You approach.*images.neopets.com/items/(.*?)\'', msg_2)[1]
            print(f'Omelette: Got item with image {prize}')
            return prize
        else:
            print('Omelette: Error.')
        return None
    
    async def plushie(self):
        """Plushie Thing
        
        Gives NP
        (0-3000 np / day)
        """
        res_1 = await self.query.get("http://www.neopets.com/faerieland/tdmbgpop.phtm", referer="https://thedailyneopets.com/dailies")
        msg_1 = await res_1.text()

        res_2 = await self.query.post("http://www.neopets.com/faerieland/tdmbgpop.phtm", params={
            'talkto': 1
        })
        msg_2 = await res_2.text()

        if NPHelpers.contains("<div align='center'>", msg_2):
            result = NPHelpers.search(r"<div align='center'>(.*?)</div>", msg_2)[1]
            print(f'Plushie: {result}')
            return result
        elif NPHelpers.contains('already visited the plushie today', msg_2):
            print('Plushie: Already visited.')
        else:
            print('Plushie: Error.')
        return None
    
    async def scratchcard(self):
        """Scratchcard (PAID)
        
        Insane profit margins by selling the cards

        Gives items
        (350-10000 np / day)
        """
        if await self.get_np() < 1200:
            print('Not enough NP for scratchcard')
            return None

        res_1 = await self.query.get("http://www.neopets.com/halloween/scratch.phtml", referer="https://thedailyneopets.com/dailies")
        msg_1 = await res_1.text()

        res_2 = await self.query.post("http://www.neopets.com/halloween/process_scratch.phtml")
        msg_2 = await res_2.text()

        if NPHelpers.contains('Hey, give everybody else a chance', msg_2):
            print('Scratchcard: Already bought.')
            return True
        else:
            print('Bought a scratchcard???')
        return None

    async def shrine(self):
        """Coltzan's Shrine
        
        Gives items
        (unknown np / day)
        """
        res_1 = await self.query.get("http://www.neopets.com/desert/shrine.phtml", referer="https://thedailyneopets.com/dailies")
        msg_1 = await res_1.text()

        res_2 = await self.query.post("http://www.neopets.com/desert/shrine.phtml", params={
            'type': 'approach'
        })
        msg_2 = await res_2.text()

        if NPHelpers.contains('shrine_win.gif', msg_2) or NPHelpers.contains('shrine_scene.gif', msg_2):
            result = NPHelpers.search(r'\n<p>.*?<br clear="all">', msg_2)[0]
            print(f"Coltzan's Shrine: {result}")
            return result
        elif NPHelpers.contains('Maybe you should wait a while', msg_2):
            print("Coltzan's Shrine: Already visited.")
        else:
            print("Coltzan's Shrine: Error.")
        return None
    
    async def snowager(self):
        """Snowager
        
        Gives Items
        (unknown np / day)
        """
        res_1 = await self.query.get("http://www.neopets.com/winter/snowager.phtml", referer="https://thedailyneopets.com/dailies")
        msg_1 = await res_1.text()

        if NPHelpers.contains('The Snowager is awake', msg_1):
            print('Snowager: Awake.')
            return None
        
        res_2 = await self.query.get("http://www.neopets.com/winter/snowager2.phtml")
        msg_2 = await res_2.text()

        if NPHelpers.contains('You dont want to try and enter again', msg_2):
            print('Snowager: Already done.')
            return None
        result = NPHelpers.search(r'<p>(.*?)<p>.*?</center><center>', msg_2)
        if result:
            print(f'Snowager: {result}')
            return True
        else:
            print('Snowager: Error.')
        return None
    
    async def tombola(self):
        """Tombola Minigame
        
        Gives Items and NP
        (100-200 np / day)
        """
        res_1 = await self.query.get("http://www.neopets.com/island/tombola.phtml", referer="https://thedailyneopets.com/dailies")
        msg_1 = await res_1.text()

        res_2 = await self.query.post("http://www.neopets.com/island/tombola2.phtml")
        msg_2 = await res_2.text()

        if NPHelpers.contains('you are only allowed one', msg_2):
            print('Tombola: Already played.')
            return None

        if NPHelpers.contains('YOU ARE A WINNER!!!', msg_2):
            result = NPHelpers.search(r'\n<center>(.*?)\n', msg_2)[1]
            image = re.search(r"<img src='http://images.neopets.com/items/(.*?)'", result)[1]
            print(f'Tombola: Won. {result} ({image})')
            return (result, image)
        elif NPHelpers.contains('you win a Booby Prize', msg_2):
            prize = NPHelpers.search(r'<b>Your Prize - (.*?)</b>', msg_2)[1]
            print(f'Tombola: Won booby prize: {prize}')
            return prize
        elif NPHelpers.contains("and you don't even get a booby prize", msg_2):
            print('Tombola: Lost')
        else:
            print('Tombola: Unknown result. TODO')
        return None
    
    async def fruit_machine(self):
        """Fruit Machine Minigame
        
        Gives Items and NP
        (0-25000 np / day)
        """
        res_1 = await self.query.get('http://www.neopets.com/desert/fruit/index.phtml', referer='https://thedailyneopets.com/dailies')
        msg_1 = await self._get_text(res_1)

        if 'Please come back tomorrow and try again' not in msg_1:
            result = NPHelpers.get_between(msg_1, 'name="ck" value="', '">')
            res_2 = await self.query.post('http://www.neopets.com/desert/fruit/index.phtml', data={
                'spin': '1', 
                'ck': result
                }, referer='http://www.neopets.com/desert/fruit/index.phtml')
            msg_2 = await self._get_text(res_2)

            if 'Sorry, this is not a winning spin' in msg_2:
                print('Fruit machine fail')
            else:
                print('Fruit Machine: You won!')
                return True
        return None
    
    async def ghoul(self):
        """Ghoul Catchers Minigame TODO
        
        (50000 np / day)
        """
        pass

    async def tyranu_evavu(self):
        """Tyranu Evavu Minigame TODO
        
        (unknown np / day)
        """
        pass

    async def neggsweeper(self):
        """Neggsweeper Minigame TODO
        
        (3k/day)
        """
        pass

    async def cliffhanger(self):
        """Cliffhanger Minigame TODO
        
        (1500 NP/day)
        """