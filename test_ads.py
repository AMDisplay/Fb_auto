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


URL = "http://local.adspower.com:50325"
ads_id = "302949221d20300738e52ce0046a2b48"
# http://local.adspower.net:50325 Script can go to Profile Management-> click Settings-> click Cache folder-> local_api file to obtain API address
open_url = URL + '/api/v1/browser/start?user_id=' + "j4ya2j2"
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

driver.get('https://www.facebook.com/')
time.sleep(5)
profile = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[3]/div[1]/span/div/div[1]")
# for node in profile:
#     print(node.get_attribute('aria-label'))
locationprofile = profile.location
points = curve.pointer(first_x = 900, first_y = 400 , last_coord=locationprofile) # расчет передвижения
last_coord = move_coordinate_calculation(points, action)
time.sleep(2)
setting_privicy = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[3]/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div[1]/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div[2]/div[1]")
location_setting_privicy = setting_privicy.location
points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1] , last_coord=location_setting_privicy) # расчет передвижения
last_coord = move_coordinate_calculation(points, action)
time.sleep(2)
setting = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[3]/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[1]/a/div[1]/div[2]/div/div/div/div/span")
location_setting = setting.location
points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=location_setting) # расчет передвижения
last_coord = move_coordinate_calculation(points, action)
frame = driver.find_element(By.TAG_NAME, "iframe")
driver.switch_to.frame(frame)
add_email = driver.find_element(By.XPATH, ('/html/body/div[1]/div[1]/div[1]/div/div[2]/div[2]/div[2]/div/ul/li[3]/a/h3'))
locationa_add_email = add_email.location
print(add_email.size)
print(locationa_add_email) # {'x': 24, 'y': 201}  1140 300
points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=locationa_add_email) # расчет передвижения
last_coord = move_coordinate_calculation(points, action)
ajax = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[2]/div[2]/div[2]/div/ul/li[3]/div/div/div/div[2]/div[1]/div/div/a')
location_ajax = ajax.location
points = curve.pointer(first_x = last_coord[0], first_y = last_coord[1], last_coord=location_ajax) # расчет передвижения
last_coord = move_coordinate_calculation(points, action)

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

# def get_two_fa():
#     # Подключение 2fa
#     driver.get('https://www.facebook.com/security/2fac/setup/intro/')
    # click = driver.find_element(By.XPATH, "//*[text()='Help protect your account']")
    # lick_loc = click.location
    # points = curve.pointer(first_x = 400, first_y = 120 , last_coord=lick_loc) # расчет передвижения
    # last_coord = move_coordinate_calculation(points, action)
#     button = driver.find_element(By.XPATH, "//a[@role='button'][@rel = 'dialog-post']")
#     button.click()
#     time.sleep(5)
#     auth = driver.find_element(By.XPATH, "//span[@style='font-family: Arial, sans-serif; font-size: 14px; line-height: 18px; letter-spacing: normal; font-weight: bold; overflow-wrap: normal; text-align: center; color: rgb(28, 30, 33);']")
#     auth_text = auth.text
#     button = driver.find_element(By.XPATH, "//button[@rel='post'][@type='button']")
#     time.sleep(2)
#     button.click()
#     driver.switch_to.new_window()
#     driver.get('https://2fa.live/')
#     list_win = driver.window_handles
#     time.sleep(2)
#     area_for_auth = driver.find_element(By.XPATH, "//textarea[@class='form-control']")
#     area_for_auth.send_keys(auth_text)
#     time.sleep(1)
#     submit = driver.find_element(By.XPATH, "//a[@id='submit']")
#     submit.click()
#     fa_area = driver.find_element(By.XPATH, "//textarea[@id='output']")
#     time.sleep(2)
#     not_filter_2fa = fa_area.get_property('value')
#     fa2 = not_filter_2fa[-6:]
#     driver.switch_to.window(list_win[0])
#     list_input = driver.find_elements(By.TAG_NAME, ('input'))
#     time.sleep(2)
#     list_input = list_input[-6:]
#     n=0
#     for index in list_input:
#         index.send_keys(fa2[n])
#         n+=1


