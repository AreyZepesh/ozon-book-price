from utils import normalizePrice
from getDriver import getDriver

import json
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By

PAUSE = True

def pauseW(fn):
    def wrapper(*args, **kwargs):
        if PAUSE:
            sleep(2)  # ВРЕМЯ ПАУЗЫ
        return fn(*args, **kwargs)
    return wrapper
    
@pauseW
def searchPageData(driver) -> list:
    """Сбор данных по странице поиска.
    Возвращает список словарей"""
    def _cardData(cardOBJ) -> dict:
        """Подфункция сбора данных с одной карточки"""
        card = {}
        href = cardOBJ.find_element( By.XPATH, ".//a[@href]" )
        # card["URL"] = href.get_attribute("href").split('/?')[0]
        card['article'] = href.get_attribute("href").split('/?')[0].split('-')[-1]
        card['price']  = normalizePrice(cardOBJ.find_element( By.XPATH, ".//span[contains(@class, 'tsHeadline')]" ).text)
        card['datetime'] = str(datetime.now())
        return card
    
    cardsOBJs = driver.find_elements( By.XPATH, "//div[@data-index]" )
    cards = [_cardData(cardOBJ) for cardOBJ in cardsOBJs]
    return cards

@pauseW
def productPageData(driver) -> dict:
    """Сбор данных на странице товара"""
    card = {}
    # card["URL"] = driver.current_url
    card['article'] = driver.find_element( By.XPATH, "//div[contains(text(),'Артикул')]" ).text.replace('Артикул: ', '')
    prices = driver.find_elements( By.XPATH, "//div[@data-widget='webPrice']//span" )
    card['price'] = min( [normalizePrice(f.text) for f in prices] ) 
    card['datetime'] = str(datetime.now())
    return card

@pauseW
def addCookie(driver, file='./tmp/cookies.json'):
    # куки входа... как долго проживут?
    with open(file, 'r') as file:
        cookies = json.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

@pauseW
def saveCookie(driver, file='./tmp/new.json'):
    with open(file, 'w') as file:
        json.dump(driver.get_cookies(), file)

def main():
    # pass
    baseURL = "https://ozon.kz/"
    bookURL = "https://ozon.kz/category/knigi-16500/?sorting=price&text=5-251-00198-3"
    productURL = "https://ozon.kz/product/1792268276"

    driver = getDriver()
    driver.get(baseURL)
    driver.implicitly_wait(5)
    sleep(5)

    # addCookie(driver)

    driver.get(bookURL)
    res = searchPageData(driver)

    driver.get(productURL)
    res.append( productPageData(driver) )

    for r in res:
        print(r)

 

    # saveCookie(driver)
    sleep(2)
    driver.close()
    # driver.quit()

if __name__  == '__main__':
    main()