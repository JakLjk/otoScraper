from typing import Literal
from selenium.webdriver import Firefox, Chrome, Safari, Edge
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as firefoxOptions

def set_selenium_driver(browser_type:Literal["firefox"],
                        headless:bool=True):
    
    accepted_drivers = {
        "firefox":webdriver.Firefox}
    accepted_options = {
        "firefox":firefoxOptions}
    
    options = accepted_options[browser_type]()
    options.headless=headless
    return accepted_drivers[browser_type](options=options)