# driver.get('https://www.facebook.com/settings?tab=account&section=email')
# time.sleep(5)
# click = driver.find_element(By.XPATH, "//*[text()='Settings']")
# lick_loc = click.location
# points = curve.pointer(first_x = 400, first_y = 120 , last_coord=lick_loc) # расчет передвижения
# last_coord = move_coordinate_calculation(points, action)
# frame = driver.find_element(By.TAG_NAME, "iframe")
# driver.switch_to.frame(frame)
# tab = driver.find_element(By.PARTIAL_LINK_TEXT, "Download Your Information")
# tab.send_keys(Keys.TAB)
# qwe = driver.find_element(By.PARTIAL_LINK_TEXT, "+ Add another email or mobile number")
# qwe.send_keys(Keys.ENTER)
# time.sleep(2)
# send_email = driver.find_element(By.XPATH, "//input[@name='new_email']")
# send_email.send_keys('nbrian7qom@outlook.com')
# time.sleep(10)
# send_email.send_keys(Keys.ENTER)
# time.sleep(10)
# if len(driver.find_elements(By.XPATH, "//input[@type='password'][@id='ajax_password']")) > 0:
#     ajax_pass = driver.find_element(By.XPATH, "//input[@type='password'][@id='ajax_password']")
#     ajax_pass.send_keys('sdfsdf')
#     time.sleep(5)
#     ajax_pass.send_keys(Keys.TAB)
#     ajax_pass.send_keys(Keys.TAB)
#     ajax_pass.send_keys(Keys.TAB)
#     ajax_pass.send_keys(Keys.ENTER)

# Пароль из емаил
# driver.switch_to.new_window()
# driver.get('https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=13&ct=1675278328&rver=7.0.6737.0&wp=MBI_SSL&wreply=https%3a%2f%2foutlook.live.com%2fowa%2f0%2f%3fstate%3d1%26redirectTo%3daHR0cHM6Ly9vdXRsb29rLmxpdmUuY29tL21haWwvMC8%26RpsCsrfState%3d6cecb439-8cd2-6cd5-64d1-bcaba09f90e8&id=292841&aadredir=1&whr=outlook.com&CBCXT=out&lw=1&fl=dob%2cflname%2cwld&cobrandid=90015')
# send_email = driver.find_element(By.XPATH, "//input[@type='email']")
# email = 'cloverwirick1l5@outlook.com'
# ps = 'qOknxvh1'
# send_email.send_keys(f'{email}')
# send_email.send_keys(Keys.ENTER)
# time.sleep(5)
# send_password = driver.find_element(By.XPATH, "//input[@type='password']")
# send_password.send_keys(f'{ps}')
# send_password.send_keys(Keys.ENTER)
# time.sleep(5)
# driver.get('https://outlook.live.com/mail/0/')
# time.sleep(10)
# email_pismo = driver.find_element(By.XPATH, "//div[@tabindex='0'][@aria-selected='false'][@role='option']")
# email_pismo.click()
# time.sleep(5)
# code = driver.find_elements(By.XPATH, '//span[@class="x_mb_text"]')
# text_code = code[4].text
# code = text_code[-6:-1]

# def confirm_email_in_fb():
#     # Вбивание кода из емаил
#     list_win = driver.window_handles
#     driver.switch_to.window(list_win[0])
#     frame = driver.find_element(By.TAG_NAME, "iframe")
#     driver.switch_to.frame(frame)
#     but = driver.find_elements(By.XPATH, '//a[@role="button"][@rel="dialog"]')
#     but[0].click()
#     time.sleep(3)
#     code_input = driver.find_element(By.XPATH, '//input[@id="code"]')
#     code_input.send_keys('234234')
#     code_input.send_keys(Keys.ENTER)

