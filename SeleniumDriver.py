
from selenium import webdriver
from backports import configparser

def read_config():
    config = configparser.ConfigParser() 
    configFilePath = 'login.config'
    config.read(configFilePath)
    username = config['login-info']['username']
    password = config['login-info']['password']
    return (username, password)      


def log_in():
    username, password = read_config()
    driver = webdriver.Chrome()
    driver.get ("https://public.traviscountytx.gov/aaro/")
    driver.find_element_by_id("input_1").send_keys(username)
    driver.find_element_by_id ("input_2").send_keys(password)
    driver.find_element_by_css_selector(".credentials_input_submit").click()
    return driver
