import requests
import time
import sys
import os
import re
import csv
import threading
import random
import api_5sim
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from fake_useragent import UserAgent
from get_proxy import get_proxy
import sms_activate
import list_of_settings
import curve
import tkinter as tk
import numpy as np


UserAgent = UserAgent()


API_KEY = "4304212080cc384c8f667102d1852af7"
URL = "http://local.adspower.com:50325"
USER_ID = "h98ot4"
GROUP_ID = "1836292"

FILENAME = "Malaziya.csv"


def move_coordinate_calculation(points, action):
    coord = points.tolist() # Преобразование многомерного (N массива np) в список питон
    for point in coord:
        point_x = point[0]
        point_y = point[1]

        action.pointer_action.move_to_location(point_x,point_y)
        action.perform()


        print(point)
    action.pointer_action.click()
    action.perform()
    time.sleep(5)
    return coord[-1]


def wrote_csv(name = None, surename = None, password = None, phone = None, status = None):
    with open(FILENAME, "a", newline="") as file:
        colums = ['name', 'surename', 'password', 'phone', 'status']
        user = {
                'name': name,
                'surename' : surename,
                'password' : password,
                'phone' : phone,
                'status' : status
            }
        writer = csv.DictWriter(file, delimiter = ';', fieldnames=colums)
        writer.writeheader()
        writer.writerow(user)


def get_status_api(url):
    """Проверка АПИ на статус"""
    return requests.get(url + "/status").json()


def generaited_password():
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    n = 0
    password =''
    while n != 8:
        password += random.choice(chars)
        n+=1
    return password


def take_id_profile(new_profile):
    print(new_profile)
    """Вытаскивает ид созданного акка"""
    return new_profile['data']['id']


def create_profile(url,proxy):
    """Создает профиль"""
    url = url + "/api/v1/user/create"
    payload = {
        "name": "mobile",
        "group_id": "1836292",
        "domain_name": "google.com",
        "repeat_config": [
            "0"
        ],
        "country": "us",
        "fingerprint_config": {
            "language": [
            "uk-UA", "uk", "en-US", "en" #   ru-RU,ru,en-US,en ["en-US","en","zh-CN","zh"]
            ],
            "ua": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.107 Safari/537.36",
            "flash": "block",
            "scan_port_type": "1",
            "screen_resolution": f'{random.choice(list_of_settings.screen_resolution)}', # ex 1024_600 or default or random
            "fonts": [
            "all"
            ],
            "longitude": "180",
            "latitude": "90",
            "webrtc": "proxy",
            "do_not_track": "true", # Отслеживание действий на сайте
        },
        "user_proxy_config": {
            "proxy_soft": "other", # other or no_proxy
            "proxy_type":"http",
            "proxy_host":proxy[0][0],
            "proxy_port":proxy[0][1],
            "proxy_user":proxy[0][2],
            "proxy_password":proxy[0][3],
        }
        }
    headers = {
        'Content-Type': 'application/json'
        }
    requests.get("http://node-ua-48.astroproxy.com:10457/api/changeIP?apiToken=4ab44ab9172361f2")
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


def start_profile(url, id_profile):
    """Запускает только что созданный профиль"""
    id_profile = str(id_profile)
    open_profile = requests.get(url + '/api/v1/browser/start?user_id=' + id_profile).json()
    driver = open_profile['data']['webdriver']
    options = Options() # Класс опций в браузере
    options.add_experimental_option("debuggerAddress", open_profile["data"]["ws"]["selenium"]) # Создание кастомной опций
    # options.add_argument('')
    driver = webdriver.Chrome(service=Service(driver), options=options) # Добавление кастомной опций 1 - путь до юзерагента, 2 = передаваемые кастомные настройки браузер
    list_win = driver.window_handles
    driver.switch_to.window(list_win[1])
    driver.switch_to.window(list_win[0])
    driver.close()
    driver.switch_to.window(list_win[1])
    driver.get("https://m.facebook.com/")
    # time.sleep(2)
    # driver.quit()
    # requests.get(url + '/api/v1/browser/stop?user_id=' + id_profile).json()
    return driver
    
        
