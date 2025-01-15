import database
from utils import normalizePrice
from utils import normalizeStr
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
def findOnSearchPage(driver) -> list:
    """Сбор данных по странице поиска.
    Возвращает список словарей"""
    def _cardData(cardOBJ) -> dict:
        """Подфункция сбора данных с одной карточки"""
        card = {}

        title = cardOBJ.find_element( By.XPATH, ".//a[@href]//span[contains(@class, 'tsBody500Medium')]" ).text
        if '|' in title:
            card['title'], card['author'] = title.split('|')
            card['author'] = normalizeStr(card['author'])
        else:
            card['title'], card['author'] = title, None
        card['title'] = normalizeStr(card['title'])

        href = cardOBJ.find_element( By.XPATH, ".//a[@href]" )
        card['article'] = href.get_attribute("href").split('/?')[0].split('-')[-1]
        card['price']  = normalizePrice(cardOBJ.find_element( By.XPATH, ".//span[contains(@class, 'tsHeadline')]" ).text)
        card['datetime'] = str(datetime.now())
        return card
    
    cardsOBJs = driver.find_elements( By.XPATH, "//div[@data-index]" )
    cards = [_cardData(cardOBJ) for cardOBJ in cardsOBJs]
    return cards

@pauseW
def findOnProductPage(driver) -> dict:
    """Сбор данных на странице товара"""
    card = {}
    
    title = driver.find_element( By.XPATH, "//h1[contains(@class, 'tsHeadline550Medium')]" ).text
    if '|' in title:
        card['title'], card['author'] = title.split('|')
        card['author'] = normalizeStr(card['author'])
    else:
        card['title'], card['author'] = title, None
    card['title'] = normalizeStr(card['title'])
    
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

def getSearhData(book: dict) -> list:
    """Получение списка словарей данных, 
    для поиска и обработки полученных данных.
    Принимает словарь одной книги из database.getAllBooks().
    Возвращает список словарей {book_id, title, URL, type}.
    Словарей на книгу может быть больше одного"""
    def _articleURL(_book) -> list:
        aURLs = []
        if _book['articles']:
            for art in _book['articles']:
                URL = f"https://ozon.kz/product/{art}"
                aURLs.append({'book_id': _book['id'], 'title': _book['title'], 'URL': URL, 'type': 'article'})
        return aURLs

    def _isbnURL(_book, _param) -> list:
        iURLs = []
        if _book['isbns']:
            for isbn in _book['isbns']:
                URL = f"https://ozon.kz/category/knigi-16500/?sorting=price{_param}&text={isbn}"
                iURLs.append({'book_id': _book['id'], 'title': _book['title'], 'URL': URL, 'type': 'isbn'})
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
    URLs.append({'book_id': book['id'], 'title': book['title'], 'URL': URL, 'type': 'text'})
    URLs += _isbnURL(book, add_search_param)
    URLs += _articleURL(book)

    return URLs

def getAllData() -> list:
    """Возвращает список словарей 
    {book_id, title, URL, type}.
    Словарей на книгу может быть больше одного"""
    allBooks = database.getAllBooks()
    URLs = []
    for book in allBooks:
        URLs += getSearhData(book)
    return URLs

def main():
    # TODO 
    # проверку ссылки
    # проверку названия книги
    # минимальную цену в findOnSearchPage вместо всех
    # объединение входного и выходного словаря

    # {'book_id': 1, 'title': 'Свет вечный', 'URL': 'https://ozon.kz/category/knigi-16500/?sorting=price&text=Свет+вечный+Сапковский', 'type': 'text'}
    baseURL = "https://ozon.kz/"
    driver = getDriver()
    driver.get(baseURL)
    driver.implicitly_wait(5)

    res = []
    for item in getAllData(): 
        print(item)
        driver.get(item['URL'])
        if item["type"] == "article":
            res.append(findOnProductPage(driver))
        else:
            res.extend(findOnSearchPage(driver))

    for r in res:
        print(r)

    sleep(2)
    driver.close()
    # driver.quit()


    pass
if __name__  == '__main__':
    main()