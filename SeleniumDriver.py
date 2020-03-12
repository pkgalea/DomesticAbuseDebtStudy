
from selenium import webdriver
from backports import configparser

class SeleniumDriver:

    def __init__(self):
        self.username=""
        self.password=""
        self.driver = ""

    def read_config(self):
        """ 
            Reads the configuration file to get the login information for the courthouse website

            Parameters: None

            Returns: None  
        """
        config = configparser.ConfigParser() 
        configFilePath = 'login.config'
        config.read(configFilePath)
        self.username = config['login-info']['username']
        self.password = config['login-info']['password']  


    def log_in(self):
        """ 
            Uses Selenium Chrome driver to open up the travis county website page and login.

            Parameters: None

            Returns: None  
        """
        self.read_config()
        self.driver = webdriver.Chrome()
        self.driver.get ("https://public.traviscountytx.gov/aaro/")
        self.driver.find_element_by_id("input_1").send_keys(self.username)
        self.driver.find_element_by_id ("input_2").send_keys(self.password)
        self.driver.find_element_by_css_selector(".credentials_input_submit").click()

    def close(self):
        self.driver.close()