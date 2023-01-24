import requests
import time
import sys
import os
import logging
import re
import csv
import random
import subprocess
import threading
import pickle
from pathlib import Path
from api_sms import api_5sim
from api_sms import sms_activate
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
import list_of_settings
import curve
import tkinter as tk
import numpy as np



UserAgent = UserAgent()


API_KEY = "302949221d20300738e52ce0046a2b48"
URL = "http://local.adspower.com:50725"
USER_ID = "h98ot4"
GROUP_ID = "1836292"




class Facebook(threading.Thread):

    def __init__(self, country, number_proxy, file_name, count_run) -> None:
        threading.Thread.__init__(self)
        self.country = country
        self.number_proxy = number_proxy
        self.file_name = file_name
        self.lock = threading.RLock()
        self.count_run = count_run



    def run(self):
        """Основная логика работы"""
        n = int(0)
        while n < self.count_run:
            logging.info(f'Попытка номер {n}')
            try:
                status_api = self.get_status_api(URL)
                if status_api['code'] != 0:
                    print(status_api["msg"])
            except Exception:
                print("Проблема подключения к апи")
                sys.exit()
            current_proxy = get_proxy(self.number_proxy)
            new_profile = self.create_profile(URL,current_proxy)
            driver = self.start_profile(URL,new_profile["response"])
            data = self.click_on_registraion(driver)
            self.add_fields_in_reg_and_buy_number(data, new_profile["response"], payload=new_profile['payload'])
            
            n+=1



    def move_coordinate_calculation(self ,points, action):
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


    def wrote_csv(self, file_name, password = None, phone = None, status = None, id_account = None, cookies = None, payload = None,country_number = None, operator_number = None, driver = None, manager_id = None, eeab_token = None):
        path = Path('csv', file_name)
        if cookies is None: # По странам с говном
            ua = driver.execute_script("return navigator.userAgent")
            with open(str(path), "a", newline="") as file:
                colums = ['phone','password', 'id_account', "cookies", 'status', 'ua']
                account = {
                        'phone' : phone,
                        'password' : password,
                        'id_account': id_account,
                        'cookies': cookies,
                        'status' : status,
                        'ua': ua
                    }
                writer = csv.DictWriter(file, fieldnames=colums, extrasaction='ignore', delimiter = ';')
                if not file_name:
                    writer.writeheader()
                writer.writerow(account)
        if cookies is not None: # Только успешные со всей инфой
            with open("csv\For_myself.csv", "a", newline="") as file:
                colums = ['phone','password', 'id_account', "cookies", 'payload', "country_number", "operator_number"]
                account = {
                        'phone' : phone,
                        'password' : password,
                        'id_account': id_account,
                        'cookies': cookies,
                        'payload': payload,
                        "country_number" : country_number,
                        "operator_number" : operator_number
                    }
                writer = csv.DictWriter(file, fieldnames=colums, extrasaction='ignore', delimiter = ';')
                if not file_name:
                    writer.writeheader()
                writer.writerow(account)
        if cookies is not None: # Только успешные на продажу
            payload = payload['fingerprint_config']['ua']
            with open("csv\All_S.csv", "a", newline="") as file:
                colums = ['phone','password', 'manager_id', 'eeab_token',  "cookies",  'payload']
                account = {
                        'phone' : phone,
                        'password' : password,
                        'manager_id': manager_id,
                        'eeab_token': eeab_token,
                        'cookies': cookies,
                        'payload': payload,
                    }
                writer = csv.DictWriter(file, fieldnames=colums, extrasaction='ignore', delimiter = ';')
                if not file_name:
                    writer.writeheader()
                writer.writerow(account)
        



    def write_text_input(self, action, text):
        text = str(text) 
        for letter in text:
            action.key_action.send_keys(letter)
            action.perform()
            time.sleep(random.uniform(0.2,0.4))


    def get_status_api(self,url):
        """Проверка АПИ на статус"""
        return requests.get(url + "/status").json()


    def generaited_password(self):
        chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        n = 0
        password =''
        while n != 8:
            password += random.choice(chars)
            n+=1
        return password


    def chech_checkpoint(self,data, id_number,password,phone, new_profile):
        profile_id = new_profile['data']['id']
        driver = data['driver']
        sms_activate.close_status(id_number,status=8 )
        logging.info('Аккаунт на чеке')
        self.lock.acquire()
        self.wrote_csv(password=password,phone=phone,status="Check", file_name=self.file_name, id_account=profile_id, driver=driver)
        self.lock.release()
        self.delete_account(new_profile=new_profile, driver=driver)


    def create_profile(self,url,proxy):
        """Создает профиль"""
        self.lock.acquire()
        logging.info('Создание профиля')
        url = url + "/api/v1/user/create"
        payload = { #№
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
                "ua": f"{random.choice(list_of_settings.ua)}",
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
                "proxy_host":proxy[0],
                "proxy_port":proxy[1],
                "proxy_user":proxy[2],
                "proxy_password":proxy[3],
            }
            }
        headers = {
            'Content-Type': 'application/json'
            }
        # self.wrote_browser_settings(settings=payload)
        ip = requests.get(f"{proxy[4]}")
        logging.info(f'Настройки браузера {payload}')
        logging.info(f'ip = {ip.text}')
        time.sleep(1)
        response = requests.request("POST", url, headers=headers, json=payload)
        self.lock.release()
        logging.info(f'{response.json()}')
        data = {
            'response' :response.json(),
            'payload' : payload
        }
        return data


    def delete_account(self,new_profile, driver = None):
        self.lock.acquire()
        url = URL + "/api/v1/user/delete"
        profile_id = new_profile['data']['id']
        logging.info('Закрытие профиля')
        time.sleep(1)
        requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
        payload = {
        "user_ids": [
            f"{profile_id}"
        ]
        }

        headers = {
        'Content-Type': 'application/json'
        }
        logging.info('Удаление профиля')
        self.lock.release()
        time.sleep(1)
        response = requests.request("POST", url, headers=headers, json=payload)
        print(response.text)


    def change_profile_name(self,profile_id,driver):
        logging.info('Успешная регистрация')
        logging.info('Закрытие профиля')
        self.lock.acquire()
        requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
        logging.info('Меняю имя профиля')
        url = URL + "/api/v1/user/update"

        payload = {
        "user_id": f"{profile_id}",
        "name": "Success",
        }

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, json=payload)
        time.sleep(1)
        self.lock.release()
        print(response.text)


    def start_profile(self,url, new_profile):
        """Запускает только что созданный профиль"""
        logging.info('Запуск профиля')
        self.lock.acquire()
        profile_id = new_profile['data']['id'] #№
        logging.info(f'ID профиля {profile_id}')
        open_profile = requests.get(url + '/api/v1/browser/start?user_id=' + profile_id).json()
        time.sleep(1)
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
        time.sleep(10)
        logging.info('Открываю фейсбук')
        driver.get("https://m.facebook.com/")
            # self.wrote_browser_settings(settings=profile_id)
        # time.sleep(2)
        # driver.quit()
        # requests.get(url + '/api/v1/browser/stop?user_id=' + id_profile).json()
        self.lock.release()
        return driver

            
    def click_on_registraion(self, driver):
        logging.info('Нажимаю на регистрацию')
        action =  ActionBuilder(driver, duration=1)
        clickable = driver.find_element(By.XPATH, "//a[@id='signup-button']")
        size_window = driver.get_window_size() # Размер окна #№
        logging.info(f'Размер окна {size_window}')
        loc = clickable.location # Координаты элемента  
        height_window = size_window['height']/2
        width_window = size_window['width']/2
        points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc) # координаты движения курсора
        last_coord = self.move_coordinate_calculation(points, action)
        time.sleep(0.2)
        data = {
            "driver": driver,
            "action": action,
            "last_coord": last_coord
        }
        # self.wrote_browser_settings(settings=size_window)
        return data


    def add_fields_in_reg_and_buy_number(self, data, new_profile, payload):
        name = random.choice(list_of_settings.name) 
        surename = random.choice(list_of_settings.surename) 
        wait = WebDriverWait(data["driver"], 20)
        action = data['action']
        list_of_month = ['July', 'Feb', 'Mart', 'Apr' 'Jun', 'Jul', 'May', 'Au', 'Sep', 'Oct', 'Nov', 'Dec']

        try:
            wait.until(lambda x: x.find_element(By.XPATH, "//span[@data-sigil='name_step_title_text']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            lang = wait.until(lambda x: x.find_element(By.XPATH, "//span[@data-sigil='name_step_title_text']"))
            if lang.text != "What's your name?":
                logging.info('Меняю язык')
                eng = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Eng"))
                loc_eng = eng.location # коорды
                points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_eng) # расчет передвижения
                last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение


        logging.info('Имя')
        elem_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='firstname']"))
        loc_elem_name = elem_name.location # коорды
        points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_elem_name) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
        self.write_text_input(action, name)

        logging.info('Фамилия')
        elem_second_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='lastname']"))
        loc_second_name = elem_second_name.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_second_name) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
        self.write_text_input(action, surename)

        logging.info('Подтверждаю ФИО')
        but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        loc_but = but.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        logging.info('Месяц рожденья')
        select_elem_birthday_month = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_month']"))
        loc_elem_birthday_month = select_elem_birthday_month.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_month) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"])
        self.write_text_input(action, text=random.choice(list_of_month))

        logging.info('День рожденья')
        select_elem_birthday_day = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_day']"))
        loc_elem_birthday_day = select_elem_birthday_day.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_day) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"])
        self.write_text_input(action, text=random.randrange(0, 26))

        logging.info('Год рожденья')
        select_elem_birthday_year = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_year']"))
        loc_select_elem_birthday_year = select_elem_birthday_year.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_birthday_year) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"])
        self.write_text_input(action, text=random.randrange(1990, 2002))

        logging.info('Подтверждаю рождение')
        but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        loc_but = but.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        logging.info('Вбиваю телефон')
        elem_mail = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_email__']"))
        loc_elem_mail = elem_mail.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_mail) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        logging.info('Жду телефон')
        response = sms_activate.get_number(country=self.country) #№
        logging.info(f'Ответ номера {response}')
        country_number = response['countryCode']
        operator_number = response['countryCode']
        # self.wrote_browser_settings(settings=response)
        id_number = response.get('activationId')
        phone = response['phoneNumber']
        self.write_text_input(action, text=phone)

        logging.info('Подтверждаю телефон')
        but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        loc_but = but.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
        time.sleep(random.randrange(2,3))

        logging.info('Указываю пол')
        select_elem_sex_woman = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='sex'][@value='1']"))
        loc_select_elem_sex_woman = select_elem_sex_woman.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_sex_woman) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        logging.info('Подтвержадаю пол')
        but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        loc_but = but.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
        time.sleep(random.randrange(2,3))

        logging.info('Генерирую пароль')
        elem_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_passwd__']"))
        loc_elem_password = elem_password.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_password) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
        password = self.generaited_password()
        time.sleep(1)
        self.write_text_input(action, text=password)

        logging.info('Подтверждаю пароль на странице')
        but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit'][@name='submit']"))
        loc_elem_confirm = but.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            
        time.sleep(40)

        if data['driver'].current_url.find("action_dialog") > 0:
            logging.info('Аккаунт существует')
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
            loc_but = but.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            try:
                logging.info('Ищу поле для пароля из смс')
                wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
            except:
                logging.info('Чекпоинт загрузи внутри action-dialog')
                self.chech_checkpoint(data, id_number, password,phone, new_profile)
            else:
                logging.info('Рега прошла, подверждение смс внутри action-dialog')
                self.accept_number_code(data, id_number, name=name, surename=surename, password=password, phone=phone, new_profile=new_profile)
        elif data['driver'].current_url.find("error") > 0:
            logging.info('error загрузка')
            self.chech_checkpoint(data, id_number, password,phone, new_profile)
        elif data['driver'].current_url.find("checkpoint") > 0:
            logging.info('checkpoint')
            self.chech_checkpoint(data, id_number, password,phone, new_profile)
        else:
            try:
                logging.info('Ищу Not now')
                wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Not now"))
            except:
                logging.info('Не нашел правильной кнопки =  какая-то неведомая хуйня')
                self.chech_checkpoint(data, id_number, password,phone, new_profile)
            else:
                logging.info('Рега прошла, подверждение смс')
                elem_confirm = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Not now"))
                loc_elem_confirm = elem_confirm.location # коорды
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # расчет передвижения
                last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
                self.accept_number_code(data, id_number, password=password, phone=phone, new_profile=new_profile, payload=payload, last_coord = last_coord, country_number = country_number,operator_number = operator_number)


    def accept_number_code(
        self,
        data, 
        id_number, 
        password = None, 
        phone = None, 
        new_profile = None,
        last_coord = None,
        country_number = None,
        operator_number = None, 
        payload = None
        ):
        profile_id = new_profile['data']['id']
        driver = data['driver']
        wait = WebDriverWait(driver, 15)
        code_sms = sms_activate.get_activate(id_number) # код из смс
        if len(code_sms) > 8:
            logging.info('смс не пришла')
            self.chech_checkpoint(data, id_number, password,phone, new_profile)
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
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
        self.write_text_input(action=data['action'], text=code_sms)

        time.sleep(1)
        code_confirm_button = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Confirm"))
        loc_code_confirm_button = code_confirm_button.location # коорды
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_confirm_button) # расчет передвижения
        last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижениt

        cookies = driver.get_cookies()

        manager_id = self.find_account_manager_id(driver=driver)
        eeab_token = self.find_eeab_token(driver=driver)
        self.wrote_csv(file_name=self.file_name, id_account=profile_id ,password=password,phone=phone,status="Success", cookies=cookies, payload=payload, country_number=country_number, operator_number=operator_number, manager_id=manager_id,eeab_token=eeab_token)
        sms_activate.close_status(id_number, status=6)
        self.change_profile_name(profile_id=profile_id, driver=driver)


    def find_account_manager_id(self, driver):
        logging.info('Получаю manager_id')
        driver.get('https://www.facebook.com/adsmanager/manage/')
        time.sleep(5)
        if driver.current_url.find("nav_source") > 0:
            current_url = driver.current_url
            idx_1 = current_url.find('act')+4
            idx_2 = current_url.find('&', idx_1)
            manager_id = current_url[idx_1:idx_2]
            logging.info(f'manager_id = {manager_id}')
            return manager_id
        else: 
            current_url = driver.current_url
            idx_1 = current_url.find('act')+4
            manager_id = current_url[idx_1:]
            logging.info(f'manager_id = {manager_id}')
            return manager_id


    def find_eeab_token(self, driver):
        logging.info('Получаю Eaab_Token')
        html_doc=driver.page_source
        idx = html_doc.find('EAAB')
        idx_2 = html_doc.find('"', idx)-1
        eeab_token = html_doc[idx:idx_2]
        logging.info(f'Eaab_Token = {eeab_token}')
        return eeab_token
        

        



if __name__ == '__main__':
    file_log = logging.FileHandler('py_log.log')
    console_out = logging.StreamHandler()
    format = " [%(threadName)s]: %(asctime)s: %(message)s"
    logging.basicConfig(handlers=(file_log, console_out),format=format, level=logging.INFO,
                        datefmt="%H:%M:%S", )

    # Facebook.get_status_api

    fb1 = Facebook(country=0, number_proxy=0, file_name="Nider.csv",count_run=50)
    fb1.start()
    time.sleep(10)
    fb2 = Facebook(country=1, number_proxy=1, file_name="Estonia.csv", count_run=50) # max 9
    fb2.start()
    time.sleep(10)
    fb3 = Facebook(country=2, number_proxy=2, file_name="England.csv", count_run=50)
    fb3.start()
    time.sleep(10)
    fb4 = Facebook(country=3, number_proxy=3, file_name="Canada.csv", count_run=50)
    fb4.start()

    # Eingrun4uf вбивать рандомный пароль руками - копировать
#  Тайланд, Австрия(ИНСТА) Дания (инста)