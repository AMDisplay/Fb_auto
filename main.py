# coding: Windows-1251

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
from selenium.webdriver.chrome.options import Options, ChromiumOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys


import curve
import settings.list_of_settings as list_of_settings
from api_sms import api_5sim, sms_activate
from proxy.get_proxy import get_proxy

# 680 ��� 10/10 ����� � ��� 25 ������ ���� ���������

API_KEY = "302949221d20300738e52ce0046a2b48"
URL = "http://local.adspower.com:50325"
USER_ID = "h98ot4"
GROUP_ID = "1836292"

sms_list = ['activate', '5sim']

therad_list = []

EMAIL_TXT = 'csv\email.txt'
NEW_EMAIL_TXT = 'csv\\new_email.txt'






class Facebook(threading.Thread):

    def __init__(self, country = None, number_proxy= None, sms= None, count_run = None) -> None:
        threading.Thread.__init__(self)
        self.country = country
        self.number_proxy = number_proxy
        self.lock = threading.RLock()
        self.count_run = count_run
        self.event = threading.Event()
        self.sms = sms
        self.options = Options()

    def run(self):
        """�������� ������ ������"""
        logging.info('Start thread %s', threading.current_thread().name)
        try:
            try:
                status_api = self.get_status_api(URL)
                if status_api['code'] != 0:
                    print(status_api)
            except Exception:
                print("�������� ����������� � ���")
                sys.exit()
            current_proxy = get_proxy(self.number_proxy)
            new_profile = self.create_profile(current_proxy)
            driver = self.start_profile(URL, new_profile["response"])
            data = self.click_on_registraion(driver ,new_profile)
            self.add_fields_in_reg_and_buy_number(data, new_profile["response"], payload=new_profile['payload'])
        except WebDriverException:
            logging.critical('��� �� ���� %s', new_profile)
            self.delete_account(new_profile=new_profile)
        except KeyError:
            logging.critical('��� �� ����� %s', new_profile)
            self.delete_account(new_profile=new_profile)

    def move_coordinate_calculation(self, points, action):
        coord = points.tolist()  # �������������� ������������ (N ������� np) � ������ �����
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
        eeab_token=None,
        email=None
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
            
        if cookies is not None:  # ������ �������� �� �������, ��� ����
            payload = payload['fingerprint_config']['ua']
            # email = email[0]
            # email_pass = email[1]
            with open('csv\For_sale.txt', "a") as file:
                lines = [phone, password,manager_id, eeab_token, cookies, payload]
                file.writelines("%s\t" % line for line in lines)
                file.write('\n')

    def chech_checkpoint(self, id_number, new_profile, phone, status, payload, country_number, operator_number):
        if self.sms == 'activate':
            sms_activate.close_status(id_number,status=8 )
        else:
            api_5sim.ban_phone_number(id_number)
        logging.info('Account on check')
        self.lock.acquire()
        self.wrote_csv(phone=phone, status=status, payload=payload, country_number=country_number, operator_number=operator_number)
        self.lock.release()
        self.delete_account(new_profile=new_profile)

    def create_profile(self,proxy):
        """������� �������"""
        self.lock.acquire()
        logging.info('Create profile')
        url = URL + "/api/v1/user/create"
        payload = { #�
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
                "do_not_track": "true", # ������������ �������� �� �����
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
                logging.info('Error create profile after 5 try')
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
        logging.info('Close profile')
        response = requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
        n = 0
        while response['msg'] == "Too many request per second, please check" and  n < 5:
            try:
                logging.info(f'Status close profile {response["msg"]}')
                self.event.wait(3)
                response = requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
                n+=1
            except:
                logging.info('Error close profile after 5 try')
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
        logging.info('Deleting profile')
        self.lock.acquire()
        #  [Thread-5]: 02:38:24: [j4wclp4] is being used by [DIsplay1997@yandex.ru] mailbox users and cannot be deleted
        # ������� ������ {'data': {}, 'msg': 'wrong user_id or wrong user_ids', 'code': 9108}

        response = requests.request("POST", url, headers=headers, json=payload).json()
        n=0
        while response['msg'] == "Too many request per second, please check"  and n < 5:
            try:
                logging.info(f' Status deleting profile {response["msg"]}')
                self.event.wait(3)
                response = requests.request("POST", url, headers=headers, json=payload).json()
                n+=1
            except:
                logging.info('Error deletig profile after 5 try')
        if response['msg'] == 'wrong user_id or wrong user_ids':
            raise Exception ('error get id profile, profile delete success')
        if response['code'] == -1:
            logging.info('repeat deleting profile')
            return self.delete_account(new_profile=new_profile)
        self.lock.release()
        logging.info("profile deleted %s", response)
        logging.info('Thread %s end', threading.current_thread().name)

    # def change_profile_name(self,profile_id,driver):
        # logging.info('�������� �����������')
        # logging.info('�������� �������')
        # self.lock.acquire()
        # requests.get(URL + '/api/v1/browser/stop?user_id=' + profile_id).json()
        # self.event.wait(timeout=1)
        

        # logging.info('����� ��� �������')
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
        """��������� ������ ��� ��������� �������"""
        logging.info('Start profile')
        self.lock.acquire()
        self.event.wait(3)
        profile_id = new_profile['data']['id'] #�
        logging.info(f'ID profile {profile_id}')
        open_profile = requests.get(url + '/api/v1/browser/start?user_id=' + profile_id).json()
        driver = open_profile['data']['webdriver']
        self.options.add_argument("--disable-notifications")
        self.options.add_experimental_option("debuggerAddress", open_profile["data"]["ws"]["selenium"])
        driver = webdriver.Chrome(service=Service(driver), options=self.options)
        driver.maximize_window()
        list_win = driver.window_handles
        driver.switch_to.window(list_win[1])
        driver.switch_to.window(list_win[0])
        driver.close()
        driver.switch_to.window(list_win[1])
        logging.info('Open FB')
        driver.get("https://m.facebook.com/")
        while driver.current_url.find('facebook') < 0:
            self.event.wait(5)
            driver.get("https://m.facebook.com/")
        self.lock.release()
        return driver
     
    def click_on_registraion(self, driver, new_profile):
        wait = WebDriverWait(driver, 20)
        action =  ActionBuilder(driver, duration=1)
        logging.info('Check on cookie')
        if len(driver.find_elements(By.XPATH, "//button[@value='Allow essential and optional cookies']")) > 0:
            logging.info('Accept cookie')
            cookie_button = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Allow essential and optional cookies']"))
            size_window = driver.get_window_size() # ������ ���� #�
            loc = cookie_button.location
            height_window = size_window['height']/2
            width_window = size_window['width']/2
            points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc) # ���������� �������� �������
            last_coord = self.move_coordinate_calculation(points, action)
        if len(driver.find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
            driver.refresh()
            self.event.wait(5)
            if len(driver.find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
                self.delete_account(new_profile=new_profile)
        try:
            logging.info('Click on reg')
            clickable = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='signup-button']"))
        except Exception:
            self.delete_account(new_profile=new_profile)
        else:
            self.event.wait(5)
            size_window = driver.get_window_size() # ������ ���� #�
            logging.info(f'Size window {size_window}')
            loc = clickable.location
            height_window = size_window['height']/2
            width_window = size_window['width']/2
            points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc) # ���������� �������� �������
            last_coord = self.move_coordinate_calculation(points, action)
            while driver.current_url.find('reg') < 0:
                self.event.wait(5)
                clickable = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='signup-button']"))
                points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc)
                logging.info('repeat click on reg')
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
        wait = WebDriverWait(data["driver"], 40)
        action = data['action']
        list_of_month = ['July', 'Feb', 'Mart', 'Apr' 'Jun', 'Jul', 'May', 'Au', 'Sep', 'Oct', 'Nov', 'Dec']

        try:
            wait.until(lambda x: x.find_element(By.XPATH, "//span[@data-sigil='name_step_title_text']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            lang = wait.until(lambda x: x.find_element(By.XPATH, "//span[@data-sigil='name_step_title_text']"))
            if lang.text != "What's your name?":
                logging.info('Change lang')
                eng = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Eng"))
                loc_eng = eng.location # ������
                points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_eng) # ������ ������������
                last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������


        logging.info('Name')
        try:
            elem_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='firstname']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_name = elem_name.location # ������
            points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_elem_name) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            self.write_text_input(action, name)

        logging.info('Surename')
        try:
            elem_second_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='lastname']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_second_name = elem_second_name.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_second_name) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            self.write_text_input(action, surename)

        logging.info('Accept NS')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        logging.info('Mounth birthday')
        try:
            select_elem_birthday_month = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_month']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_birthday_month = select_elem_birthday_month.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_month) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.choice(list_of_month))

        logging.info('Day birthday')
        try: 
            select_elem_birthday_day = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_day']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_birthday_day = select_elem_birthday_day.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_day) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.randrange(0, 26))

        logging.info('Year birthday')
        try:
            select_elem_birthday_year = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_year']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_select_elem_birthday_year = select_elem_birthday_year.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_birthday_year) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.randrange(1990, 2002))

        logging.info('Accept birthday')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        logging.info('Put phone') # Please enter a valid phone number.
        try:
            elem_mail = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_email__']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_mail = elem_mail.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_mail) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        if self.sms == 'activate':
            logging.info('Waiting phone sms_activate')
            response = sms_activate.get_number(country=self.country) #�
            logging.info(f'Responce phone {response}')
            country_number = response['countryCode']
            operator_number = response['countryCode']
            id_number = response.get('activationId')
            phone = response['phoneNumber']
            logging.info('Add phone')
            self.write_text_input(action, text=phone)
        else:
            logging.info('Waiting phone 5sim')
            response = api_5sim.buy_number(country=self.country) #� 
            country_number = response['country']
            operator_number = response['operator']
            id_number = response.get('id')
            phone = response['phone']
            logging.info('Add phone')
            self.write_text_input(action, text=phone)


        logging.info('Accept phone')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            time.sleep(random.randrange(2,3))

        logging.info('Add sex')
        try:
            select_elem_sex_woman = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='sex'][@value='1']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_select_elem_sex_woman = select_elem_sex_woman.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_sex_woman) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        logging.info('Accept sex')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            time.sleep(random.randrange(2,3))

        logging.info('Generate password')
        try:
            elem_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_passwd__']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_password = elem_password.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_password) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            password = self.generaited_password()
            self.event.wait(timeout=1)
            self.write_text_input(action, text=password)

        logging.info('Accept password')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit'][@name='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_confirm = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            
        self.event.wait(timeout=35)

        if data['driver'].current_url.find("action_dialog") > 0:
            logging.info('Acc exist')
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            while len(data['driver'].find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
                logging.info('Error connect after action-dialog')
                data['driver'].back()
                but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
                loc_but = but.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) # ������ ������������
                last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
                self.event.wait(10)
            if len(data["driver"].find_elements(By.XPATH, "//input[@type='number']")) > 0:
                logging.info("Accept reg after without now now")
            try:
                logging.info('Try find OK in check')
                elem_confirm = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
                # try:
                #     logging.info('Finding field for password sms incide check')
                #     wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
                # except:
                #     logging.info('Check download in action-dialog')
                #     self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='�������� ������� ������ action-dialog', payload=payload , country_number=country_number, operator_number=operator_number)
                # else:
                #     logging.info('Reg success, accept sms incide action-dialog')
                #     self.accept_number_code(data, id_number, password, phone, new_profile, last_coord, country_number, operator_number, payload)
            except:
                logging.info('Not find right button')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='������ � Now now', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                logging.info('Reg success incide check, accepy sms')
                loc_elem_confirm = elem_confirm.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # ������ ������������
                last_coord = self.move_coordinate_calculation(points, data["action"]) # �����������
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)

        elif data['driver'].current_url.find("error") > 0:
            logging.info('error download')
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='error ��������', payload=payload , country_number=country_number, operator_number=operator_number)

        elif data['driver'].current_url.find("checkpoint") > 0:
            logging.info('checkpoint')
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Chekpoint ����h� action', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            if len(data["driver"].find_elements(By.PARTIAL_LINK_TEXT, ('Please enter a valid phone number'))) > 0:
                logging.info('Not valid phone')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='�� �������� �����', payload=payload , country_number=country_number, operator_number=operator_number)
            if len(data["driver"].find_elements(By.XPATH, "//input[@type='number']")) > 0:
                logging.info("reg accept withour not now")
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)
            if data['driver'].current_url.find("save") > 0:
                logging.info('reg accept, add sms')
                elem_confirm = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
                loc_elem_confirm = elem_confirm.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) # ������ ������������
                last_coord = self.move_coordinate_calculation(points, data["action"]) # �����������
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)
            else:
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='���-�� �� ��� � not now', payload=payload , country_number=country_number, operator_number=operator_number)

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
                logging.info(f'Sms not found {code_sms}')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Sms ne prishla', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            code_sms = api_5sim.get_sms_status(id_number)
            if len(code_sms) == 0:
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Sms ne prishla', payload=payload , country_number=country_number, operator_number=operator_number)

        logging.info('Check on connect')
        while len(driver.find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
            driver.refresh()
            self.event.wait(10)
        logging.info('Add sms')
        try:
            code_form = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='number']"))
        except:
            logging.info("Can't add sms")
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='�� ���� ����� ���', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            loc_code_form = code_form.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_form) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            self.write_text_input(action=data['action'], text=code_sms)
        self.event.wait(3)
        logging.info('Check on valid sms')
        if len(driver.find_elements(By.PARTIAL_LINK_TEXT, ('Check your SMS for a message with your code and try again.'))) != 0:
            logging.info('Sms not valid, retry get sms')
            try:
                elem_didnt_code = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, ("I didn't get the code")))
            except:
                logging.info("Sms not valid")
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Sms ne prishla', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                loc_elem_didnt_code = elem_didnt_code.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_didnt_code) # ������ ������������
                last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            try:  
                elem_send_sms_code_again = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, ("Send Code Again")))
            except:
                logging.info("Problem with send sms")
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='�������� � ��������� ���', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                loc_elem_send_sms_code_again = elem_send_sms_code_again.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_send_sms_code_again) # ������ ������������
                last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
                logging.info('Repeat add sms')
                if self.sms == 'activate':
                    code_sms = sms_activate.set_status(id=id_number)
                    logging.info(f'Repeating value sms sms_activate {code_sms}')
                else:
                    code_sms = api_5sim.get_sms_status(id_number)
                    logging.info(f'Repeating value sms 5sim {code_sms}')
                logging.info('Repeat adding sms')
                if len(driver.find_elements(By.PARTIAL_LINK_TEXT, ('Check your SMS for a message with your code and try again.'))) != 0:
                    logging.info("Problem with retry send sms")
                    self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='�������� � ��������� ���������', payload=payload , country_number=country_number, operator_number=operator_number)
                self.write_text_input(action=data['action'], text=code_sms)
                self.event.wait(3)
        logging.info('Sms valid')
        try:
            code_confirm_button = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Confirm"))
        except:
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='�������� � �������� ������', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            loc_code_confirm_button = code_confirm_button.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_confirm_button) # ������ ������������
            last_coord = self.move_coordinate_calculation(points, data["action"]) # �����������
        # self.lock.acquire()
        # email = self.get_email() # ������� ����� ������ [0] - email [1] = pass
        # self.lock.release()
        # self.send_code_on_email(driver=driver, action = data["action"], email=email, last_coord=last_coord, password=password) # ������ ���� �� �����
        # email_code = self.get_code_email(driver=driver, email=email)
        # self.confirm_email_in_fb(driver=driver, action=data['action'], email_code=email_code)
        # self.get_two_fa(driver=driver, action=data['action'], last_coord=last_coord)
        self.options.page_load_strategy = 'eager'
        manager_id = self.find_account_manager_id(driver=driver)
        eeab_token = self.find_eeab_token(driver=driver)
        cookies = json.dumps(driver.get_cookies())
        self.wrote_csv(password=password, phone=phone, status='Success', cookies=cookies, payload=payload, country_number=country_number, operator_number=operator_number, manager_id=manager_id,eeab_token=eeab_token)
        if self.sms == 'activate':
            sms_activate.close_status(id_number, status=6)
        else:
            api_5sim.finish_orfer(id=id_number)
        logging.info("Succes reg")
        self.delete_account(new_profile=new_profile)

    def get_email(self):
        logging.info('Get email from txt')
        if os.stat(EMAIL_TXT).st_size == 0:
            print('email text end')
        else:
            with open(EMAIL_TXT) as fp:
                email = fp.readline()


        with open(EMAIL_TXT) as infile, open(NEW_EMAIL_TXT, "w",) as outfile:
            for line in infile:
                if email not in line:
                    outfile.write(line)
        os.remove(EMAIL_TXT)
        os.rename(NEW_EMAIL_TXT, EMAIL_TXT)
        email = email.split(":")
        print(email)
        return email

    def send_code_on_email(self, driver, email, action, last_coord, password):
        wait = WebDriverWait(driver, 20)
        logging.info('Send code on email')
        self.event.wait(5)
        while driver.current_url.find('settings') < 0:
            driver.get('https://www.facebook.com/settings?tab=account&section=email')
            logging.info('Retry email ')
            self.event.wait(5)
        self.event.wait(10)
        click = driver.find_element(By.XPATH, "//*[text()='Settings']")
        lick_loc = click.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=lick_loc) # ������ ������������
        self.move_coordinate_calculation(points, action)
        frame = wait.until(lambda x: x.find_element(By.TAG_NAME, "iframe"))
        driver.switch_to.frame(frame)
        tab = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Download Your Information"))
        tab.send_keys(Keys.TAB)
        add_email = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "+ Add another email or mobile number"))
        add_email.send_keys(Keys.ENTER)
        self.event.wait(2)
        send_email = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='new_email']"))
        send_email.click()
        self.write_text_input(action, f'{email[0]}')
        self.event.wait(2)
        send_email.send_keys(Keys.ENTER)
        self.event.wait(3)
        if len(driver.find_elements(By.XPATH, "//input[@type='password'][@id='ajax_password']")) > 0:
            ajax_pass = driver.find_element(By.XPATH, "//input[@type='password'][@id='ajax_password']")
            self.write_text_input(action, password)
            ajax_pass.send_keys(Keys.TAB)
            self.event.wait(1)
            ajax_pass.send_keys(Keys.TAB)
            self.event.wait(1)
            ajax_pass.send_keys(Keys.TAB)
            self.event.wait(1)
            ajax_pass.send_keys(Keys.ENTER)

    def get_code_email(self, driver, email):
        logging.info('Get code from email')
        wait = WebDriverWait(driver, 20)
        email = email[0]
        ps = email[1]
        driver.switch_to.new_window()
        driver.get('https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=13&ct=1675278328&rver=7.0.6737.0&wp=MBI_SSL&wreply=https%3a%2f%2foutlook.live.com%2fowa%2f0%2f%3fstate%3d1%26redirectTo%3daHR0cHM6Ly9vdXRsb29rLmxpdmUuY29tL21haWwvMC8%26RpsCsrfState%3d6cecb439-8cd2-6cd5-64d1-bcaba09f90e8&id=292841&aadredir=1&whr=outlook.com&CBCXT=out&lw=1&fl=dob%2cflname%2cwld&cobrandid=90015')
        send_email = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='email']"))
        send_email.send_keys(f'{email}')
        send_email.send_keys(Keys.ENTER)
        self.event.wait(10)
        send_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='password']"))
        send_password.send_keys(f'{ps}')
        send_password.send_keys(Keys.ENTER)
        self.event.wait(10)
        driver.get('https://outlook.live.com/mail/0/')
        email_pismo = wait.until(lambda x: x.find_element(By.XPATH, "//div[@tabindex='0'][@aria-selected='false'][@role='option']"))
        email_pismo.click()
        self.event.wait(5)
        code = wait.until(lambda x: x.find_element(By.XPATH, '//span[@class="x_mb_text"]'))
        text_code = code[4].text
        code = text_code[-6:-1]
        return code

    def confirm_email_in_fb(self, driver, action, email_code):
        logging.info('Adding code in FB')
        wait =  WebDriverWait(driver, 20)
        list_win = driver.window_handles
        driver.switch_to.window(list_win[0])
        frame = wait.until(lambda x: x.find_element(By.TAG_NAME, "iframe"))
        driver.switch_to.frame(frame)
        but = wait.until(lambda x: x.find_element(By.XPATH, '//a[@role="button"][@rel="dialog"]'))
        self.event.wait(2)
        but[0].click()
        code_input = wait.until(lambda x: x.find_element(By.XPATH, '//input[@id="code"]'))
        self.write_text_input(action, f'{email_code}')
        code_input.send_keys(Keys.ENTER)

    def get_two_fa(self, driver, action, last_coord):
        wait = WebDriverWait(driver, 20)
        while driver.current_url.find('2fac') < 0:
            driver.get('https://www.facebook.com/security/2fac/setup/intro/')
            logging.info('Retry 2fa')
            self.event.wait(5)
        click = wait.until(lambda x: x.find_element(By.XPATH, "//*[text()='Help protect your account']"))
        lick_loc = click.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=lick_loc) # ������ ������������
        last_coord = self.move_coordinate_calculation(points, action)
        button = wait.until(lambda x: x.find_element(By.XPATH, "//a[@role='button'][@rel = 'dialog-post']"))
        lick_loc = button.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=lick_loc) # ������ ������������
        self.move_coordinate_calculation(points, action)
        self.event.wait(5)
        auth = wait.until(lambda x: x.find_element(By.XPATH, "//span[@style='font-family: Arial, sans-serif; font-size: 14px; line-height: 18px; letter-spacing: normal; font-weight: bold; overflow-wrap: normal; text-align: center; color: rgb(28, 30, 33);']"))
        auth_text = auth.text
        button = wait.until(lambda x: x.find_element(By.XPATH, "//button[@rel='post'][@type='button']"))
        self.event.wait(2)
        button.click()
        driver.switch_to.new_window()
        driver.get('https://2fa.live/')
        list_win = driver.window_handles
        self.event.wait(2)
        area_for_auth = wait.until(lambda x: x.find_element(By.XPATH, "//textarea[@class='form-control']"))
        area_for_auth.send_keys(auth_text)
        self.event.wait(2)
        submit = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='submit']"))
        submit.click()
        fa_area = wait.until(lambda x: x.find_element(By.XPATH, "//textarea[@id='output']"))
        self.event.wait(2)
        not_filter_2fa = fa_area.get_property('value')
        fa2 = not_filter_2fa[-6:]
        driver.switch_to.window(list_win[0])
        list_input = wait.until(lambda x: x.find_element(By.TAG_NAME, ('input')))
        self.event.wait(2)
        list_input = list_input[-6:]
        n=0
        for index in list_input:
            index.send_keys(fa2[n])
            n+=1

    def find_account_manager_id(self, driver):
        logging.info('Get manager_id')
        self.event.wait(5)
        while driver.current_url.find('manage') < 0:
            driver.get('https://www.facebook.com/adsmanager/manage/campaigns')
            logging.info('Retry get adsmanager')
            self.event.wait(5)
        while driver.current_url.find('act') < 0:
            logging.info('Refresh page with manager_id')
            driver.refresh()
            self.event.wait(30) # ���������� 30
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
        logging.info('Get Eaab_Token')
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
        """�������� ��� �� ������"""
        return requests.get(url + "/status").json()

    def generaited_password(self):
        chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        n = 0
        password =''
        while n != 10:
            password += random.choice(chars)
            n+=1
        return password

