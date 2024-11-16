from typing import Literal
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager



def initialise_selenium(browser_type:Literal["firefox"],
                        headless:bool=True) ->WebDriver:
    accepted_drivers = {
        "firefox":webdriver.Firefox}
    accepted_options = {
        "firefox":firefoxOptions}
    
    options = accepted_options[browser_type]()
    options.add_argument('--headless')
    return accepted_drivers[browser_type](options=options)

