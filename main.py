import csv
import logging
import random
import sys
import threading
import time
from pathlib import Path
import json
import datetime
import os

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException

import curve
import list_of_settings
from api_sms import api_5sim, sms_activate
from get_proxy import get_proxy

# 680 при 10/10 стате и при 25 рублях надо продавать

API_KEY = "302949221d20300738e52ce0046a2b48"
URL = "http://local.adspower.com:50325"
USER_ID = "h98ot4"
GROUP_ID = "1836292"

sms_list = ['activate', '5sim']

therad_list = []



class Facebook(threading.Thread):

    def __init__(self, country = None, number_proxy= None, sms= None, count_run = None, options = None) -> None:
        threading.Thread.__init__(self)
        self.country = country
        self.number_proxy = number_proxy
        self.lock = threading.RLock()
        self.count_run = count_run
        self.event = threading.Event()
        self.sms = sms
        self.options = options

    def run(self):
        """Основная логика работы"""
        logging.info('Старт потока %s', threading.current_thread().name)
        try:
            try:
                status_api = self.get_status_api(URL)
                if status_api['code'] != 0:
                    print(status_api)
            except Exception:
                print("Проблема подключения к апи")
                sys.exit()
            current_proxy = get_proxy(self.number_proxy)
            new_profile = self.create_profile(current_proxy)
            driver = self.start_profile(URL, new_profile["response"])
            data = self.click_on_registraion(driver ,new_profile)
            self.add_fields_in_reg_and_buy_number(data, new_profile["response"], payload=new_profile['payload'])
        except WebDriverException:
            logging.critical('Лог из веба %s', new_profile)
            self.delete_account(new_profile=new_profile)
        except KeyError:
            logging.critical('Лог из ключа %s', new_profile)
            self.delete_account(new_profile=new_profile)

    def move_coordinate_calculation(self, points, action):
        coord = points.tolist()  # Преобразование многомерного (N массива np) в список питон
        for point in coord:
            point_x = point[0]
            point_y = point[1]
            action.pointer_action.move_to_location(point_x, point_y)
            action.perform()
        action.pointer_action.click()
        action.perform()
        self.event.wait(timeout=5)
        return coord[-1]

    def wrote_csv( 
        self,
        password=None,
        phone=None,
        status=None,
        cookies=None,
        payload=None,
        country_number=None,
        operator_number=None,
        manager_id=None,
        eeab_token=None
    ):
        filename = 'csv\For_analysis.json'
        time = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
        data = {
            'time':time,
            'status': status,
            'payload': payload,
            'country_number' : country_number,
            'operator_number': operator_number
        }

        if os.stat(filename).st_size == 0:
            with open(filename, "w") as file:
                json.dump([data], file, indent=4)
        else:
            with open(filename) as fp:
                listObj = json.loads(fp.read())
                listObj.append(data)
            with open(filename, 'w') as json_file:
                json.dump(listObj, json_file, 
                                    indent=4,  
                                    separators=(',',': '))
            
        if cookies is not None:  # Только успешные на продажу, все норм
            payload = payload['fingerprint_config']['ua']
            with open('csv\For_sale.txt', "a") as file:
                lines = [phone, password, manager_id, eeab_token, cookies, payload]
                file.writelines("%s\t" % line for line in lines)
                file.write('\n')

    def chech_checkpoint(self, id_number, new_profile, phone, status, payload, country_number, operator_number):
        if self.sms == 'activate':
            sms_activate.close_status(id_number,status=8 )
        else:
            api_5sim.ban_phone_number(id_number)
        logging.info('Аккаунт на чеке')
        self.lock.acquire()
        self.wrote_csv(phone=phone, status=status, payload=payload, country_number=country_number, operator_number=operator_number)
        self.lock.release()
        self.delete_account(new_profile=new_profile)

    def create_profile(self,proxy):
        """Создает профиль"""
        self.lock.acquire()
        logging.info('Создание профиля')
        url = URL + "/api/v1/user/create"
        payload = { #№
            "name": "Fb",
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
        self.lock.acquire()
        self.event.wait(timeout=2)
        ip = requests.get(f"{proxy[4]}")
        self.lock.release()
        logging.info(f'ip = {ip.text}')
        response = requests.request("POST", url, headers=headers, json=payload).json()
        n = 0
        while response['code'] == -1 and  n < 5:
            try:
                logging.info(response["msg"])
                self.event.wait(2)
                response = requests.request("POST", url, headers=headers, json=payload).json()
                n+=1
            except:
                logging.info('Ошибка создания профиля после 5 попыток')
        logging.info(f'{response}')
        data = {
            'response' :response,
            'payload' : payload
        }
        self.lock.release()
        return data

    def delete_account(self,new_profile):
        self.lock.acquire()
        url = URL + "/api/v1/user/delete"
        profile_id = new_profile['data']['id']
        logging.info('Закрытие профиля')
        response = requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
        n = 0
        while response['msg'] == "Too many request per second, please check" and  n < 5:
            try:
                logging.info(f' Статус закрытия профиля {response["msg"]}')
                self.event.wait(3)
                response = requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
                n+=1
            except:
                logging.info('Ошибка закрытия профиля после 5 попыток')
        self.event.wait(timeout=1)
        self.lock.release()
        payload = {
        "user_ids": [
            f"{profile_id}"
        ]
        }

        headers = {
        'Content-Type': 'application/json'
        }
        logging.info('Удаление профиля')
        self.lock.acquire()
        #  [Thread-5]: 02:38:24: [j4wclp4] is being used by [DIsplay1997@yandex.ru] mailbox users and cannot be deleted
        # Профиль удален {'data': {}, 'msg': 'wrong user_id or wrong user_ids', 'code': 9108}

        response = requests.request("POST", url, headers=headers, json=payload).json()
        n=0
        while response['msg'] == "Too many request per second, please check"  and n < 5:
            try:
                logging.info(f' Статус удаления профиля {response["msg"]}')
                self.event.wait(3)
                response = requests.request("POST", url, headers=headers, json=payload).json()
                n+=1
            except:
                logging.info('Ошибка удаления профиля после 5 попыток')
        if response['msg'] == 'wrong user_id or wrong user_ids':
            raise Exception ('Ошибка получения ид профиля либо упал браузер, профиль удален успешно')
        if response['code'] == -1:
            logging.info('Повторное удаление профиля')
            return self.delete_account(new_profile=new_profile)
        self.lock.release()
        logging.info("Профиль удален %s", response)
        logging.info('Поток %s завершил работу', threading.current_thread().name)

    # def change_profile_name(self,profile_id,driver):
        # logging.info('Успешная регистрация')
        # logging.info('Закрытие профиля')
        # self.lock.acquire()
        # requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
        # self.event.wait(timeout=1)
        

        # logging.info('Меняю имя профиля')
        # url = URL + "/api/v1/user/update"

        # payload = {
        # "user_id": f"{profile_id}",
        # "name": "Success",
        # }

        # headers = {
        #     'Content-Type': 'application/json'
        # }
        # response = requests.request("POST", url, headers=headers, json=payload)
        # self.lock.release()
        # print(response.text)

    def start_profile(self,url, new_profile):
        """Запускает только что созданный профиль"""
        logging.info('Запуск профиля')
        self.lock.acquire()
        self.event.wait(3)
        profile_id = new_profile['data']['id'] #№
        logging.info(f'ID профиля {profile_id}')
        open_profile = requests.get(url + '/api/v1/browser/start?user_id=' + profile_id).json()
        driver = open_profile['data']['webdriver']
        options = self.options
        # options.page_load_strategy = 'eager' # тетс
        options.add_experimental_option("debuggerAddress", open_profile["data"]["ws"]["selenium"])
        driver = webdriver.Chrome(service=Service(driver), options=options)
        list_win = driver.window_handles
        driver.switch_to.window(list_win[1])
        driver.switch_to.window(list_win[0])
        driver.close()
        driver.switch_to.window(list_win[1])
        logging.info('Открываю фейсбук')
        driver.get("https://m.facebook.com/")
        while driver.current_url.find('facebook') < 0:
            self.event.wait(5)
            driver.get("https://m.facebook.com/")
        self.lock.release()
        return driver
     
    def click_on_registraion(self, driver, new_profile):
        logging.info('Нажимаю на регистрацию')
        wait = WebDriverWait(driver, 20)
        action =  ActionBuilder(driver, duration=1)

        if len(driver.find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
            driver.refresh()
            self.event.wait(5)
            if len(driver.find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
                self.delete_account(new_profile=new_profile)
        try:
            clickable = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='signup-button']"))
        except Exception:
            self.delete_account(new_profile=new_profile)
        else:
            self.event.wait(5)
            size_window = driver.get_window_size() # Размер окна #№
            logging.info(f'Размер окна {size_window}')
            loc = clickable.location
            height_window = size_window['height']/2
            width_window = size_window['width']/2
            points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc) # координаты движения курсора
            last_coord = self.move_coordinate_calculation(points, action)
            while driver.current_url.find('reg') < 0:
                self.event.wait(5)
                clickable = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='signup-button']"))
                points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc)
                logging.info('Повторное нажатие на регу')
                self.move_coordinate_calculation(points, action)
            self.event.wait(timeout=0.2)
            data = {
                "driver": driver,
                "action": action,
                "last_coord": last_coord
            }
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
        try:
            elem_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='firstname']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_name = elem_name.location # коорды
            points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_elem_name) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            self.write_text_input(action, name)

        logging.info('Фамилия')
        try:
            elem_second_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='lastname']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_second_name = elem_second_name.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_second_name) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            self.write_text_input(action, surename)

        logging.info('Подтверждаю ФИО')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        logging.info('Месяц рожденья')
        try:
            select_elem_birthday_month = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_month']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_birthday_month = select_elem_birthday_month.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_month) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.choice(list_of_month))

        logging.info('День рожденья')
        try: 
            select_elem_birthday_day = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_day']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_birthday_day = select_elem_birthday_day.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_day) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.randrange(0, 26))

        logging.info('Год рожденья')
        try:
            select_elem_birthday_year = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_year']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_select_elem_birthday_year = select_elem_birthday_year.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_birthday_year) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.randrange(1990, 2002))

        logging.info('Подтверждаю рождение')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        logging.info('Вбиваю телефон') # Please enter a valid phone number.
        try:
            elem_mail = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_email__']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_mail = elem_mail.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_mail) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        if self.sms == 'activate':
            logging.info('Жду телефон sms_activate')
            response = sms_activate.get_number(country=self.country) #№
            logging.info(f'Ответ номера {response}')
            country_number = response['countryCode']
            operator_number = response['countryCode']
            id_number = response.get('activationId')
            phone = response['phoneNumber']
            logging.info('Вбиваю телефон')
            self.write_text_input(action, text=phone)
        else:
            logging.info('Жду телефон 5sim')
            response = api_5sim.buy_number(country=self.country) #№ 
            country_number = response['country']
            operator_number = response['operator']
            id_number = response.get('id')
            phone = response['phone']
            logging.info('Вбиваю телефон')
            self.write_text_input(action, text=phone)


        logging.info('Подтверждаю телефон')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            time.sleep(random.randrange(2,3))

        logging.info('Указываю пол')
        try:
            select_elem_sex_woman = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='sex'][@value='1']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_select_elem_sex_woman = select_elem_sex_woman.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_sex_woman) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение

        logging.info('Подтвержадаю пол')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            time.sleep(random.randrange(2,3))

        logging.info('Генерирую пароль')
        try:
            elem_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_passwd__']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_password = elem_password.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_password) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            password = self.generaited_password()
            self.event.wait(timeout=1)
            self.write_text_input(action, text=password)

        logging.info('Подтверждаю пароль на странице')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit'][@name='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_confirm = but.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            
        self.event.wait(timeout=35)

        if data['driver'].current_url.find("action_dialog") > 0:
            logging.info('Аккаунт существует')
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
            loc_but = but.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            while len(data['driver'].find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
                logging.info('Ошибка подключения после action-dialog')
                data['driver'].back()
                but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
                loc_but = but.location # коорды
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # расчет передвижения
                last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
                self.event.wait(10)
            try:
                logging.info('Ищу Not now внутри чека')
                elem_confirm = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Not now"))
                try:
                    logging.info('Ищу поле для пароля из смс внутри чека ')
                    wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
                except:
                    logging.info('Чекпоинт загрузи внутри action-dialog')
                    self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Чекпоинт загрузи внутри action-dialog', payload=payload , country_number=country_number, operator_number=operator_number)
                else:
                    logging.info('Рега прошла, подверждение смс внутри action-dialog')
                    self.accept_number_code(data, id_number, password, phone, new_profile, last_coord, country_number, operator_number, payload)
            except:
                logging.info('Не нашел правильной кнопки =  какая-то неведомая хуйня')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Ошибка в Now now', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                logging.info('Рега прошла внутри чека, подверждение смс')
                loc_elem_confirm = elem_confirm.location # коорды
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # расчет передвижения
                last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижени
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)

        elif data['driver'].current_url.find("error") > 0:
            logging.info('error загрузка')
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='error загрузка', payload=payload , country_number=country_number, operator_number=operator_number)

        elif data['driver'].current_url.find("checkpoint") > 0:
            logging.info('checkpoint')
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Chekpoint внутhи action', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            if len(data["driver"].find_elements(By.PARTIAL_LINK_TEXT, ('Please enter a valid phone number'))) != 0:
                logging.info('Не валидный телефон')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Не валидный номер', payload=payload , country_number=country_number, operator_number=operator_number)
            try:
                logging.info('Ищу Not now')
                elem_confirm = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Not now"))
            except:
                logging.info('Не нашел правильной кнопки =  какая-то неведомая хуйня')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Ошибка в Now now', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                logging.info('Рега прошла, подверждение смс')
                loc_elem_confirm = elem_confirm.location # коорды
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # расчет передвижения
                last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижени
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)

    def accept_number_code(
        self,
        data, 
        id_number, 
        password, 
        phone, 
        new_profile,
        payload,
        last_coord,
        country_number,
        operator_number, 
        ):
        driver = data['driver']
        wait = WebDriverWait(driver, 15)
        if self.sms == 'activate':
            code_sms = sms_activate.get_activate(id_number)
            if code_sms == "STATUS_WAIT_CODE":
                logging.info(f'Смс не пришла, возвращаемое значениие активаций: {code_sms}')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Sms ne prishla', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            code_sms = api_5sim.get_sms_status(id_number)
            if len(code_sms) == 0:
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Sms ne prishla', payload=payload , country_number=country_number, operator_number=operator_number)

        logging.info('Проверка на подключение')
        while len(driver.find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
            driver.refresh()
            self.event.wait(10)
        logging.info('Вбиваю смс')
        try:
            code_form = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
        except:
            logging.info("Не смог вбить смс")
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Не смог вбить смс', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            loc_code_form = code_form.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_form) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            self.write_text_input(action=data['action'], text=code_sms)
        self.event.wait(3)
        logging.info('Проверка на валидность смс')
        if len(driver.find_elements(By.PARTIAL_LINK_TEXT, ('Check your SMS for a message with your code and try again.'))) != 0:
            logging.info('Смс не валидна, повторный запрос смс')
            try:
                elem_didnt_code = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, ("I didn't get the code")))
            except:
                logging.info("Смс не валидна")
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Sms ne prishla', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                loc_elem_didnt_code = elem_didnt_code.location # коорды
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_didnt_code) # расчет передвижения
                last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
            try:  
                elem_send_sms_code_again = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, ("Send Code Again")))
            except:
                logging.info("Проблема с отправкой кода смс")
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Проблема с отправкой смс', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                loc_elem_send_sms_code_again = elem_send_sms_code_again.location # коорды
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_send_sms_code_again) # расчет передвижения
                last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижение
                logging.info('Повторное получение смс')
                if self.sms == 'activate':
                    code_sms = sms_activate.set_status(id=id_number)
                    logging.info(f'Повторное значение смс sms_activate {code_sms}')
                else:
                    code_sms = api_5sim.get_sms_status(id_number)
                    logging.info(f'Повторное значение смс 5sim {code_sms}')
                logging.info('Вбиваю смс повторно')
                if len(driver.find_elements(By.PARTIAL_LINK_TEXT, ('Check your SMS for a message with your code and try again.'))) != 0:
                    logging.info("Проблема с повторной отправкой смс")
                    self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Проблема с повторной отправкой', payload=payload , country_number=country_number, operator_number=operator_number)
                self.write_text_input(action=data['action'], text=code_sms)
                self.event.wait(3)
        logging.info('Смс валидна, подтверждаю')
        try:
            code_confirm_button = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Confirm"))
        except:
            logging.info("Проблема с нажатием кнопки при подтверждений смс")
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Проблема с нажатием кнопки', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            loc_code_confirm_button = code_confirm_button.location # коорды
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_confirm_button) # расчет передвижения
            last_coord = self.move_coordinate_calculation(points, data["action"]) # передвижениt
        self.options.page_load_strategy = 'eager'
        manager_id = self.find_account_manager_id(driver=driver)
        eeab_token = self.find_eeab_token(driver=driver)
        cookies = json.dumps(driver.get_cookies())
        self.wrote_csv(password=password, phone=phone, status='Success', cookies=cookies, payload=payload, country_number=country_number, operator_number=operator_number, manager_id=manager_id,eeab_token=eeab_token)
        if self.sms == 'activate':
            sms_activate.close_status(id_number, status=6)
        else:
            api_5sim.finish_orfer(id=id_number)
        logging.info("Успешная регистрация")
        self.delete_account(new_profile=new_profile)

    def find_account_manager_id(self, driver):
        logging.info('Получаю manager_id')
        while driver.current_url.find('adsmanager') < 0:
            driver.get('https://www.facebook.com/adsmanager/manage/')
            logging.info('Повторная попытка загрузить adsmanager')
            self.event.wait(5)
        while driver.current_url.find('act') < 0:
            logging.info('Обновление страницы с manager_id')
            driver.refresh()
            self.event.wait(30) # Оптимально 30
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
        idx_2 = html_doc.find('"', idx)
        eeab_token = html_doc[idx:idx_2]
        logging.info(f'Eaab_Token = {eeab_token}')
        return eeab_token

    def write_text_input(self, action, text):
        text = str(text) 
        for letter in text:
            action.key_action.send_keys(letter)
            action.perform()
            time.sleep(random.uniform(0.2,0.4))

    def get_status_api(self, url):
        """Проверка АПИ на статус"""
        return requests.get(url + "/status").json()

    def generaited_password(self):
        chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        n = 0
        password =''
        while n != 10:
            password += random.choice(chars)
            n+=1
        return password

