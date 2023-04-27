# npapi

A neopets API created with python/aiohttp, uses asyncpg for database. Supports multiple accounts.

## Features
- Supports registration, account activation, creating a pet, trudy's surprise, and multiple dailies.
- Proxy services to find open proxies that work for neopets. Supports Socks proxies (maybe).
    - Around 100 working proxies in 3 minutes.
    - For each working proxy, a new account is created.
- Email services to allow (unlimited?) free email activations
    - Using 1secmail currently
    - You may want to use proxies to access 1sec if they block your ip
    - Possible other services: Mailinator, Guerrilla Mail, 10MinuteMail

## Warning
I would not use this API with any account you care about. It might freeze it, it might not. Who knows. It is only meant for using a massive number of accounts.

## Setup

#### Installation
```bash
git clone https://github.com/esgameco/npapi.git
pip install -r requirements.txt
```

#### Secrets:
``` bash
export DB_STR={replace with str}
```

## Goal
The goal of this project is to create a Neopets API that is quick, error resistant, and scalable.
Most other Neopets projects I've seen on Github are only meant for one account, and scaling to multiple accounts adds new complexity.
The end goal is to get a Super Attack Pea and give it away to someone.

## Side note
You can get cheap ChatGPT accounts on HStock that have $5 balance for cents.

## TODO:
- [ ] Captcha Bypass: https://github.com/raresoft/Neopets-Perfect-Captcha/blob/master/captcha.dat
- [ ] Autobuyer: https://github.com/daniellok/neopets-autobuyer
- [ ] More Activities
    - [ ] 
- [ ] Mule Accounts
- [x] Add proxy test accounts to database

## Activities shamelessly stolen from:
- https://github.com/neynt/nptools
- https://github.com/bensnilloc/Inks-Multi-Tool
- https://github.com/bensnilloc/Inks-Account-Scanner
- https://github.com/MajinClraik/Multi-Tool/tree/master/classes