def add_new_thread(country, number_proxy, sms):
    therad_list.append({'thread': None, 'country': country, 'number_proxy': number_proxy, 'sms': sms})
	
def start_thread():
    logging.info("Start thread")
    for thread in therad_list:
        if thread['thread'] is None:
            thread['thread'] = Facebook(country=thread['country'], number_proxy=thread['number_proxy'], sms=thread['sms'])
            thread['thread'].start()
            time.sleep(2)
        else:
            if thread['thread'].is_alive() is False:
                thread['thread'] = Facebook(country=thread['country'], number_proxy=thread['number_proxy'], sms=thread['sms'])
                thread['thread'].start()
                time.sleep(2)	
                
if __name__ == '__main__':

    file_log = logging.FileHandler('settings\py_log.log')
    console_out = logging.StreamHandler()
    format = " [%(threadName)s]: %(asctime)s: %(message)s"
    logging.basicConfig(handlers=(file_log, console_out),format=format, level=logging.INFO,
                        datefmt="%H:%M:%S", )

    logging.info("Start main thread")
    add_new_thread(country=0, number_proxy=0, sms=sms_list[1])
    add_new_thread(country=1, number_proxy=1, sms=sms_list[1]) # �������� ������
    add_new_thread(country=2, number_proxy=2, sms=sms_list[1])
    add_new_thread(country=3, number_proxy=3, sms=sms_list[1]) # �������� ������
    add_new_thread(country=4, number_proxy=4, sms=sms_list[1])
    add_new_thread(country=5, number_proxy=5, sms=sms_list[1])
    start_thread()
    n = 10
    while n != 0:
        time.sleep(420) # 420 ��� ����� �������� ���� ���� 5 ������� �� �� ������ ����� ���� ��������� �� 10 ��� (5 ������� ��� 40 ����������� ��� �.�. 1 �� �����������)
        if threading.active_count() - 1 < len(therad_list):
            start_thread()
            n-=1