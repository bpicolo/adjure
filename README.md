[![Build Status](https://travis-ci.org/bpicolo/adjure.svg?branch=master)](https://travis-ci.org/bpicolo/adjure)
# adjure
Adjure is a simple microservice for Two-Factor authentication. It provides endpoints for user provisioning, authorization, and generating relevant QR-codes to scan with apps
like Google Authenticator.

## Using adjure
### Running Adjure
Docker is the easiest way to run Adjure, though it's also just a standard
uWSGI application. The default config.yaml and also uWSGI configurations
are a reasonable configuration set for typical use.

Running in Docker:
```
docker-compose build adjure
ADJURE_DB_HOST=sqlite:////tmp/adjure.data docker-compose up adjure
```

On first startup, adjure will create an `adjure_auth_user` table in the given
database.

### Provision a new user
```
>>> response = requests.post(
    'http://localhost:5000/user/provision',
    json={
        'user_id': '123',
        'key_length': 6,  # Defaults to your config.yaml value or 6
        'key_valid_duration': 30,  # Defaults to your config.yaml value or 30
        'hash_algorithm': 'SHA256',  # Defaults to your config.yaml value or SHA256
    }
)
>>> print(response.json())
{u'user_id': 123}
```

### Authenticate the user
```
# Typically a user would get this code from their 2FA app.
>>> response = requests.get('http://localhost:5000/user/auth_code', params={'user_id': '123'})
>>> response.json()
{u'code': u'832136'}
>>> code = response.json()['code']
>>> authenticate_response = requests.post(
...         'http://localhost:5000/user/authenticate',
...         json={
...             'user_id': '123',
...             'auth_code': code
...         }
...     )
>>> authenticate_response.json()
{}
```

### Generate a QR code image to scan with a user's 2FA app
You should proxy directly to this from your application. (Return type is image/png)

Issuer, username, and user_id are required fields. Issuer and username are used
by 2FA apps just for display purposes, to allow users to figure out which of
their many apps this is for.

- issuer: Typically, your business name
- username: The username to show for the user in their 2FA app

`http://localhost:5000/user/qrcode?issuer=Adjure&username=Foobar&user_id=123`
