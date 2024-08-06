from abc import ABC
from typing import Literal
from logging import Logger
from selenium.webdriver.remote.webdriver import WebDriver

from .webpage_element import webpageElements
from .selenium_driver import set_selenium_driver


class Webpage():
    def __init__(self,
                browser_type:str="firefox", 
                headless:bool=True, 
                log:Logger=None) -> None:
        self.web_driver:WebDriver = set_selenium_driver(
                                    browser_type=browser_type,
                                    headless=headless)
        self.webpage_raw:str = None



    def load_page(self, link:str):
        self.web_driver.get(link)

    def get_element(self, 
                    searched_key:str,
                    element_type:str,
                    wait_for_element:int=0,
                    retries_if_obstructed:int=2,
                    wait_time_if_obstructed:int=0.5,
                    raise_error_if_multiple_elements=True) -> webpageElements:
        
        #TODO return error if more than one element found
        return webpageElements(self.web_driver,
                               searched_key,
                               element_type,
                               wait_for_element,
                               raise_error_if_multiple_elements)


    def close_webpage(self):
        self.web_driver.quit()



