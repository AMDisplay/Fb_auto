import requests
import logging
import time
import main


API_KEY_5SIM = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDYyNjM3MjcsImlhdCI6MTY3NDcyNzcyNywicmF5IjoiN2ZhZmQ1YjI1MWY3NmM5OGI5YThkNDY3NDBiOTVhMDAiLCJzdWIiOjE0MDk3ODF9.xvSchlmDf37N4F5msHJJBGGJ3qrjb-eQdn5BqApayszno7RywRCNIhKGQqRMbSGq0MfJDkMUZjm-sutTnDIcWy3SCpiiD2aPlYaN828qntZEVqdkfcNEIjU88fLpLq9niy8xnFEp0gry-6vU1TUdoldylnSkeLKKLBJB0S0RqT8mznN1XUqDOv7NiOc6neF3Pdb-IpWBZanrVltyeT8mKFvkkDJ_JJhm2FVAKIvAnm8k8IxC3DInKk4iOuWt6eyolbsigaTHvUBcrEP18yQqjdffWJPoEvOwP38ot4cbYnPnorWZpv6wVe0U9ErcwMPOpiROTmp1j1J9mTONVktmQg'
DOMAIN = "5sim.net"
# @ - На тесте
# {'country': 'canada', 'operator': 'virtual12', 'cost': 5.6, 'count': 145727} 4/5 5 1 4 2 3
# {'country': 'canada', 'operator': 'virtual23', 'cost': 8.4, 'count': 1000} 0/2 Проходит хорошо, смс не приходит 5 тест 10 0/9 дял цены плохо TEST 1 2 3 4 5 
# {'country': 'canada', 'operator': 'virtual35', 'cost': 8.4, 'count': 1000} 0/2 Проходит хорошо, смс не приходит TEST 2 3 4 1 5 
# {'country': 'canada', 'operator': 'virtual8', 'cost': 5, 'count': 175} 4/5 3 4 5 1 2
# {'country': 'colombia', 'operator': 'virtual21', 'cost': 9, 'count': 33} Не приходят смс 1/5 TEST Нет номеров 5 1 2 3 4
# {'country': 'congo', 'operator': 'virtual4', 'cost': 8.8, 'count': 528} 4/5 1 2 3 4 5 
# {'country': 'denmark', 'operator': 'virtual35', 'cost': 8.84, 'count': 1000} 2 3 1 4 5 
# {'country': 'egypt', 'operator': 'virtual21', 'cost': 5, 'count': 94} 1/2 Чеков много 3 4 2 1 @ 
# {'country': 'england', 'operator': 'virtual34', 'cost': 9, 'count': 1248} Оценка - 5/5 4 5 1 3 2 
# {'country': 'england', 'operator': 'virtual4', 'cost': 8, 'count': 8014} 4/5 5 1 3 2 4
# {'country': 'haiti', 'operator': 'virtual4', 'cost': 8.7, 'count': 601} 4/5 2 3 5 1 4 
# {'country': 'india', 'operator': 'virtual21', 'cost': 4, 'count': 25}  3 2 1 4 @ 5 (не записан)
# {'country': 'mauritius', 'operator': 'virtual21', 'cost': 3, 'count': 2}  1 4 2 3 @ 
# {'country': 'mongolia', 'operator': 'virtual7', 'cost': 7, 'count': 1000} 1/2 4 тест 9 (4/9) - Отлично за свою цену И смс все принимает, сажать на топ прокси 2 5 3 1 @ 4 (не записан)
# {'country': 'nicaragua', 'operator': 'virtual23', 'cost': 3.8, 'count': 1000} 3/5. смс пришли 5/14 3 1 4 2 @ 
# {'country': 'senegal', 'operator': 'virtual4', 'cost': 9.4, 'count': 807} 2/5 4 2 5 3 @ 1 (не записан)
# {'country': 'tanzania', 'operator': 'virtual21', 'cost': 9, 'count': 2} 5 3 1 @  2 (не записан)


country_dict =[
{'country': 'tanzania', 'operator': 'virtual21'},
{'country': 'nicaragua', 'operator': 'virtual23'},
{'country': 'senegal', 'operator': 'virtual4'},
{'country': 'england', 'operator': 'virtual4'},
{'country': 'denmark', 'operator': 'virtual35'},
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
        logging.info('Нет доступных номеров %s', number.text)
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




# def get_all_price():
#     """Получение списка стран с ценой"""
#     product = 'facebook'

#     headers = {
#         'Accept': 'application/json',
#     }

#     params = (
#         ('product', product),
#     )



#     response = requests.get('https://5sim.net/v1/guest/prices', headers=headers, params=params)
#     response = response.json()
#     get_value_country(response['facebook'])


# def get_value_country(json, rate=None):
#     """Получение выгодной и качественной страны"""
#     country_emp = ''
#     operator_emp = ''
#     count_emp = 0 
#     for country, operator_list in json.items():
#         for operator, price_and_count_list in operator_list.items():
#             if price_and_count_list['count'] > 1:
#                 current_cost = price_and_count_list['cost']
#                 if current_cost < 10:
#                     cost = current_cost
#                     country_emp = country
#                     operator_emp = operator
#                     count_emp = price_and_count_list['count']
#                     result = {
#                         'country' : country_emp,
#                         'operator' : operator_emp,
#                         'cost' : cost,
#                         'count' : count_emp,
#                     }
#                     print(result)

# get_all_price()