# npapi

A neopets API created with python/httpx, uses asyncpg for database. Supports multiple accounts.

## Features
- Supports registration, account activation, creating a pet, and trudy's surprise. More to come.
- Proxy services to find open proxies that work for neopets (can take a while).
- Email services to allow (unlimited?) free email activations
    - Using 1secmail currently
    - Possible other services: Mailinator, Guerrilla Mail, 10MinuteMail

### TODO:
- Captcha Bypass: https://github.com/raresoft/Neopets-Perfect-Captcha/blob/master/captcha.dat
- Autobuyer: https://github.com/daniellok/neopets-autobuyer
- More Activities
- Mule Accounts
- Add proxy test accounts to database