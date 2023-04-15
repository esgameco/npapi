import aiohttp
import asyncio
import json

from ..query import NPQuery

class NPEmailManager:
    def __init__(self):
        self.query = NPQuery()

    async def gen_email(self):
        """Generates email to use for getting activation code"""

        # Create a temporary email address
        res = await self.query.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        
        temp_email = json.loads(await res.text())[0]

        return temp_email

    async def get_code(self, email: str):
        """Gets activation code from email"""

        # Get the list of emails received by the temporary email address
        res = await self.query.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={email.split('@')[0]}&domain={email.split('@')[1]}")
        messages = json.loads(await res.text())

        # Find the Neopets activation email
        activation_email_id = None
        for message in messages:
            if message["from"] == "noreply@neopets.com" and "activation" in message["subject"].lower():
                activation_email_id = message["id"]
                break
        if not activation_email_id:
            raise Exception("Neopets activation email not found")

        # Get the content of the activation email
        res_2 = await self.query.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={email.split('@')[0]}&domain={email.split('@')[1]}&id={activation_email_id}")
        email_content = json.loads(await res_2.text())

        # Extract the activation code from the email content (you may need to modify the parsing logic)
        activation_code = email_content["textBody"].split("code: ")[1].split("\n")[0].strip()

        return activation_code

    async def close(self):
        await self.query.close()