from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from typing import Literal

class webpageElements():
    def __init__(self, 
                driver:WebDriver,
                searched_key:str,
                element_type:Literal["div", "id", "css-selector"],
                wait_for_element:int=0,
                raise_error_if_multiple_elements:bool=True) -> None:
        by_type = {
                "id":By.ID,
                "css-selector":By.CSS_SELECTOR}
        wd = driver
        if wait_for_element > 0:
            (WebDriverWait(driver, wait_for_element)
                        .until(EC.presence_of_element_located((by_type[element_type], searched_key))))
        self.elements = wd.find_elements(by_type[element_type], searched_key)
        
        if raise_error_if_multiple_elements and len(self.elements) > 1:
            self.elements = None
            raise Exception("Multiple elements found, although one was excected")
        elif len(self.elements) == 0:
            self.elements = None
            raise NoSuchElementException(f"No element found for {element_type} = {searched_key}")
    
    def click_element(self):
        for element in self.elements:
            element.click()