def click_on_registraion(driver):
    action =  ActionBuilder(driver)
    clickable = driver.find_element(By.XPATH, "//a[@id='signup-button']")
    size_window = driver.get_window_size() # Размер окна
    loc = clickable.location # Координаты элемента
    height_window = size_window['height']/2
    width_window = size_window['width']/2
    points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc) # координаты движения курсора
    last_coord = move_coordinate_calculation(points, action)
    time.sleep(0.2)
    data = {
        "driver": driver,
        "action": action,
        "last_coord": last_coord
    }
    return data


def add_fields_in_reg_and_buy_number(data):
    name = random.choice(list_of_settings.name)
    surename = random.choice(list_of_settings.surename)
    wait = WebDriverWait(data["driver"], 15)
    action = data['action']
    elem_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='firstname']"))
    loc = elem_name.location # коорды
    points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
    time.sleep(1) # тут
    elem_second_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='lastname']"))
    action.move_to_element(elem_second_name).click(elem_second_name).send_keys(surename).perform()
    time.sleep(2)
    but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
    but.click()
    time.sleep(3)
    select_elem_birthday_day = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_day']"))
    # driver.switch_to.frame(select_elem_birthday_day)
    # checkbox = driver.find_element(By.NAME, "scroll_checkbox")
    time.sleep(5)
    # option_elements = select_elem_birthday_day.find_elements(By.TAG_NAME, 'option')
    # action.move_to_element(select_elem_birthday_day).click().pause(1).click().perform()
    # time.sleep(5)
    # action.move_to_element(option_elements[20]).pause(1).click().perform()
    # random = random.randrange(1, 27)
    # select_elem_birthday_day_drop = wait.until(lambda x: x.find_element(By.XPATH, f"//option[@value='2']"))
    # action.move_to_element(select_elem_birthday_day_drop).click().perform()
    # упало дроп меню
    # time.sleep(2)
    list_select_birthday_day = Select(select_elem_birthday_day)
    list_select_birthday_day.select_by_index(random.randrange(0, 26))
    select_elem_birthday_month = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_month']"))
    ActionChains(driver).move_to_element(select_elem_birthday_month).perform()
    list_select_birthday_month = Select(select_elem_birthday_month)
    list_select_birthday_month.select_by_index(random.randrange(1, 11))
    time.sleep(3)
    select_elem_birthday_year = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_year']"))
    ActionChains(driver).move_to_element(select_elem_birthday_year).perform()
    list_select_birthday_year = Select(select_elem_birthday_year)
    list_select_birthday_year.select_by_index(random.randrange(30,50))
    but.click()
    time.sleep(3)
    elem_mail = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_email__']"))
    response = sms_activate.get_number()
    # response = api_5sim.check_phone_on_free()
    id_number = response['activationId']
    phone = response['phoneNumber']
    elem_mail.clear()
    elem_mail.send_keys(f'{phone}')
    but.click()
    time.sleep(3)
    select_elem_sex_woman = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='sex'][@value='1']"))
    select_elem_sex_woman.click()
    but.click()
    time.sleep(3)
    elem_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_passwd__']"))
    elem_password.clear()
    password = generaited_password()
    time.sleep(3)
    elem_password.send_keys(f'{password}')
    cur_url = driver.current_url.find("action_dialog")
    if cur_url > 0:
        but = wait.until(lambda x: x.find_element(By.XPATH, "//form[@method='post'][@id=suma_create_account]"))
        but.click()
        accept_number_code(driver_and_id_num=driver_and_id_num, name=name, surename=surename, password=password, phone=phone)
    but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit'][@name='submit']"))
    time.sleep(3)
    but.click()
    driver_and_id_num = {
        'driver': driver,
        'id_number' : id_number
    }
    time.sleep(30)
    accept_number_code(driver_and_id_num=driver_and_id_num, name=name, surename=surename, password=password, phone=phone)


