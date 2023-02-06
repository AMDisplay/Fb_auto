import requests
import logging
import time


API_KEY_5SIM = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDYyNjM3MjcsImlhdCI6MTY3NDcyNzcyNywicmF5IjoiN2ZhZmQ1YjI1MWY3NmM5OGI5YThkNDY3NDBiOTVhMDAiLCJzdWIiOjE0MDk3ODF9.xvSchlmDf37N4F5msHJJBGGJ3qrjb-eQdn5BqApayszno7RywRCNIhKGQqRMbSGq0MfJDkMUZjm-sutTnDIcWy3SCpiiD2aPlYaN828qntZEVqdkfcNEIjU88fLpLq9niy8xnFEp0gry-6vU1TUdoldylnSkeLKKLBJB0S0RqT8mznN1XUqDOv7NiOc6neF3Pdb-IpWBZanrVltyeT8mKFvkkDJ_JJhm2FVAKIvAnm8k8IxC3DInKk4iOuWt6eyolbsigaTHvUBcrEP18yQqjdffWJPoEvOwP38ot4cbYnPnorWZpv6wVe0U9ErcwMPOpiROTmp1j1J9mTONVktmQg'
DOMAIN = "5sim.net"

# {'country': 'canada', 'operator': 'virtual8', 'cost': 5, 'count': 175}
# {'country': 'haiti', 'operator': 'virtual4', 'cost': 8.7, 'count': 601}
# {'country': 'mongolia', 'operator': 'virtual7', 'cost': 7, 'count': 1000}
# {'country': 'england', 'operator': 'virtual34', 'cost': 9, 'count': 1248} 
# {'country': 'senegal', 'operator': 'virtual4', 'cost': 9.4, 'count': 807}
# {'country': 'canada', 'operator': 'virtual12', 'cost': 5.6, 'count': 145727} 
# {'country': 'congo', 'operator': 'virtual4', 'cost': 8.8, 'count': 528} 
# {'country': 'colombia', 'operator': 'virtual21', 'cost': 9, 'count': 33}
# {'country': 'egypt', 'operator': 'virtual21', 'cost': 5, 'count': 94}
# {'country': 'mauritius', 'operator': 'virtual21', 'cost': 3, 'count': 2}  
# {'country': 'nicaragua', 'operator': 'virtual23', 'cost': 3.8, 'count': 1000} 
# {'country': 'tanzania', 'operator': 'virtual21', 'cost': 9, 'count': 2}
# {'country': 'canada', 'operator': 'virtual35', 'cost': 8.4, 'count': 1000} 
# {'country': 'england', 'operator': 'virtual4', 'cost': 8, 'count': 8014} 

# {'country': 'canada', 'operator': 'virtual23', 'cost': 8.4, 'count': 1000} Была тесте, показала себя плохо. Не юзать
# {'country': 'india', 'operator': 'virtual21', 'cost': 4, 'count': 25} Была тесте, показала себя плохо. Не юзать
# {'country': 'denmark', 'operator': 'virtual35', 'cost': 8.84, 'count': 1000} Была тесте, показала себя плохо. Не юзать


# {'country': 'cambodia', 'operator': 'virtual21', 'cost': 3, 'count': 4}
# {'country': 'cambodia', 'operator': 'virtual23', 'cost': 5, 'count': 1000} Запасной вариант
# {'country': 'canada', 'operator': 'virtual12', 'cost': 5.6, 'count': 145180} 5/66 окуп при 1/28
# {'country': 'canada', 'operator': 'virtual8', 'cost': 5, 'count': 1442} 34/40 85%+ проход имба
# {'country': 'china', 'operator': 'virtual23', 'cost': 4.3, 'count': 1000} Нет номеров даже при 1000 написанных
# {'country': 'egypt', 'operator': 'virtual21', 'cost': 5, 'count': 190}
# {'country': 'gambia', 'operator': 'virtual21', 'cost': 5, 'count': 14}
# {'country': 'india', 'operator': 'virtual21', 'cost': 4, 'count': 5552} Параша все на чек падает 0/12 12 - чеков
# {'country': 'indonesia', 'operator': 'virtual21', 'cost': 5.4, 'count': 109}
# {'country': 'kyrgyzstan', 'operator': 'virtual21', 'cost': 1, 'count': 4}
# {'country': 'mauritius', 'operator': 'virtual21', 'cost': 3, 'count': 15}
# {'country': 'nicaragua', 'operator': 'virtual23', 'cost': 3.8, 'count': 1000} Тоже наебалово с кол-вом номеров. 1/10 прошелю 8/10 на чеке
# {'country': 'zimbabwe', 'operator': 'virtual21', 'cost': 3, 'count': 8}


