import requests
from smsactivate.api import SMSActivateAPI
import time



SMS_ACTIVATE_URL = "https://api.sms-activate.org/stubs/handler_api.php?"
API_KEY_SMS = '6d4c2b3Acbf7e763A8f68648ff88c7c6'



sa = SMSActivateAPI(API_KEY_SMS)

# 24 {'cost': 6, 'count': 2001} Камбоджа -
# 36 {'cost': 8.5, 'count': 104508} Канада any
# 73 {'cost': 9, 'count': 7696} Бразилия +
# 22 {'cost': 6.5, 'count': 2229} Индия -
# 7 {'cost': 9, 'count': 10197} Малайзия -
# 0 {'cost': 4, 'count': 63288}  Россия -
# 6 {'cost': 10.5, 'count': 55304} Индонезия -
# 12 {'cost': 4.5, 'count': 13299} США (виртуальные) -
# 11 {'cost': 8, 'count': 1060} Кыргызстан -
# 16 {'cost': 9, 'count': 5817} Англия +
# 48 {'cost': 10, 'count': 881} Нидерланды + kpn
# 33 {'cost': 10, 'count': 2670} Колумбия -
# 8 {'cost': 10, 'count': 1214} Кения - 
# 151 {'cost': 10, 'count': 251} чили -
# 34 Эстония  +
# 187 = Сша Тест нет номеров всегда
# 4 {'cost': 12.5, 'count': 3007} Филипины 1/7 и то не прошел
# 10 {'cost': 12.5, 'count': 3007} Вьетнам
# 14 {'cost': 7.5, 'count': 142} Гонконг нет
# 2 Казахстан ytn
# 54 Месика ytn
# 78	 Франция ytn
# 1	 Украина
# 148	 Армения
country_list = [48, 16, 36, 73, 34]




def get_number(country=None):
    default_country = country_list[country]
    number = sa.getNumberV2(service="fb,", country=default_country) # {'activation_id': 000000000, 'phone': 79999999999}
    print(number)
    error = number.get('error')
    if error == "NO_NUMBERS" or error == 'BAD_STATUS':
        print(error)
        time.sleep(10)
        country+=1
        return get_number(country)
    else:
        return number


def get_activate(id):
    id = int(id)
    n = int(0)
    status = sa.getStatus(id=id)
    print(status)
    while status == "STATUS_WAIT_CODE" and n < 3:
        time.sleep(10)
        status = sa.getStatus(id=id)
        print(status)
        n+=1
        
    if status == "STATUS_WAIT_CODE":
        return status
    else:
        return status[-5:]


def close_status(id, status = None):
    id = int(id)
    status = sa.setStatus(id=id, status=status) # id и отмена активаций
    print(status)
    return status


# Цены по странам
# countries = sa.getPrices(service='ig')
# for id_country, servise_list in countries.items():
#     for servise, count_and_cost in servise_list.items():
#         if count_and_cost['count'] > 100 and count_and_cost['cost'] < 10:
#             print(id_country,count_and_cost)

# # # 