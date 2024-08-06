from abc import ABC
from typing import Literal
from logging import Logger
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .webpage_element import webpageElement
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
                    wait_for_element:int=0) -> webpageElement:
        
        return webpageElement(driver=self.web_driver,
                            searched_key=searched_key,
                            element_type=element_type,
                            wait_for_element=wait_for_element)

    def get_all_elements(self, 
                    searched_key:str,
                    element_type:Literal["div"]) -> list[webpageElement]:
        pass

    def close_webpage(self):
        self.web_driver.quit()



