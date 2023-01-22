import requests
from smsactivate.api import SMSActivateAPI
import time



SMS_ACTIVATE_URL = "https://api.sms-activate.org/stubs/handler_api.php?"
API_KEY_SMS = '6d4c2b3Acbf7e763A8f68648ff88c7c6'



sa = SMSActivateAPI(API_KEY_SMS)

# 24 {'cost': 6, 'count': 2001} Камбоджа хуйня собачья
# 36 {'cost': 8.5, 'count': 104508} Канада
# 73 {'cost': 9, 'count': 7696} Бразилия Более менее
# 22 {'cost': 6.5, 'count': 2229} Индия ТОж не валидная хуйнюшка
# 7 {'cost': 9, 'count': 10197} Малайзия # Хуже чем Бразилия
# 0 {'cost': 4, 'count': 63288}  Россия
# 12 {'cost': 4.5, 'count': 13299} США (виртуальные)
# 11 {'cost': 8, 'count': 1060} Кыргызстан
# 16 {'cost': 9, 'count': 5817} Англия
# 34 Эстония кайф
# 187 = Сша Тест нет номеров всегда
country_list = [73, 34,  11, 34, 16, 7]




def get_number(n=1):
    default_country = country_list[n]
    number = sa.getNumberV2(service="fb,", country=default_country) # {'activation_id': 000000000, 'phone': 79999999999}
    print(number)
    error = number.get('error')
    if error == "NO_NUMBERS":
        print(error)
        time.sleep(10)
        n+=1
        number = get_number(n)
        return number
    else:
        return number





def get_activate(id, n=0):
    id = int(id)
    time.sleep(10)
    status = sa.getStatus(id=id)
    print(status)
    if status == "STATUS_WAIT_CODE" and n < 3:
        n+=1
        get_activate(id, n)
    elif n == 3:
        return status
    else:
        return status[-5:]


def close_status(id, status = None):
    id = int(id)
    status = sa.setStatus(id=id, status=status) # id и отмена активаций
    print(status)
    return status


# Цены по странам
# countries = sa.getPrices(service='fb')
# for id_country, servise_list in countries.items():
#     for servise, count_and_cost in servise_list.items():
#         if count_and_cost['count'] > 100 and count_and_cost['cost'] < 10:
#             print(id_country,count_and_cost)