def add_new_thread(country, number_proxy, sms, options):
    therad_list.append({'thread': None, 'country': country, 'number_proxy': number_proxy, 'sms': sms, "options":options})
	
def start_thread():
    logging.info("Старт потоков")
    for thread in therad_list:
        if thread['thread'] is None:
            thread['thread'] = Facebook(country=thread['country'], number_proxy=thread['number_proxy'], sms=thread['sms'], options=thread['options'])
            thread['thread'].start()
            time.sleep(5)
        else:
            if thread['thread'].is_alive() is False:
                thread['thread'] = Facebook(country=thread['country'], number_proxy=thread['number_proxy'], sms=thread['sms'],  options=thread['options'])
                thread['thread'].start()
                time.sleep(5)	
                
if __name__ == '__main__':

    file_log = logging.FileHandler('py_log.log')
    console_out = logging.StreamHandler()
    format = " [%(threadName)s]: %(asctime)s: %(message)s"
    logging.basicConfig(handlers=(file_log, console_out),format=format, level=logging.INFO,
                        datefmt="%H:%M:%S", )

    logging.info("Инициализация потоков")
    # add_new_thread(country=0, number_proxy=0, sms=sms_list[1], options=Options())
    # add_new_thread(country=1, number_proxy=1, sms=sms_list[1], options=Options()) # Ахуенная прокси
    # add_new_thread(country=2, number_proxy=2, sms=sms_list[1], options=Options())
    # add_new_thread(country=3, number_proxy=3, sms=sms_list[1],  options=Options()) # Ахуенная прокси
    add_new_thread(country=4, number_proxy=4, sms=sms_list[1],  options=Options())
    start_thread()
    n = 1
    while n != 0:
        time.sleep(450) # 420 для одной успешной реги если 5 потоков то за каждый поток надо добавлять по 10 сек (5 потоков это 40 прибавочных сек т.к. 1 не учитывается)
        if threading.active_count() - 1 < len(therad_list):
            start_thread()
            n-=1