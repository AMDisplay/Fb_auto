import requests
from get_value_country import get_all_price

API_KEY_5SIM = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDI5MTQ0NjksImlhdCI6MTY3MTM3ODQ2OSwicmF5IjoiNzM5NWU4MDU1M2M5YTIzOTRmMDRjYzQ4MjMxOTAyMWIiLCJzdWIiOjEzMzkzNzJ9.rUw6MTafe_hwaF1kpJnzOe_sI4wLsJQFtR9tCTvdKw81oUlKEXM_c-W1lgejxL6zqIQW_zMJnIqCgFpCZ0p7qzibQ5WwGGcsrzrqFsfzrqXyPkbZRIybA1wIYYMf5x3-PE_o4au3DcKNrCpV7ybUuJgRLHyEMfadEj3xo-vYt6Bk7ia4aOD5mNq4yAyvTv44EvWMrBuUbt3ObtmKBZsMR3URGih-q9TLJU0KHh22yuCeyi7L60Q2Qm4a4MbSZpsKMQR3eSVCl6reHg208rGldgGXA0nvpBkkgfkROilxXtruvUl0QpFF7m4pWFJqYs9V9gUGA2ztuAEvncfez4KMXg'
DOMAIN = "5sim.net"


def buy_number():
    token = API_KEY_5SIM
    result_value_price = get_all_price()
    print(result_value_price)
    country = result_value_price['country']
    operator = result_value_price['operator']
    product = 'instagram'
    
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }



    response = requests.get(f'https://{DOMAIN}/v1/user/buy/activation/' + country + '/' + operator + '/' + product, headers=headers)
    print(response.text)
    return response.json()


def get_sms_status(id):
    token = API_KEY_5SIM
    id = id

    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    response = requests.get(f'https://{DOMAIN}/v1/user/check/' + str(id), headers=headers)
    return response


def ban_phone_number(info_sms):
    id_number = info_sms['id']
    token = API_KEY_5SIM
    id = str(id_number)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    response = requests.get(f'https://{DOMAIN}/v1/user/ban/' + id, headers=headers)
    return response


def cancel_phone(id):
    token = API_KEY_5SIM
    id = str(id)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    response = requests.get(f'https://{DOMAIN}/v1/user/cancel/' + id, headers=headers)
    return response


def check_phone_on_free():
    response = buy_number()
    if response is None:
        print('Телефона нет в наличий')
        rate_for_number = 0
        response = get_all_price(rate=rate_for_number)
        return response
    else:
        return response