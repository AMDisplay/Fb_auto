import re


def get_proxy(num_proxy):
    """Получение прокси для профиля"""
    with open('proxy_list.txt', 'r') as f:
        nums = f.read().splitlines()
    num = nums[num_proxy]
    return num.split("@")


# def chech_proxy_on_use(list_proxy):
#     """Контроль количества использования одного прокси"""
#     index_proxy_in_list = 0
#     count_use_proxy = 0
#     proxy_counter = {
#         'proxy' : list_proxy[index_proxy_in_list],
#         'use' : count_use_proxy
#     }
#     if count_use_proxy < 50:
#         count_use_proxy+=1
#         return proxy_counter['proxy']
#     else:
#         count_use_proxy = 0
#         index_proxy_in_list+=1
#         return proxy_counter['proxy']







#     count = 0
# while count < 5:
#     count+=1
#     for i in list_proxy:
#         print(i)
