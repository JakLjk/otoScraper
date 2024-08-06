from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from typing import Literal

class webpageElement():
    def __init__(self, 
                driver:WebDriver,
                searched_key:str,
                element_type:Literal["div", "id", "css-selector"],
                wait_for_element:int=0) -> None:
        by_type = {
                "id":By.ID,
                "css-selector":By.CSS_SELECTOR}

        wd = driver
        if wait_for_element > 0:
            self.element = (WebDriverWait(driver, wait_for_element)
                        .until(EC.presence_of_element_located((by_type[element_type], searched_key))))
        else:
            self.element = wd.find_element(by_type[element_type], searched_key)
        

    def click_element(self):
        self.element.click()
