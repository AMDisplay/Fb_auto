import requests
import time
import sys
import os
import logging
import re
import csv
import random
import multiprocessing
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


API_KEY = "302949221d20300738e52ce0046a2b48"
URL = "http://local.adspower.com:50725"
USER_ID = "h98ot4"
GROUP_ID = "1836292"

FILENAME = "Kirgiz.csv"



def move_coordinate_calculation(points, action):
    coord = points.tolist() # Преобразование многомерного (N массива np) в список питон
    for point in coord:
        point_x = point[0]
        point_y = point[1]
        action.pointer_action.move_to_location(point_x,point_y)
        action.perform()
    action.pointer_action.click()
    action.perform()
    time.sleep(5)
    return coord[-1]


def write_text_input(action, text):
    text = str(text)
    for letter in text:
        action.key_action.send_keys(letter)
        action.perform()
        time.sleep(0.4)


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


def chech_checkpoint(data, id_number, name, surename,password,phone, new_profile):
    sms_activate.close_status(id_number,status=8 )
    data['driver'].close()
    data['driver'].quit()
    logging.info('Аккаунт на чеке')
    wrote_csv(name=name,surename=surename,password=password,phone=phone,status="Check")
    delete_account(new_profile)
    os.execv(sys.executable, ['python'] + sys.argv)


def take_id_profile(new_profile):
    print(new_profile)
    """Вытаскивает ид созданного акка"""
    return new_profile['data']['id']


def create_profile(url,proxy):
    """Создает профиль"""
    logging.info('Создание профиля')
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
    ip = requests.get("http://node-ua-3.astroproxy.com:10281/api/changeIP?apiToken=9f796d93469124de")
    logging.info(f'ip = {ip.text}')
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()


def delete_account(new_profile):
    logging.info('Удаляю профиля')
    profile_id = new_profile['data']['id']
    url = URL + "/api/v1/user/delete"

    payload = {
    "user_ids": [
        f"{profile_id}"
    ]
    }

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.text)


def change_profile_name(new_profile):
    logging.info('Меняю имя профиля')
    profile_id = new_profile['data']['id']
    url = URL + "/api/v1/user/update"

    payload = {
    "user_ids": [
        f"{profile_id}",
    ],
    "name": "Success",
    }

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.text)


def start_profile(url, id_profile):
    """Запускает только что созданный профиль"""
    logging.info('Запуск профиля')
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
    logging.info('Открываю фейсбук')
    driver.get("https://m.facebook.com/")
    # time.sleep(2)
    # driver.quit()
    # requests.get(url + '/api/v1/browser/stop?user_id=' + id_profile).json()
    return driver

        
def click_on_registraion(driver):
    logging.info('Нажимаю на регистрацию')
    action =  ActionBuilder(driver, duration=1)
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


