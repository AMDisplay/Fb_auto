import re


def get_proxy():
    """Получение прокси для профиля"""
    with open('proxy_list.txt', 'r') as f:
        nums = f.read().splitlines()
    list_proxy = []
    for i in nums:
        match_ip = re.findall(r'([0-9]{1,}[.][0-9]{1,}[.][0-9]{1,}[.][0-9]{1,})[:]([\d]{4,5})[:]([\w]{1,})[:]([\w]{1,})', i)
        list_proxy.append(match_ip)
    result = chech_proxy_on_use(list_proxy)
    return result


def chech_proxy_on_use(list_proxy):
    """Контроль количества использования одного прокси"""
    index_proxy_in_list = 0
    count_use_proxy = 0
    proxy_counter = {
        'proxy' : list_proxy[index_proxy_in_list],
        'use' : count_use_proxy
    }
    if count_use_proxy < 50:
        count_use_proxy+=1
        return proxy_counter['proxy']
    else:
        count_use_proxy = 0
        index_proxy_in_list+=1
        return proxy_counter['proxy']









#     count = 0
# while count < 5:
#     count+=1
#     for i in list_proxy:
#         print(i)
