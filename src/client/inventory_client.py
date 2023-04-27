#    _____                      _                   
#    \_   \_ ____   _____ _ __ | |_ ___  _ __ _   _ 
#     / /\/ '_ \ \ / / _ \ '_ \| __/ _ \| '__| | | |
#  /\/ /_ | | | \ V /  __/ | | | || (_) | |  | |_| |
#  \____/ |_| |_|\_/ \___|_| |_|\__\___/|_|   \__, |
#                                             |___/ 

import re
import random
import asyncio
from typing import Dict, List

from .client import NPClient
from ..helpers import NPHelpers

class NPInventoryClient(NPClient):
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
    
    ###################
    # SHOP MANAGEMENT #
    ###################

    async def shop_create(self, shop_info: dict) -> bool:
        """Creates shop
        
        Returns whether the shop was successfully created or not
        """
        res_1 = await self.query.post("https://www.neopets.com/process_market.phtml", data={
            'shop_name': shop_info['name'],
            'shop_world': shop_info['world'], # 0-2
            'description': shop_info['description'],
            'remLen': 4000 - len(shop_info['description']),
            'shopkeeper_name': shop_info['sk-name'],
            'shopkeeper_greeting': shop_info['sk-greeting']
        }, referer='https://www.neopets.com/market.phtml?type=edit')
        msg_1 = await NPHelpers.get_text(res_1).lower()

        if 'you do not have enough neopoints to upgrade your shop' in msg_1:
            return False
        
        res_2 = await self.query.get("https://www.neopets.com/market.phtml?type=edit",
                                     referer='https://www.neopets.com/market.phtml?type=edit')
        msg_2 = await NPHelpers.get_text(res_2).lower()
        
        return 'your shop is currently size' in msg_2
    
    async def shop_upgrade(self) -> bool:
        """Upgrades shop
        
        Returns whether it was successfully upgraded or not
        """
        res_1 = await self.query.post("https://www.neopets.com/process_market.phtml", data={
            'type': 'upgrade'
        }, referer='https://www.neopets.com/market.phtml?type=edit')
        msg_1 = await NPHelpers.get_text(res_1).lower()

        if 'you do not have enough neopoints to upgrade your shop' in msg_1:
            return False
        
        res_2 = await self.query.get("https://www.neopets.com/market.phtml?type=edit",
                                     referer='https://www.neopets.com/market.phtml?type=edit')
        msg_2 = await NPHelpers.get_text(res_2).lower()
        
        return 'your shop is currently size' in msg_2

    async def shop_get_stock(self) -> List[dict]:
        """Gets the current stock of a client's shop
        
        Returns the stock of the shop
        """
        res = await self.query.get("http://www.neopets.com/objects.phtml?type=shop&obj_type_id=1")
        msg = await NPHelpers.get_text(res)

        stock_pattern = r'<tr class="(?:content|contentAlt)"[^>]*><td><b><a href="/market.phtml\?obj_info_id=(\d+)[^"]*"[^>]*>([^<]+)</a></b></td><td>(\d+)</td><td>(\d+)</td>'
        stock_data = re.findall(stock_pattern, msg, re.MULTILINE)

        stock_list = []
        for obj_id, name, stock, price in stock_data:
            stock_list.append(
                {"name": name, "stock": int(stock), "price": int(price), "obj_id": int(obj_id)}
            )

        return stock_list
    
    async def shop_update_stock(self, items: List[Dict]):
        """Updates the store stock
        
        Returns whether it was updated successfully
        """
        data = {
            "type": "update_prices",
            "order_by": "",
            "view": "",
            "lim": 30,
            "obj_name": "",
        }

        for index, item in enumerate(items, start=1):
            prefix = f"{index}_"
            data[f"obj_id_{index}"] = item["obj_id"]
            data[f"oldcost_{index}"] = 0
            data[f"cost_{index}"] = item["new_price"]
            data[f"back_to_inv[{item['obj_id']}]"] = int(item["remove"])

        res = await self.query.post("https://www.neopets.com/your_shop_url_here", data=data)
        # Check if the request was successful and handle errors if needed
        if res.status != 200:
            raise Exception(f"Error updating stock: {res.status}")
        
        return True
    
    async def shop_withdraw_till(self, amount):
        """Withdraws np from the shop till
        
        Returns whether withdraw was successful or not
        """
        withdraw_url = "http://www.neopets.com/process_till.phtml"
        shop_url = "http://www.neopets.com/market.phtml?type=till"

        # Get the shop till page
        shop_response = await self.query.get(shop_url)
        shop_content = await shop_response.text()

        # Find the "ck" value needed for the withdrawal request
        ck_pattern = re.compile(r'name="ck" value="(\w+)"')
        ck_value = ck_pattern.search(shop_content).group(1)

        # Make the withdrawal request
        withdrawal_data = {
            "ck": ck_value,
            "amount": amount,
            "action": "withdraw",
            "type": "till"
        }
        withdrawal_response = await self.query.post(withdraw_url, data=withdrawal_data)

        return withdrawal_response.status == 200

    ########################
    # INVENTORY MANAGEMENT #
    ########################

    async def inv_add_to_shop(self, object_id: int) -> bool:
        """Adds item to user shop
        
        Returns whether it actually happened or not
        """
        res_1 = await self.query.post("https://www.neopets.com/np-templates/views/useobject.phtml", data={
            'obj_id': object_id,
            'action': 'stockshop',
            'petcare': 0
        }, referer='https://www.neopets.com/inventory.phtml')
        msg_1 = await NPHelpers.get_text(res_1).lower()

        return 'you have added' in msg_1

    async def inv_give_item(self, object_id: int, recipient: str) -> bool:
        """Gives item to other user
        
        Returns whether item was successfully sent
        """
        res_1 = await self.query.post("https://www.neopets.com/np-templates/views/useobject.phtml", data={
            'obj_id': object_id,
            'action': 'give',
            'petcare': 0
        }, referer='https://www.neopets.com/inventory.phtml')
        msg_1 = await NPHelpers.get_text(res_1).lower()

        res_2 = await self.query.post("https://www.neopets.com/np-templates/views/useobject.phtml", data={
            'obj_id': object_id,
            'or_name': recipient
        }, referer='https://www.neopets.com/inventory.phtml')
        msg_2 = await NPHelpers.get_text(res_2).lower()

        return 'you have given' in msg_2
    
    ##############
    # Shop Buyer #
    ##############

    async def get_shop_items(self, shop_owner: str) -> List[Dict]:
        """Gets all items in a shop
        
        Returns a list of items
        """
        items = []
        page = 1
        for _ in range(30): # Only do 30 maximum pages in case it breaks
            res = await self.query.get(f'http://www.neopets.com/browseshop.phtml?owner={shop_owner}&page={page}')
            msg = await NPHelpers.get_text(res)
            if "doesn't have a shop" in msg:
                raise ValueError("Shop owner doesn't have a shop")
            if "does not exist" in msg:
                raise ValueError("Shop owner does not exist")
            if "You cannot view this shop" in msg:
                raise ValueError("You cannot view this shop")
            if "You are not allowed to view" in msg:
                raise ValueError("You are not allowed to view this shop")

            page_data = re.findall(
                r'<tr class="content">.+?<b>(.+?)</b>.+?stock">(\d+).+?cost">(\d+).+?obj_info_id=(\d+)', msg, re.DOTALL)

            if not page_data:
                break

            for name, stock, cost, obj_id in page_data:
                item = {
                    'name': name,
                    'stock': int(stock),
                    'cost': int(cost),
                    'obj_id': int(obj_id)
                }
                items.append(item)

            page += 1

        return items
    
    async def purchase_item(self, owner: str, obj_id: int) -> bool:
        """Puchases item from a shop
        
        Returns whether puchase was successful or not
        """
        res_1 = await self.query.get(f'https://www.neopets.com/browseshop.phtml?owner={owner}&buy_obj_info_id={obj_id}')
        msg_1 = await NPHelpers.get_text(res_1)
        search_result = re.search(r'<form action="process_shop.phtml" method="POST".*?">', msg_1, re.DOTALL)

        if not search_result:
            return False

        form_data = {
            'obj_id': obj_id,
            'owner': owner
        }

        for match in re.finditer(r'<input type="hidden" name="(.*?)" value="(.*?)"', search_result.group(0)):
            form_data[match.group(1)] = match.group(2)

        res_2 = await self.query.post('https://www.neopets.com/process_shop.phtml', data=form_data)
        msg_2 = await NPHelpers.get_text(res_2).lower()
        return 'your purchase has been successful' in msg_2

    ###############
    # Shop Wizard #
    ###############

    async def wizard_get_listings(self, item_name):
        item_name = item_name.replace(' ', '+')
        url_template = f"http://www.neopets.com/market.phtml?type=wizard&string={item_name}&criteria=exact&submit=Search&numSections=13&section={{section}}"

        all_listings = []
        tasks = []

        for section in range(1, 14):
            tasks.append(self.fetch_section(url_template.format(section=section)))

        listings_per_section = await asyncio.gather(*tasks)

        for listings in listings_per_section:
            all_listings.extend(listings)

        return all_listings

    async def wizard_fetch_section(self, url):
        async with self.query.get(url) as response:
            text = await response.text()
            return self.parse_listings(text)

    def wizard_parse_listings(self, html):
        pattern = re.compile(r'<tr.*?><td.*?>.*?<b>(.*?)</b>.*?<td.*?>\s*(\d+,\d+|\d+)\s*NP\s*<', re.DOTALL)
        return re.findall(pattern, html)