def add_fields_in_reg_and_buy_number(data, new_profile):
    name = random.choice(list_of_settings.name)
    surename = random.choice(list_of_settings.surename)
    wait = WebDriverWait(data["driver"], 20)
    action = data['action']
    list_of_month = ['J', 'F', 'Mart', 'Ap' 'Jun', 'Jul', 'May', 'Au', 'S', 'O', 'N', 'D']

    lang = wait.until(lambda x: x.find_element(By.XPATH, "//span[@data-sigil='name_step_title_text']"))

    if lang.text != "What's your name?":
        logging.info('Меняю язык')
        eng = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Eng"))
        loc_eng = eng.location # коорды
        points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_eng) # расчет передвижения
        last_coord = move_coordinate_calculation(points, data["action"]) # передвижение

    logging.info('Имя')
    elem_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='firstname']"))
    loc_elem_name = elem_name.location # коорды
    points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_elem_name) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
    write_text_input(action, name)

    logging.info('Фамилия')
    elem_second_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='lastname']"))
    loc_second_name = elem_second_name.location
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_second_name) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
    write_text_input(action, surename)

    logging.info('Подтверждаю ФИО')
    but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
    loc_but = but.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение

    logging.info('Месяц рожденья')
    select_elem_birthday_month = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_month']"))
    loc_elem_birthday_month = select_elem_birthday_month.location
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_month) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"])
    write_text_input(action, text=random.choice(list_of_month))

    logging.info('День рожденья')
    select_elem_birthday_day = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_day']"))
    loc_elem_birthday_day = select_elem_birthday_day.location
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_day) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"])
    write_text_input(action, text=random.randrange(0, 26))

    logging.info('Год рожденья')
    select_elem_birthday_year = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_year']"))
    loc_select_elem_birthday_year = select_elem_birthday_year.location
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_birthday_year) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"])
    write_text_input(action, text=random.randrange(1990, 2002))

    logging.info('Подтверждаю рождение')
    but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
    loc_but = but.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение

    logging.info('Вбиваю телефон')
    elem_mail = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_email__']"))
    loc_elem_mail = elem_mail.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_mail) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение

    logging.info('Жду телефон')
    response = sms_activate.get_number()
    id_number = response.get('activationId')
    phone = response['phoneNumber']
    write_text_input(action, text=phone)

    logging.info('Подтверждаю телефон')
    but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
    loc_but = but.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
    time.sleep(3)

    logging.info('Указываю пол')
    select_elem_sex_woman = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='sex'][@value='1']"))
    loc_select_elem_sex_woman = select_elem_sex_woman.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_sex_woman) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение

    logging.info('Подтвержадаю пол')
    but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
    loc_but = but.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
    time.sleep(3)

    logging.info('Генерирую пароль')
    elem_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_passwd__']"))
    loc_elem_password = elem_password.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_password) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
    password = generaited_password()
    time.sleep(1)
    write_text_input(action, text=password)

    logging.info('Подтверждаю пароль на странице')
    but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit'][@name='submit']"))
    loc_elem_confirm = but.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
        
    time.sleep(40)

    if data['driver'].current_url.find("action_dialog") > 0:
        logging.info('Аккаунт существует')
        but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
        loc_but = but.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
        last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
        try:
            logging.info('Ищу поле для пароля из смс')
            wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
        except:
            logging.info('Чекпоинт загрузи внутри action-dialog')
            chech_checkpoint(data, id_number, name, surename,password,phone, new_profile)
        else:
            logging.info('Рега прошла, подверждение смс внутри action-dialog')
            accept_number_code(data, id_number, name=name, surename=surename, password=password, phone=phone, new_profile=new_profile)
    try:
        logging.info('Ищу Not now')
        wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Not now"))
    except:
        logging.info('Не нашел правильной кнопки = либо чек, либо ошибка, либо еще какая-то неведомая хуйня')
        chech_checkpoint(data, id_number, name, surename,password,phone, new_profile)
    else:
        logging.info('Рега прошла, подверждение смс')
        elem_confirm = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Not now"))
        loc_elem_confirm = elem_confirm.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # расчет передвижения
        last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
        accept_number_code(data, id_number, name=name, surename=surename, password=password, phone=phone, new_profile=new_profile, last_coord = last_coord)


def accept_number_code(
    data, 
    id_number, 
    name = None, 
    surename = None, 
    password = None, 
    phone = None, 
    new_profile = None,
    last_coord = None,
    ):
    profile_id = new_profile['data']['id']
    driver = data['driver']
    wait = WebDriverWait(driver, 15)
    code_sms = sms_activate.get_activate(id_number) # код из смс
    if len(code_sms) > 8:
        logging.info('смс не пришла')
        chech_checkpoint(data, id_number, name, surename,password,phone, new_profile)
    # info_sms = api_5sim.get_sms_status(driver_and_id_num['id_number']) # Значение ид номера заказа
    # info_sms = info_sms.json()

    # try:
    #     driver.find_element(By.XPATH, "//div[@id='reg_error_inner']")
    # except Exception:
    #     print('Телефон уже использован')
    #     ban_phone_number(info_sms=info_sms)
    #     driver.quit()
    #     raise
    # try:
    #     code_sms = info_sms['sms'][0]['code']
    # except Exception as sms_not_confirm:
    #     print(f'Отсутствует код в смс')
    #     api_5sim.ban_phone_number(info_sms=info_sms)
    #     raise
    code_form = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
    loc_code_form = code_form.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_form) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижение
    write_text_input(action=data['action'], text=code_sms)

    time.sleep(1)
    code_confirm_button = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Confirm"))
    loc_code_confirm_button = code_confirm_button.location # коорды
    points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_confirm_button) # расчет передвижения
    last_coord = move_coordinate_calculation(points, data["action"]) # передвижениt
    wrote_csv(name=name,surename=surename,password=password,phone=phone,status="Success")
    sms_activate.close_status(id_number, status=6)
    driver.close()
    driver.quit()
    requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
    change_profile_name(new_profile=new_profile)
    # subprocess.Popen(['python', 'main.py'], start_new_session=True)


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
    add_fields_in_reg_and_buy_number(data, new_profile)





if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
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