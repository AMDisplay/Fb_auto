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

import pickle
import json

URL = "http://local.adspower.com:50360"
ads_id = "302949221d20300738e52ce0046a2b48"
# http://local.adspower.net:50325 Script can go to Profile Management-> click Settings-> click Cache folder-> local_api file to obtain API address
open_url = "http://local.adspower.net:50360/api/v1/browser/start?user_id=" + "j4wp5ds"
# close_url = "http://local.adspower.net:50325/api/v1/browser/stop?user_id=" + ads_id

resp = requests.get(open_url).json()
login = "+255772049150"
password  = 'DcHgUKVLaw'


chrome_driver = resp["data"]["webdriver"]
chrome_options = Options()
chrome_options.page_load_strategy = 'eager'
chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
driver = webdriver.Chrome(chrome_driver, options=chrome_options)



driver.get('https://www.facebook.com/')
qwe = driver.find_element(By.XPATH, "//input[@id='email']")
qwe.send_keys(login)
time.sleep(1)
zxc = driver.find_element(By.XPATH, "//input[@id='pass']")
zxc.send_keys(password)
time.sleep(1)
zxc.send_keys(Keys.ENTER)
driver.get('https://www.facebook.com/')
driver.get("https://www.facebook.com/adsmanager/manage/")
yyyy=0
while driver.current_url.find('act') < 0:
    print(yyyy)
    driver.refresh()
    yyyy+=1
if driver.current_url.find("nav_source") > 0:
    current_url = driver.current_url
    idx_1 = current_url.find('act')+4
    idx_2 = current_url.find('&', idx_1)
    manager_id = current_url[idx_1:idx_2]
    print(manager_id)
else:
    current_url = driver.current_url
    idx_1 = current_url.find('act')+4
    manager_id = current_url[idx_1:]
    print(manager_id)

html_doc=driver.page_source
idx = html_doc.find('EAAB')
idx_2 = html_doc.find('"', idx)
eeab_token = html_doc[idx:idx_2]
print(eeab_token)

рasd = json.dumps(driver.get_cookies())
print(рasd)
driver.close()