def accept_number_code(driver_and_id_num, name = None, surename = None, password = None, phone = None):
    driver = driver_and_id_num['driver']
    wait = WebDriverWait(driver, 15)
    code_sms = sms_activate.get_activate(driver_and_id_num['id_number']) # код из смс
    # info_sms = api_5sim.get_sms_status(driver_and_id_num['id_number']) # Значение ид номера заказа
    # info_sms = info_sms.json()

    # try:
    #     driver.find_element(By.XPATH, "//div[@id='reg_error_inner']")
    # except Exception:
    #     print('Телефон уже использован')
    #     ban_phone_number(info_sms=info_sms)
    #     driver.quit()
    #     raise
    cur_url = driver.current_url.find("checkpoint")
    if cur_url > 0:
        # api_5sim.cancel_phone(driver_and_id_num['id_number'])
        sms_activate.close_status(driver_and_id_num['id_number'],status=8 )
        driver.close()
        print('Аккаунт на чеке')
        wrote_csv(name=name,surename=surename,password=password,phone=phone,status="Check")
        os.execv(sys.executable, ['python'] + sys.argv)
    cur_url = driver.current_url.find("error")
    if cur_url > 0:
        # api_5sim.cancel_phone(driver_and_id_num['id_number'])
        sms_activate.close_status(driver_and_id_num['id_number'],status=8 )
        driver.close()
        print('Ошибка регистраций')
        wrote_csv(name=name,surename=surename,password=password,phone=phone,status="Error")
        os.execv(sys.executable, ['python'] + sys.argv)
    # try:
    #     code_sms = info_sms['sms'][0]['code']
    # except Exception as sms_not_confirm:
    #     print(f'Отсутствует код в смс')
    #     api_5sim.ban_phone_number(info_sms=info_sms)
    #     raise
    try:
        code_form = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
    except Exception as not_found_form:
       driver.close()
       print(f'Отсутствует элемент на странице {not_found_form}')
       wrote_csv(name=name,surename=surename,password=password,phone=phone,status="Not find elem")
       os.execv(sys.executable, ['python'] + sys.argv)
    code_form.clear()
    code_form.send_keys(code_sms)
    time.sleep(1)
    code_confirm_button = wait.until(lambda x: x.find_element(By.XPATH, "//a[@href='#']"))
    code_confirm_button.click()
    button_after_reg = wait.until(lambda x: x.find_element(By.XPATH, "//button[@tabindex='0']"))
    button_after_reg.click()
    wrote_csv(name=name,surename=surename,password=password,phone=phone,status="Success")
    sms_activate.close_status(driver_and_id_num['id_number'], status=6)


def main():
    """Основная логика работы"""
    try:
        status_api = get_status_api(URL)
        if status_api['code'] != 0:
            print(status_api["msg"])
    except Exception:
        print("Проблема подключения к апи")
        sys.exit()
    current_proxy = get_proxy()
    new_profile = create_profile(URL,current_proxy)
    id_profile = take_id_profile(new_profile)
    driver = start_profile(URL,id_profile)
    data = click_on_registraion(driver)
    # add_fields_in_reg_and_buy_number(data)





if __name__ == '__main__':
    main()
    # t1 = threading.Thread(target=main)
    # t1.start()
    # time.sleep(30)
    # t2 = threading.Thread(target=main)
    # t2.start()
    # time.sleep(30)
    # t3 = threading.Thread(target=main)
    # t3.start()
    # time.sleep(30)
    # t1.join()
    # t2.join()
    # t3.join()
    # print("Done!")


    # Eingrun4uf вбивать рандомный пароль руками - копировать
#  Тайланд, Австрия(ИНСТА) Дания (инста)