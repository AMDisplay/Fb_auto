import pickle
import time

import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
import curve

"""Запускает только что созданный профиль"""
options = webdriver.ChromeOptions() 
options.add_argument("start-maximized")
# to supress the error messages/logs
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options, executable_path=r'C:\WebDrivers\chromedriver.exe')
qwe = driver.get("https://www.selenium.dev/selenium/web/mouse_interaction.html")
clickable = driver.find_element(By.XPATH, "//a[@id='click']")
print(clickable.id)
print(clickable.tag_name)
print(clickable.text)
print(driver.get_cookies())
driver.find_element
print(driver.get_cookies())
pickle.dump
driver.execute_script("return navigator.userAgent")
driver.quit()
driver.get()
driver.implicitly_wait()