country_dict =[
{'country': 'zimbabwe', 'operator': 'virtual21'},
{'country': 'zimbabwe', 'operator': 'virtual21'},
{'country': 'zimbabwe', 'operator': 'virtual21'},
{'country': 'zimbabwe', 'operator': 'virtual21'},
{'country': 'zimbabwe', 'operator': 'virtual21'},
{'country': 'zimbabwe', 'operator': 'virtual21'},
{'country': 'mauritius', 'operator': 'virtual21'},
{'country': 'nicaragua', 'operator': 'virtual23'},
{'country': 'egypt', 'operator': 'virtual21'}
    ]

def buy_number(country=None):
    default_country = country_dict[country]
    token = API_KEY_5SIM
    current_country = default_country["country"]
    current_operator = default_country['operator']
    product = 'facebook'
    
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    number = requests.get(f'https://{DOMAIN}/v1/user/buy/activation/' + current_country + '/' + current_operator + '/' + product, headers=headers)
    if number.text ==  'no free phones' and len(country_dict) != country:
        logging.info(number.text)
        country+=1
        # main.Facebook().wrote_csv(status='Не было номеров', country_number=current_country, operator_number=current_operator)
        if len(country_dict) == country:
            country=0
            return buy_number(country)
        return buy_number(country)
    elif len(country_dict) == country:
        logging.info('Список стран закончился')
        raise print('Список стран для номеров закончился')
    else:
        number = number.json()
        logging.info('Ответ покупки номера 5sim %s', number)
        if number['status'] != "RECEIVED" and number['status'] != "PENDING":
            logging.info('Не смог купить номер 5sim %s', number)
            time.sleep(10)
            country+=1
            return buy_number(country)
        else:
            return number

def get_sms_status(id):
    token = API_KEY_5SIM
    id = str(id)
    n = int(0)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    status = requests.get(f'https://{DOMAIN}/v1/user/check/' + id, headers=headers).json()

    while len(status['sms'])==0 and n < 15:
        time.sleep(10)
        status = requests.get(f'https://{DOMAIN}/v1/user/check/' + id, headers=headers).json()
        logging.info(f'Статус повторной активаций: {status}')
        n+=1
    if len(status['sms'])==0:
        logging.info(f'Смс не пришла, статус активаций: {status}')
        return status['sms']
    else:
        logging.info(f'Смс: {status}')
        return status['sms'][0]['code']

def ban_phone_number(id):
    token = API_KEY_5SIM
    id = str(id)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    status = requests.get(f'https://{DOMAIN}/v1/user/ban/' + id, headers=headers)
    logging.info(f'Статус бана смс заявки: {status}')


def finish_orfer(id):
    token = API_KEY_5SIM
    id = str(id)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    status = requests.get(f'https://{DOMAIN}/v1/user/finish/' + id, headers=headers)
    logging.info(f'Статус закрытия смс заявки: {status}')




def get_all_price():
    """Получение списка стран с ценой"""
    product = 'facebook'

    headers = {
        'Accept': 'application/json',
    }

    params = (
        ('product', product),
    )



    response = requests.get('https://5sim.net/v1/guest/prices', headers=headers, params=params)
    response = response.json()
    get_value_country(response['facebook'])


def get_value_country(json, rate=None):
    """Получение выгодной и качественной страны"""
    country_emp = ''
    operator_emp = ''
    count_emp = 0 
    for country, operator_list in json.items():
        for operator, price_and_count_list in operator_list.items():
            if price_and_count_list['count'] > 1:
                current_cost = price_and_count_list['cost']
                if current_cost < 6:
                    cost = current_cost
                    country_emp = country
                    operator_emp = operator
                    count_emp = price_and_count_list['count']
                    result = {
                        'country' : country_emp,
                        'operator' : operator_emp,
                        'cost' : cost,
                        'count' : count_emp,
                    }
                    print(result)

get_all_price()