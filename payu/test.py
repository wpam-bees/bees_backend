import requests

pos_id = '345119'
second_key = 'cb313271a1b1c2d804b9ee420aa1f4ba'
client_id = '345119'
client_secret = 'ee6696cecc1a2c14bb549076dc6a7f4f'


url = 'https://secure.payu.com/pl/standard/user/oauth/authorize'
headers = {
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'email': 'pawel.a.rybak@gmail.com',
    'ext_customer_id': 1,
}

r = requests.post(url, headers=headers, data=data)

print(r.status_code)
print(r.json())
