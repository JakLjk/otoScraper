from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep

from config import URL, TIMERS
from otomoto.objects import OFFER

load_time = TIMERS.standard_load_element_wait


def try_close_onetrust_button(wd:WebDriver):
    onetrust_button = WebDriverWait(wd, load_time).until(
        EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
    )
    onetrust_button.click()


def get_all_car_brands(driver:WebDriver) -> list:
    """Get all brand names that are available on the otomoto webpage"""
    link = URL.otomoto_main_webpage
    wd = driver
    wd.get(link)
    try_close_onetrust_button(wd)
    sleep(0.25)
    WebDriverWait(driver, 3).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "onetrust-pc-dark-filter ot-fade-in"))
    )
    car_type_list_button = wd.find_element(By.CSS_SELECTOR, '[aria-label="Marka pojazdu"]')
    car_type_list_button.click()
    car_list = wd.find_element(By.CLASS_NAME, "ooa-1ohf0ui")
    car_list = car_list.find_elements(By.CLASS_NAME, "ooa-x4ohs6")
    car_list = [link.get_attribute('id') for link in car_list]    
    return car_list


def get_number_of_pages(driver:WebDriver,
                        scrollpage_link:str):
    wd = driver
    wd.get(scrollpage_link)
    try_close_onetrust_button(wd)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    num_pages = wd.find_elements(By.CLASS_NAME, "ooa-1xgr17q")
    num_pages = num_pages[-1].text
    return num_pages


def get_all_offer_links_from_scrollpage(driver:WebDriver,
                                        scrollpage_link:str) -> list:
    wd = driver
    wd.get(scrollpage_link)
    try_close_onetrust_button(wd)
    sleep(0.25)
    offer_box = wd.find_element(By.CLASS_NAME, "ooa-r53y0q.eupw8r111")
    offer_links = offer_box.find_elements(By.CLASS_NAME, "efpuxbr9.ooa-1ed90th.er34gjf0")
    offer_links  = [l.find_element(By.TAG_NAME, 'a').get_attribute('href') for l in offer_links]
    return offer_links


def get_offer_details(driver:WebDriver,
                    link:str) -> OFFER:

    wd = driver 
    wd.get(link)
    try_close_onetrust_button(wd)
    tytul = wd.find_element(By.CLASS_NAME, "offer-title.big-text.etrkop92.ooa-13tge55.er34gjf0").text

    _box = wd.find_elements(By.CLASS_NAME, "edazosu4.ooa-1afacld.er34gjf0")
    data_dodatnia = _box[0].text
    id_oferty = _box[1].text

    cena = wd.find_element(By.CLASS_NAME, "offer-price__number").text

    _box = wd.find_elements(By.CLASS_NAME, "e1ho6mkz2.ooa-1rcllto.er34gjf0")
    przebieg = _box[0].text
    rodzaj_paliwa = _box[1].text
    skrzynia_biegow = _box[2].text
    typ_nadwozia = _box[3].text
    pojemnosc_silnika = _box[4].text
    moc_silnika = _box[5].text

    opis = wd.find_element(By.CLASS_NAME, "ooa-unlmzs.e18op59x2").text

    szczegoly = wd.find_element(By.CLASS_NAME, "ooa-h9kvji.eyfqfx02")
    szczegoly = szczegoly.find_elements(By.CLASS_NAME, "ooa-162vy3d.eyfqfx03")
    szczegoly = {k: v for k,v in [s.text.split("\n") for s in szczegoly]}

    wyposazenie = wd.find_elements(By.CLASS_NAME, "evespt84.ooa-1i4y99d.er34gjf0")
    wyposazenie = [w.text for w in wyposazenie]
    print(wyposazenie)






    return tytul, data_dodatnia, id_oferty, cena, przebieg, moc_silnika, opis