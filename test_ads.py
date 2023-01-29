import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
import csv
import pickle
import json

URL = "http://local.adspower.com:50360"
ads_id = "302949221d20300738e52ce0046a2b48"
# http://local.adspower.net:50325 Script can go to Profile Management-> click Settings-> click Cache folder-> local_api file to obtain API address
# open_url = "http://local.adspower.net:50360/api/v1/browser/start?user_id=" + "j4wq26r"
# close_url = "http://local.adspower.net:50325/api/v1/browser/stop?user_id=" + ads_id


login = "+255772049150"
password  = 'DcHgUKVLaw'
url = URL + "/api/v1/user/create"
payload = payload = { #№
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
                "ua": "",
                "flash": "block",
                "scan_port_type": "1",
                "screen_resolution": '', # ex 1024_600 or default or random
                "fonts": [
                "all"
                ],
                "longitude": "180",
                "latitude": "90",
                "webrtc": "proxy",
                "do_not_track": "true", # Отслеживание действий на сайте
            },
            "user_proxy_config": {
                "proxy_soft": "no_proxy", # other or no_proxy
            }
            }

headers = {
            'Content-Type': 'application/json'
            }
resp = requests.request("POST", url, headers=headers, json=payload).json()
print(payload)
print(resp)
# chrome_driver = resp["data"]["webdriver"]
# chrome_options = Options()
# chrome_options.page_load_strategy = 'eager'
# chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
# driver = webdriver.Chrome(chrome_driver, options=chrome_options)



# driver.get('https://www.facebook.com/')
# qwe = driver.find_element(By.XPATH, "//input[@id='email']")
# qwe.send_keys(login)
# time.sleep(1)
# zxc = driver.find_element(By.XPATH, "//input[@id='pass']")
# zxc.send_keys(password)
# zxc.send_keys(Keys.ENTER)
# driver.get('https://www.facebook.com/')
# time.sleep(5)
# driver.get("https://www.facebook.com/adsmanager/manage/")
# yyyy=0
# chrome_options.page_load_strategy = 'eager'
# while driver.current_url.find('act') < 0:
#     print(yyyy)
#     driver.refresh()
#     yyyy+=1
# if driver.current_url.find("nav_source") > 0:
#     current_url = driver.current_url
#     idx_1 = current_url.find('act')+4
#     idx_2 = current_url.find('&', idx_1)
#     manager_id = current_url[idx_1:idx_2]
# else:
#     current_url = driver.current_url
#     idx_1 = current_url.find('act')+4
#     manager_id = current_url[idx_1:]

# html_doc=driver.page_source
# idx = html_doc.find('EAAB')
# idx_2 = html_doc.find('"', idx)
# eeab_token = html_doc[idx:idx_2]


# cookie = json.dumps(driver.get_cookies())
# driver.close()
# n=0
# file = open('cookie.txt')
# file.read()

# with open('cookie.txt', "r") as file:
#     if len(file.readline()) 

# with open('cookie.txt', "a") as file:
#     lines = [manager_id, eeab_token, cookie]

#         file.writelines("%s\t" % line for line in lines)
#         file.write('\n')
