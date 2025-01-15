import database
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

def searchList(book: dict) -> dict:
    def _articleURL(_book) -> list:
        aURLs = []
        # Генерин URL для артиклей
        if _book['articles']:
            for art in _book['articles']:
                URL = f"https://ozon.kz/product/{art}"
                aURLs.append({'book_id': _book['id'], 'URLs': URL, 'type': 'article'})
        return aURLs

    def _isbnURL(_book, _param) -> list:
        iURLs = []
        if _book['isbns']:
            for isbn in _book['isbns']:
                URL = f"https://ozon.kz/category/knigi-16500/?sorting=price{_param}&text={isbn}"
                iURLs.append({'book_id': _book['id'], 'URLs': URL, 'type': 'isbn'})
        return iURLs

    def _parametrs(_book) -> str:
        """Генерируем дополнительные опции поиска для isbn и текста"""
        _param = str()
        if _book['year_start'] and _book['year_end']:
            releaseyear = '&releaseyear=' + str(_book["year_start"]) + '.000;' + str(_book["year_end"]) + '.000' 
            _param += releaseyear
        elif _book['year_start']:
            releaseyear ='&releaseyear=' + str(_book['year_start']) + '.000;' + str(_book['year_start']) + '.000'
            _param += releaseyear
        if _book['options']:
            for opt in _book['options']:
                if opt is not None:
                    _param = _param + '&' + opt
        return _param

    URLs = []
 
    # Определяем ограничения поиска и убираем из списка опций
    if book['options']:
        if ('onlyArticle' in book['options']) and (book['articles'] is not None):
            return _articleURL(book)
        elif ('onlyArticle' in book['options']) and (book['articles'] is  None):
            book['options'].pop(book['options'].index('onlyArticle'))

        if ('onlyISBN' in book['options']) and (book['isbns'] is not None):
            return _isbnURL(book, _parametrs(book))
        elif ('onlyISBN' in book['options']) and (book['isbns'] is None):
            book['options'].pop(book['options'].index('onlyISBN'))
    
    search_text = book['title']
    if book['author']:
        search_text = search_text + ' ' + book['author']
    search_text = search_text.replace(' ', '+')

    add_search_param = _parametrs(book)
    URL = f"https://ozon.kz/category/knigi-16500/?sorting=price{add_search_param}&text={search_text}"
    URLs.append({'book_id': book['id'], 'URLs': URL, 'type': 'text'})
    URLs += _isbnURL(book, add_search_param)
    URLs += _articleURL(book)

    return URLs

def getAllURLs():
    allBooks = database.getAllBooks()
    URLs = []
    for book in allBooks:
        URLs += searchList(book)
    return URLs

def main():
    URLs = getAllURLs()
    # print(len(URLs))
    for url in getAllURLs():
        print(url)
    # baseURL = "https://ozon.kz/"
    # bookURL = "https://ozon.kz/category/knigi-16500/?sorting=price&text=5-251-00198-3"
    # productURL = "https://ozon.kz/product/1792268276"

    # driver = getDriver()
    # driver.get(baseURL)
    # driver.implicitly_wait(5)
    # # sleep(5)

    # # addCookie(driver)

    # driver.get(bookURL)
    # res = searchPageData(driver)

    # driver.get(productURL)
    # res.append( productPageData(driver) )

    # # saveCookie(driver)

    # sleep(2)
    # driver.close()
    # # driver.quit()

    # for r in res:
    #     print(r)

    pass
if __name__  == '__main__':
    main()