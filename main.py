# Coding: UFT-8

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
from selenium.webdriver.common.keys import Keys


import curve
import settings.list_of_settings as list_of_settings
from api_sms import api_5sim, sms_activate
from proxy.get_proxy import get_proxy

# 680 ��� 10/10 ����� � ��� 25 ������ ���� ���������

API_KEY = ""
URL = "http://local.adspower.com:50325"
USER_ID = ""
GROUP_ID = ""

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
        """Main"""
        logging.info('Start thread %s', threading.current_thread().name)
        try:
            try:
                status_api = self.get_status_api(URL)
                if status_api['code'] != 0:
                    print(status_api)
            except Exception:
                print("Problem with connect to api")
                sys.exit()
            current_proxy = get_proxy(self.number_proxy)
            new_profile = self.create_profile(current_proxy)
            driver = self.start_profile(URL, new_profile["response"])
            data = self.click_on_registraion(driver ,new_profile)
            self.add_fields_in_reg_and_buy_number(data, new_profile["response"], payload=new_profile['payload'])
        except WebDriverException:
            logging.critical('Problem with web %s', new_profile)
            self.delete_account(new_profile=new_profile)
        except KeyError:
            logging.critical('Success delete account %s', new_profile)
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
        eeab_token=None,
        email=None,
        fa2=None
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
            cookie_json = json.loads(cookies)
            acoount_id = cookie_json[4]['value']
            current_email = email[0]
            email_pass = email[1]
            with open('csv\For_sale.txt', "a") as file:
                lines = [phone, password, current_email, email_pass, acoount_id, eeab_token, payload, fa2, cookies]
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
        """Create profile"""
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
                "do_not_track": "true", 
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
        logging.info(payload)
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
        """Start profile"""
        logging.info('Start profile')
        self.lock.acquire()
        profile_id = new_profile['data']['id']
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
                points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_eng) 
                last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������


        logging.info('Name')
        try:
            elem_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='firstname']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_name = elem_name.location # ������
            points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc_elem_name) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            self.write_text_input(action, name)

        logging.info('Surename')
        try:
            elem_second_name = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='lastname']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_second_name = elem_second_name.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_second_name) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            self.write_text_input(action, surename)

        logging.info('Accept NS')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        logging.info('Mounth birthday')
        try:
            select_elem_birthday_month = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_month']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_birthday_month = select_elem_birthday_month.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_month) 
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.choice(list_of_month))

        logging.info('Day birthday')
        try: 
            select_elem_birthday_day = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_day']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_birthday_day = select_elem_birthday_day.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_birthday_day) 
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.randrange(0, 26))

        logging.info('Year birthday')
        try:
            select_elem_birthday_year = wait.until(lambda x: x.find_element(By.XPATH, "//select[@name='birthday_year']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_select_elem_birthday_year = select_elem_birthday_year.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_birthday_year) 
            last_coord = self.move_coordinate_calculation(points, data["action"])
            self.write_text_input(action, text=random.randrange(1990, 2002))

        logging.info('Accept birthday')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        logging.info('Put phone') # Please enter a valid phone number.
        try:
            elem_mail = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_email__']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_mail = elem_mail.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_mail) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        if self.sms == 'activate':
            logging.info('Waiting phone sms_activate')
            response = sms_activate.get_number(country=self.country)
            logging.info(f'Responce phone {response}')
            country_number = response['countryCode']
            operator_number = response['countryCode']
            id_number = response.get('activationId')
            phone = response['phoneNumber']
            logging.info('Add phone')
            self.write_text_input(action, text=phone)
        else:
            logging.info('Waiting phone 5sim')
            response = api_5sim.buy_number(country=self.country)
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
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            time.sleep(random.randrange(2,3))

        logging.info('Add sex')
        try:
            select_elem_sex_woman = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='sex'][@value='1']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_select_elem_sex_woman = select_elem_sex_woman.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_select_elem_sex_woman) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������

        logging.info('Accept sex')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            time.sleep(random.randrange(2,3))

        logging.info('Generate password')
        try:
            elem_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='reg_passwd__']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_password = elem_password.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_password) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            password = self.generaited_password()
            logging.info('account password = %s', password)
            self.event.wait(1)
            self.write_text_input(action, text=password)

        logging.info('Accept password')
        try:
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit'][@name='submit']"))
        except:
            self.delete_account(new_profile=new_profile)
        else:
            loc_elem_confirm = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            
        self.event.wait(20)

        if data['driver'].current_url.find("action_dialog") > 0:
            logging.info('Acc exist')
            but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
            loc_but = but.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            while len(data['driver'].find_elements(By.XPATH, "//div[@class='icon icon-generic']")) > 0:
                logging.info('Error connect after action-dialog')
                data['driver'].back()
                but = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Create New Account']"))
                loc_but = but.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_but) 
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
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) 
                last_coord = self.move_coordinate_calculation(points, data["action"]) # �����������
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)

        elif data['driver'].current_url.find("error") > 0:
            logging.info('error download')
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='error', payload=payload , country_number=country_number, operator_number=operator_number)

        elif data['driver'].current_url.find("checkpoint") > 0:
            logging.info('checkpoint')
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Chekpoint in action', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            if len(data["driver"].find_elements(By.PARTIAL_LINK_TEXT, ('Please enter a valid phone number'))) > 0:
                logging.info('Not valid phone')
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='not valid number', payload=payload , country_number=country_number, operator_number=operator_number)
            if len(data["driver"].find_elements(By.XPATH, "//input[@type='number']")) > 0:
                logging.info("reg accept withour not now")
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)
            if data['driver'].current_url.find("save") > 0:
                logging.info('reg accept, add sms')
                elem_confirm = wait.until(lambda x: x.find_element(By.XPATH, "//button[@type='submit']"))
                loc_elem_confirm = elem_confirm.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_confirm) 
                last_coord = self.move_coordinate_calculation(points, data["action"]) # �����������
                self.accept_number_code(data, id_number, password, phone, new_profile, payload, last_coord, country_number,operator_number)
            else:
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='check in not now', payload=payload , country_number=country_number, operator_number=operator_number)

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
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_form) 
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
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_didnt_code) 
                last_coord = self.move_coordinate_calculation(points, data["action"]) # ������������
            try:  
                elem_send_sms_code_again = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, ("Send Code Again")))
            except:
                logging.info("Problem with send sms")
                self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Problem with send sms', payload=payload , country_number=country_number, operator_number=operator_number)
            else:
                loc_elem_send_sms_code_again = elem_send_sms_code_again.location # ������
                points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_elem_send_sms_code_again) 
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
                    self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Problem with retry send sms', payload=payload , country_number=country_number, operator_number=operator_number)
                self.write_text_input(action=data['action'], text=code_sms)
                self.event.wait(3)
        logging.info('Sms valid')
        try:
            code_confirm_button = wait.until(lambda x: x.find_element(By.PARTIAL_LINK_TEXT, "Confirm"))
        except:
            self.chech_checkpoint(id_number=id_number, new_profile=new_profile, phone=phone, status='Problem with button confirm', payload=payload , country_number=country_number, operator_number=operator_number)
        else:
            loc_code_confirm_button = code_confirm_button.location # ������
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=loc_code_confirm_button) 
            last_coord = self.move_coordinate_calculation(points, data["action"]) # �����������
        last_coord = self.skip_or_add_friends(driver, data["action"], last_coord)
        self.lock.acquire()
        email_and_pass = self.get_email() # [0] - email [1] = pass
        self.send_code_on_email(driver=driver, action = data["action"], email=email_and_pass, last_coord=last_coord, password=password)
        self.lock.release()
        code_email = self.get_code_email(driver, email_and_pass, data['action'], last_coord)
        self.accept_code_from_email(driver,code_email, data['action'], last_coord)
        fa2 = self.get_two_fa(driver=driver, action=data['action'], last_coord=last_coord,password=password)
        eeab_token = self.find_eeab_token(driver=driver)
        cookies = json.dumps(driver.get_cookies())
        self.wrote_csv(password=password, phone=phone, status='Success', cookies=cookies, payload=payload, country_number=country_number, operator_number=operator_number,eeab_token=eeab_token, email=email_and_pass, fa2=fa2)
        if self.sms == 'activate':
            sms_activate.close_status(id_number, status=6)
        else:
            api_5sim.finish_orfer(id=id_number)
        logging.info("Succes reg")
        self.delete_account(new_profile=new_profile) 

    def get_email(self): 
        logging.info('Get email from txt')
        with open(EMAIL_TXT) as fp:
            email = fp.readline()
        with open(EMAIL_TXT) as infile, open(NEW_EMAIL_TXT, "w",) as outfile:
            for line in infile:
                if email not in line:
                    outfile.write(line)
        os.remove(EMAIL_TXT)
        os.rename(NEW_EMAIL_TXT, EMAIL_TXT)
        email = email.split(":")
        pas = email[1][:-1]
        email.pop(1)
        email.append(pas)
        return email

    def skip_or_add_friends(self, driver, action, last_coord):
        wait = WebDriverWait(driver, 20)
        self.event.wait(10)
        logging.info('Skip add photo previous friends')
        if len(driver.find_elements(By.XPATH, "//button[@value='Add photo']")) > 0:
            button_next = wait.until(lambda x: x.find_element(By.XPATH, "//a[text()='Next']"))
            button_next_location = button_next.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=button_next_location) 
            last_coord = self.move_coordinate_calculation(points, action)
        logging.info('Searching adding friends')
        if len(driver.find_elements(By.XPATH, "//a[@id='qf_footer_add_friend_button']")) > 0:
            add_button = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='qf_footer_add_friend_button']"))
            locationprofile = add_button.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=locationprofile) 
            last_coord = self.move_coordinate_calculation(points, action)
            self.event.wait(10)
            logging.info('Search next button after adding friends')
            button_next = wait.until(lambda x: x.find_element(By.XPATH, "//a[text()='Next']"))
            button_next_location = button_next.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=button_next_location) 
            last_coord = self.move_coordinate_calculation(points, action)
        return last_coord

    def send_code_on_email(self, driver, email, action, last_coord, password):
        logging.info('email %s , password: %s', email[0], password)
        wait = WebDriverWait(driver,20)
        logging.info('all settings')
        self.event.wait(5)
        add_button = wait.until(lambda x: x.find_element(By.XPATH, "//div[@id='bookmarks_jewel']"))
        locationprofile = add_button.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=locationprofile) 
        last_coord = self.move_coordinate_calculation(points, action)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logging.info('Settings & Privacy')
        self.event.wait(2)
        setings = wait.until(lambda x: x.find_element(By.XPATH, "//div[text()='Settings & Privacy']"))
        settings_location = setings.location
        settings_location['y'] =  settings_location['y'] - 295
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=settings_location)
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('Settings')
        settings_location['y'] =  settings_location['y'] + 50
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=settings_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('Personal and account information')
        personal_info = wait.until(lambda x: x.find_element(By.XPATH, "//div[text()='Personal and account information']"))
        personal_info_location = personal_info.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=personal_info_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('personal_information_setting_contact_info')
        contact_info = wait.until(lambda x: x.find_element(By.XPATH, "//div[@data-testid='personal_information_setting_contact_info']"))
        contact_info_location = contact_info.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=contact_info_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('Add email')
        add_email = wait.until(lambda x: x.find_element(By.XPATH, "//div[text()='Add email address']"))
        add_email_location = add_email.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=add_email_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('input email')
        input_email = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='email']"))
        input_email_location = input_email.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=input_email_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        self.write_text_input(action, email[0])
        logging.info('input password email')
        input_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='save_password']"))
        input_password_location = input_password.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=input_password_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        self.write_text_input(action, password)
        logging.info('Button Add email')
        button_confirm_email = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Add Email']"))
        button_confirm_email_location = button_confirm_email.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=button_confirm_email_location) 
        last_coord = self.move_coordinate_calculation(points, action)

    def get_code_email(self, driver, email, action, last_coord):
        logging.info('Get code from email')
        wait = WebDriverWait(driver, 60)
        current_email = email[0]
        password = email[1]
        logging.info('email = %s, pas = %s', current_email, password)
        driver.switch_to.new_window()
        driver.get('https://login.live.com')
        self.event.wait(3)
        logging.info('add email in outlook %s', current_email)
        send_email = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='email']"))
        send_email.click()
        self.write_text_input(action, current_email)
        logging.info('accept email in outlook')
        send_email_but = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='submit']"))
        send_email_but_location = send_email_but.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=send_email_but_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        self.event.wait(3)
        logging.info('add passwprd in outlook %s', password)
        send_password = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='password']"))
        send_password_location = send_password.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=send_password_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        self.write_text_input(action, password)
        logging.info('accept password in outlook')
        send_email_but = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='submit']"))
        send_email_but_location = send_email_but.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=send_email_but_location)
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('Not save password outlook')
        if len(driver.find_elements(By.XPATH, "//a[@id='iShowSkip']")) > 0:
            skip = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='iShowSkip']"))
            skip.click()
        if len(driver.find_elements(By.XPATH, "//a[@id='iShowSkip']")) > 0:
            skip = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='iShowSkip']"))
            skip.click()
        if len(driver.find_elements(By.XPATH, "//input[@id='idBtn_Back']")) > 0:
            skip = wait.until(lambda x: x.find_element(By.XPATH, "//input[@id='idBtn_Back']"))
            skip.click()
        if len(driver.find_elements(By.XPATH, "//a[@id='iCancel']")) > 0:
            qwe = driver.find_element(By.XPATH, "//a[@id='iCancel']")
            qwe.click()
        logging.info('Get mail')
        driver.get('https://outlook.live.com/mail/0/')
        logging.info('mail other')
        other = wait.until(lambda x: x.find_element(By.XPATH, "//span[text()='Other']"))
        other.click()
        logging.info('Get code from email to confirm')
        email_pismo = wait.until(lambda x: x.find_element(By.XPATH, "//div[@tabindex='0'][@aria-selected='false'][@role='option']"))
        email_pismo.click()
        self.event.wait(5)
        full_code = wait.until(lambda x: x.find_elements(By.XPATH, '//span[@class="x_mb_text"]'))
        text_code = full_code[4].text
        code = text_code[-6:-1]
        logging.info('Code from email %s', code)
        return code

    def accept_code_from_email(self,driver, code, action, last_coord):
        logging.info('accept code fron email')
        wait = WebDriverWait(driver, 20)
        list_win = driver.window_handles
        driver.switch_to.window(list_win[0])
        confirm_button = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Confirm']"))
        confirm_button_location = confirm_button.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=confirm_button_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        code_input = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='code']"))
        code_input_location = code_input.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=code_input_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        self.write_text_input(action, code)
        confirm_button = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Confirm']"))
        confirm_button_location = confirm_button.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=confirm_button_location) 
        last_coord = self.move_coordinate_calculation(points, action)

    def get_two_fa(self, driver, action, last_coord, password):
        wait = WebDriverWait(driver, 20)
        logging.info('back to main page fb')
        driver.get('https://m.facebook.com/home.php')
        logging.info('go to 2fa')
        add_button = wait.until(lambda x: x.find_element(By.XPATH, "//div[@id='bookmarks_jewel']"))
        locationprofile = add_button.location
        points = curve.pointer(first_x = 900, first_y = 400, last_coord=locationprofile) 
        last_coord = self.move_coordinate_calculation(points, action)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logging.info('Settings & Privacy 2fa')
        setings = wait.until(lambda x: x.find_element(By.XPATH, "//div[text()='Settings & Privacy']"))
        settings_location = setings.location
        settings_location['y'] =  settings_location['y'] - 300
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=settings_location)
        last_coord = self.move_coordinate_calculation(points, action)
        settings_location['y'] =  settings_location['y'] + 50
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=settings_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('Get password and security')
        password_and_security = wait.until(lambda x: x.find_element(By.XPATH, "//div[text()='Password and security']"))
        password_and_security_location = password_and_security.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=password_and_security_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('button')
        fa = wait.until(lambda x: x.find_element(By.XPATH, "//span[text()='Use two-factor authentication']"))
        fa_security_location = fa.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=fa_security_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        fa_app = wait.until(lambda x: x.find_element(By.XPATH, "//span[text()='Use authentication app']"))
        fa_app_security_location = fa_app.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=fa_app_security_location) 
        last_coord = self.move_coordinate_calculation(points, action)
        logging.info('Check on password account in 2fa')
        time.sleep(2)
        if len(driver.find_elements(By.XPATH, "//input[@type='password']")) > 0:
            input_pas = wait.until(lambda x: x.find_element(By.XPATH, "//input[@type='password']"))
            input_pas_location = input_pas.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=input_pas_location) 
            last_coord = self.move_coordinate_calculation(points, action)
            self.write_text_input(action, password)
            cont_button = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Continue']"))
            cont_button_location = cont_button.location
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=cont_button_location) 
            last_coord = self.move_coordinate_calculation(points, action)
            logging.info('Get key 2fa')
            auth = wait.until(lambda x: x.find_element(By.XPATH, "//div[@data-testid='key']"))
            auth_text = auth.text
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            setings = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Continue']"))
            settings_location = setings.location
            settings_location['y'] =  settings_location['y'] - 50
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=settings_location)
            last_coord = self.move_coordinate_calculation(points, action)
        else:
            logging.info('Get key 2fa')
            time.sleep(2)
            auth = wait.until(lambda x: x.find_element(By.XPATH, "//div[@data-testid='key']"))
            auth_text = auth.text
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            setings = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Continue']"))
            settings_location = setings.location
            settings_location['y'] =  settings_location['y'] - 50
            points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=settings_location)
            last_coord = self.move_coordinate_calculation(points, action)
        logging.info('get 2fa code')
        driver.switch_to.new_window()
        driver.get('https://2fa.live/')
        area_for_auth = wait.until(lambda x: x.find_element(By.XPATH, "//textarea[@class='form-control']"))
        area_for_auth.send_keys(auth_text)
        submit = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='submit']"))
        submit.click()
        fa_area = wait.until(lambda x: x.find_element(By.XPATH, "//textarea[@id='output']"))
        self.event.wait(2)
        not_filter_2fa = fa_area.get_property('value')
        fa2 = not_filter_2fa[-6:]
        logging.info('input 2fa %s', fa2)
        list_win = driver.window_handles
        driver.switch_to.window(list_win[0])
        conf_code_fa = wait.until(lambda x: x.find_element(By.XPATH, "//input[@name='code']"))
        conf_code_fa_location = conf_code_fa.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=conf_code_fa_location)
        last_coord = self.move_coordinate_calculation(points, action)
        self.write_text_input(action,fa2)
        conf_code_fa = wait.until(lambda x: x.find_element(By.XPATH, "//button[@value='Continue']"))
        conf_code_fa_location = conf_code_fa.location
        points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=conf_code_fa_location)
        last_coord = self.move_coordinate_calculation(points, action)
        return auth_text

    def find_eeab_token(self, driver):
        logging.info('Get Eaab_Token')
        while driver.current_url.find('adsmanager') < 0:
            driver.get('https://www.facebook.com/adsmanager/manage/campaigns')
            logging.info('Retry get adsmanager')
            self.event.wait(5)
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
        """Check API ADS status"""
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
    add_new_thread(country=1, number_proxy=1, sms=sms_list[1]) 
    add_new_thread(country=2, number_proxy=2, sms=sms_list[1])
    add_new_thread(country=3, number_proxy=3, sms=sms_list[1]) 
    # add_new_thread(country=4, number_proxy=4, sms=sms_list[1])
    # add_new_thread(country=5, number_proxy=5, sms=sms_list[1])
    start_thread()
    n = 0
    while n != 0:
        time.sleep(420) # 420 ��� ����� �������� ���� ���� 5 ������� �� �� ������ ����� ���� ��������� �� 10 ��� (5 ������� ��� 40 ����������� ��� �.�. 1 �� �����������)
        if threading.active_count() - 1 < len(therad_list):
            start_thread()
            n-=1
