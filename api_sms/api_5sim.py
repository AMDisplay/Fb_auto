import requests
import logging
import time


API_KEY_5SIM = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDYyNjM3MjcsImlhdCI6MTY3NDcyNzcyNywicmF5IjoiN2ZhZmQ1YjI1MWY3NmM5OGI5YThkNDY3NDBiOTVhMDAiLCJzdWIiOjE0MDk3ODF9.xvSchlmDf37N4F5msHJJBGGJ3qrjb-eQdn5BqApayszno7RywRCNIhKGQqRMbSGq0MfJDkMUZjm-sutTnDIcWy3SCpiiD2aPlYaN828qntZEVqdkfcNEIjU88fLpLq9niy8xnFEp0gry-6vU1TUdoldylnSkeLKKLBJB0S0RqT8mznN1XUqDOv7NiOc6neF3Pdb-IpWBZanrVltyeT8mKFvkkDJ_JJhm2FVAKIvAnm8k8IxC3DInKk4iOuWt6eyolbsigaTHvUBcrEP18yQqjdffWJPoEvOwP38ot4cbYnPnorWZpv6wVe0U9ErcwMPOpiROTmp1j1J9mTONVktmQg'
DOMAIN = "5sim.net"



# {'country': 'argentina', 'operator': 'virtual21', 'cost': 9, 'count': 5} 0/2
# {'country': 'bangladesh', 'operator': 'virtual4', 'cost': 9.4, 'count': 2786} 0/2
# {'country': 'cambodia', 'operator': 'virtual23', 'cost': 5, 'count': 1000} 0/2 
# {'country': 'cambodia', 'operator': 'virtual35', 'cost': 8.84, 'count': 1000}0/2
# {'country': 'canada', 'operator': 'virtual12', 'cost': 5.6, 'count': 145727} 0/2 1 - тест 10 1/9 для цены норм
# {'country': 'canada', 'operator': 'virtual23', 'cost': 8.4, 'count': 1000} 0/2 Проходит хорошо, смс не приходит 5 тест 10 0/9 дял цены плохо
# {'country': 'canada', 'operator': 'virtual35', 'cost': 8.4, 'count': 1000} 0/2 Проходит хорошо, смс не приходит
# {'country': 'canada', 'operator': 'virtual8', 'cost': 5, 'count': 175} 0/2 Проходит хорошо, смс не приходит 2 тест 10
# {'country': 'china', 'operator': 'virtual23', 'cost': 4.3, 'count': 1000} 0/2 Проходит хорошо, смс не приходит
# {'country': 'colombia', 'operator': 'virtual21', 'cost': 9, 'count': 33} Не приходят смс 1/5
# {'country': 'congo', 'operator': 'virtual4', 'cost': 8.8, 'count': 528} 4/5
# {'country': 'denmark', 'operator': 'virtual35', 'cost': 8.84, 'count': 1000} Не было номеров
# {'country': 'egypt', 'operator': 'virtual21', 'cost': 5, 'count': 94} 1/2 3 тест 10 0/9 - Плохо но надо еще тестить
# {'country': 'england', 'operator': 'virtual34', 'cost': 9, 'count': 1248} Оценка - 5/5
# {'country': 'england', 'operator': 'virtual4', 'cost': 8, 'count': 8014} 4/5
# {'country': 'gambia', 'operator': 'virtual21', 'cost': 5, 'count': 2} Не было номеров
# {'country': 'haiti', 'operator': 'virtual4', 'cost': 8.7, 'count': 601} 4/5
# {'country': 'india', 'operator': 'virtual21', 'cost': 4, 'count': 25} Не было номеров
# {'country': 'kyrgyzstan', 'operator': 'virtual21', 'cost': 1, 'count': 2} Нет номеров
# {'country': 'malaysia', 'operator': 'virtual21', 'cost': 6, 'count': 3} Нет номеров
# {'country': 'mauritius', 'operator': 'virtual21', 'cost': 3, 'count': 2} Нет номеров
# {'country': 'mongolia', 'operator': 'virtual7', 'cost': 7, 'count': 1000} 1/2 4 тест 9 (4/9) - Отлично за свою цену И смс все принимает, сажать на топ прокси
# {'country': 'nicaragua', 'operator': 'virtual23', 'cost': 3.8, 'count': 1000} 3/5. смс пришли 5/14
# {'country': 'philippines', 'operator': 'virtual4', 'cost': 8.4, 'count': 2778} Не было номеров
# {'country': 'russia', 'operator': 'beeline', 'cost': 5, 'count': 185} Не приходят смс
# {'country': 'russia', 'operator': 'mts', 'cost': 5, 'count': 2658} Не приходят смс
# {'country': 'russia', 'operator': 'rostelecom', 'cost': 5, 'count': 140} Не приходят смс
# {'country': 'russia', 'operator': 'tele2', 'cost': 5, 'count': 686} Не приходят смс
# {'country': 'senegal', 'operator': 'virtual4', 'cost': 9.4, 'count': 807} test
# {'country': 'tanzania', 'operator': 'virtual21', 'cost': 9, 'count': 2} 1/1 но после упал на чек
# {'country': 'usa', 'operator': 'virtual8', 'cost': 4.34, 'count': 3720} 0/1
# {'country': 'vietnam', 'operator': 'virtual16', 'cost': 6, 'count': 791}
# {'country': 'vietnam', 'operator': 'virtual17', 'cost': 6, 'count': 7}
# {'country': 'vietnam', 'operator': 'virtual23', 'cost': 8.4, 'count': 1000}
# {'country': 'zambia', 'operator': 'virtual21', 'cost': 9, 'count': 7}


country_dict =[
    {'country': 'tanzania', 'operator': 'virtual21'},
    {'country': 'usa', 'operator': 'virtual8'}, 
    {'country': 'vietnam', 'operator': 'virtual16'},
    {'country': 'vietnam', 'operator': 'virtual17'},
    {'country': 'senegal', 'operator': 'virtual4'},
    ]
# 
#  
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
    if number.text ==  'no free phones' and len(country_dict) != country: # list index out of range
        logging.info('Нет доступных номеров %s', number.text)
        country+=1
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

    while len(status['sms'])==0 and n < 10:
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