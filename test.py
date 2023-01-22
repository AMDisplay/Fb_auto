import requests
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import curve
from selenium import webdriver
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.support.select import Select



def move_coordinate_calculation(points, action):
    coord = points.tolist() # Преобразование многомерного (N массива np) в список питон
    for point in coord:
        point_x = point[0]
        point_y = point[1]

        action.pointer_action.move_to_location(point_x,point_y)
        action.perform()
        print(type(coord[0][0]))

        print(point)
    action.pointer_action.click()
    action.perform()
    time.sleep(5)

    return coord[-1]


def start_profile():
    """Запускает только что созданный профиль"""
    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    # to supress the error messages/logs
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options, executable_path=r'C:\WebDrivers\chromedriver.exe')
    driver.get("https://selenium.dev/selenium/web/scrolling_tests/frame_with_nested_scrolling_frame_out_of_view.html")
    driver.switch_to.active_element
    return driver

def click_on_registraion(driver):
    time.sleep(0.2)
    clickable = driver.find_element(By.XPATH, "//iframe[@name='nested_scrolling_frame']")
    action = ActionChains(driver,duration=1)
    scroll_origin = ScrollOrigin.from_viewport(10,10)
    action.scroll_from_origin(scroll_origin=scroll_origin, delta_x= 0,delta_y= 12000)
    action.perform()
    time.sleep(5)
    size_window = driver.get_window_size() # Размер окна
    loc = clickable.location # Координаты элемента
    height_window = size_window['height']/2
    width_window = size_window['width']/2
    action =  ActionBuilder(driver, duration=1)
    points = curve.pointer(first_x = width_window, first_y = height_window, last_coord=loc) # координаты движения курсора
    last_coord = move_coordinate_calculation(points, action)
    time.sleep(5)
    exit()
    time.sleep(0.2)
    data = {
        "driver": driver,
        "action": action,
        "last_coord": last_coord
    }
    return data


def con(data):
    driver = data['driver']
    driver.refresh()
    clickable = driver.find_element(By.XPATH, "//a[@id='click']")
    loc = clickable.location
    points = curve.pointer(first_x = data['last_coord'][0], first_y = data['last_coord'][1], last_coord=loc)
    last_coord = move_coordinate_calculation(points, data["action"])


def main():
    qwe = start_profile()
    data = click_on_registraion(qwe)
    con(data)


main()