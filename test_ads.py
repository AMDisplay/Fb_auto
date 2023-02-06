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
import curve
import random
import logging


URL = "http://local.adspower.com:50325"
ads_id = "302949221d20300738e52ce0046a2b48"
# http://local.adspower.net:50325 Script can go to Profile Management-> click Settings-> click Cache folder-> local_api file to obtain API address
open_url = URL + '/api/v1/browser/start?user_id=' + "j50j7a0"
# close_url = "http://local.adspower.net:50325/api/v1/browser/stop?user_id=" + ads_id


# # login = "+255772049150"
# # password  = 'DcHgUKVLaw'
# # url = URL + "/api/v1/user/create"
# # payload = payload = { #№
# #             "name": "Fb",
# #             "group_id": "1836292",
# #             "domain_name": "google.com",
# #             "repeat_config": [
# #                 "0"
# #             ],
# #             "country": "us",
# #             "fingerprint_config": {
# #                 "language": [
# #                 "uk-UA", "uk", "en-US", "en" #   ru-RU,ru,en-US,en ["en-US","en","zh-CN","zh"]
# #                 ],
# #                 "ua": "",
# #                 "flash": "block",
# #                 "scan_port_type": "1",
# #                 "screen_resolution": '', # ex 1024_600 or default or random
# #                 "fonts": [
# #                 "all"
# #                 ],
# #                 "longitude": "180",
# #                 "latitude": "90",
# #                 "webrtc": "proxy",
# #                 "do_not_track": "true", # Отслеживание действий на сайте
# #             },
# #             "user_proxy_config": {
# #                 "proxy_soft": "no_proxy", # other or no_proxy
# #             }
# #             }


resp = requests.get(open_url).json()
# print(payload)
# print(resp)
chrome_driver = resp["data"]["webdriver"]
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
driver = webdriver.Chrome(chrome_driver, options=chrome_options)
action =  ActionBuilder(driver, duration=1)
wait = WebDriverWait(driver, 30)

# # "//span[.='Next']"

def find_inscribed_rectangle(larger_rectangle, inscribed_rectangle):
    (x1, y1), (x2, y2) = larger_rectangle
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2

    width_inscribed, height_inscribed = inscribed_rectangle
    x1_inscribed = x_mid - width_inscribed / 2
    y1_inscribed = y_mid - height_inscribed / 2
    x2_inscribed = x_mid + width_inscribed / 2
    y2_inscribed = y_mid + height_inscribed / 2

    return [(x1_inscribed, y1_inscribed), (x2_inscribed, y2_inscribed)]

def move_coordinate_calculation(points, action):
        coord = points.tolist()  # Преобразование многомерного (N массива np) в список питон
        for point in coord:
            point_x = point[0]
            point_y = point[1]
            action.pointer_action.move_to_location(point_x, point_y)
            action.perform()
            # print(point)
        action.pointer_action.click()
        action.perform()
        time.sleep(5)
        return coord[-1]

def write_text_input( action, text):
    text = str(text) 
    for letter in text:
        action.key_action.send_keys(letter)
        action.perform()
        time.sleep(random.uniform(0.2,0.4))


# # вызор здрд
# # driver.get('https://business.facebook.com/overview/')
# # time.sleep(5)
# # elem = driver.find_element(By.LINK_TEXT, 'Create an account')
# # elem.click()
# # time.sleep(5)
# # elem_2 = driver.find_elements(By.XPATH, "//input[@type='text']") # 1 элем в бм
# # elem_2[0].click()
# # elem_2[0].send_keys('rinerine')
# # elem_2[2].click()
# # elem_2[2].send_keys('eorun') # Работает
# # button = driver.find_elements(By.XPATH, "//div[@role='button']")
# # button[1].click()  # Работает

# # Переход к зрд до вбивания почты
# # driver.get('https://www.facebook.com/accountquality/')
# # time.sleep(3)
# # confirm = driver.find_elements(By.XPATH, "//div[@role='button'][@tabindex = '0']")
# # confirm[-1].click()
# # driver.get('https://www.facebook.com/checkpoint/1501092823525282/6521215381227994/')
# # time.sleep(3)
# # con = driver.find_elements(By.XPATH, "//div[@role='button'][@tabindex = '0']")
# # con[-1].click()
# # driver.get('https://www.facebook.com/checkpoint/1501092823525282/6521215381227994/')
# # time.sleep(4)
# # qwe = driver.find_elements(By.XPATH, "//iframe[@id='captcha-recaptcha']")
# # driver.switch_to.frame(qwe[0])
# # qwe = driver.find_elements(By.XPATH, "//iframe[@title='reCAPTCHA']")
# # driver.switch_to.frame(qwe[0])
# # recapcha = driver.find_element(By.XPATH, "//div[@class='recaptcha-checkbox-border']")
# # window = driver.maximize_window()
# # print(driver.get_window_size())
# # location_box_recapcha = recapcha.location
# # location_box_recapcha['x'] = location_box_recapcha['x']*54
# # location_box_recapcha['y'] = location_box_recapcha['y']*11
# # print(location_box_recapcha)
# # points = curve.pointer(first_x = 400, first_y = 120 , last_coord=location_box_recapcha) # расчет передвижения
# # last_coord = move_coordinate_calculation(points, action)
# # driver.switch_to.default_content()
# # cont = driver.find_element(By.XPATH, "//div[@aria-label='Continue'][@aria-disabled='true']") Кнопка не активна
# # cont = driver.find_element(By.XPATH, "//div[@aria-label='Continue']")
# # cont.click()
# # email = driver.find_element(By.XPATH, "//input[@type='email']")
# # email.send_keys('fjj858@google.com')
# # cont =  driver.find_element(By.XPATH, "//div[@aria-label='Send login code']")
# # cont.click()
# # time.sleep(1)
# # email_code = driver.find_element(By.XPATH, "//input[@type='text']")
# # email_code.send_keys('546789')
# # cont =  wait.until(lambda x: x.find_element(By.XPATH,"//span[.='Next']"))
# # cont_loc = cont.location
# # cont_loc['x'] = cont_loc['x']+200
# # points = curve.pointer(first_x = 400, first_y = 500 , last_coord=cont_loc) # расчет передвижения
# # last_coord = move_coordinate_calculation(points, action)


# мб для чекера почты
# sign_in = driver.find_element(By.XPATH, "//a[@data-task= 'signin']")
# sign_in.click()
# if len(driver.find_elements(By.XPATH, "//a[@id='iShowSkip']")) > 0:
#     skip = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='iShowSkip']"))
#     skip.click()
# if len(driver.find_elements(By.XPATH, "//a[@id='iShowSkip']")) > 0:
#     skip = wait.until(lambda x: x.find_element(By.XPATH, "//a[@id='iShowSkip']"))
#     skip.click()
# skip = wait.until(lambda x: x.find_element(By.XPATH, "//input[@id='idBtn_Back']"))
# skip.click()
# qwe = driver.find_element(By.XPATH, "//a[@id='iCancel']")
# qwe.click()
# time.sleep(7)
# profile = driver.find_element(By.XPATH, "//button[contains(@title, 'Account manager')]")
# profile.click()
# time.sleep(1)
# profile_out_button = driver.find_element(By.XPATH, "//a[@id='mectrl_body_signOut']")
# profile_out_button.click()
# time.sleep(1)
# driver.get('https://outlook.live.com/owa/') #wilcoxsnickole75@outlook.com:kK5g9I19iF

