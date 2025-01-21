import database
import utils
from getDriver import getDriver

import json
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By

PAUSE = True
PRICEDCT = {'book_id': None, 'datetime': None, 'price': None, 'article': None, 'typeSearch': None}

def pauseW(fn):
    def wrapper(*args, **kwargs):
        if PAUSE:
            sleep(1)  # ВРЕМЯ ПАУЗЫ
        return fn(*args, **kwargs)
    return wrapper
    
@pauseW
def findOnSearchPage(driver, book_id, book_title, type) -> dict:
    """Сбор данных по странице поиска.
    Возвращает словарь"""
    def _cardData(cardOBJ) -> dict:
        """Подфункция сбора данных с одной карточки"""
        card = PRICEDCT.copy()
        card['book_id'] = book_id

        title = cardOBJ.find_element( By.XPATH, ".//a[@href]//span[contains(@class, 'tsBody500Medium')]" ).text
        if not utils.isTITLEinSTR(book_title, title):
            # print('>>> ', title)
            return
        # if '|' in title:
        #     card['title'], card['author'] = title.split('|')
        #     card['author'] = utils.normalizeStr(card['author'])
        # else:
        #     card['title'], card['author'] = title, None
        # card['title'] = utils.normalizeStr(card['title'])

        href = cardOBJ.find_element( By.XPATH, ".//a[@href]" )
        card['article'] = href.get_attribute("href").split('/?')[0].split('-')[-1]
        card['price']  = utils.normalizePrice(cardOBJ.find_element( By.XPATH, ".//span[contains(@class, 'tsHeadline')]" ).text)
        card['datetime'] = str(datetime.now())
        card['typeSearch'] = type
        return card
    
    if 'sorting=price' not in driver.current_url:
        # print('--->>> ', book_id, book_title, driver.current_url)
        #  TODO Проверка на наличии сортировки по цене. Сбор всех цен и вывод минимальной в случае если сортировка не найдена?
        # finds = [_cardData(cardOBJ)  for cardOBJ in cardsOBJs]
        pass

    cardsOBJs = driver.find_elements( By.XPATH, "//div[@data-index]" )
    for cardOBJ in cardsOBJs:
        d_find = _cardData(cardOBJ) 
        if d_find is not None:
            return d_find
        return 

@pauseW
def findOnProductPage(driver, book_id, book_title, type) -> dict:
    """Сбор данных на странице товара"""
    card = PRICEDCT.copy()
    card['book_id'] = book_id
    
    title = driver.find_element( By.XPATH, "//h1[contains(@class, 'tsHeadline550Medium')]" ).text
    if not utils.isTITLEinSTR(book_title, title):
            # print('>>> ', title)
            return
    # if '|' in title:
    #     card['title'], card['author'] = title.split('|')
    #     card['author'] = utils.normalizeStr(card['author'])
    # else:
    #     card['title'], card['author'] = title, None
    # card['title'] = utils.normalizeStr(card['title'])
    
    card['article'] = driver.find_element( By.XPATH, "//div[contains(text(),'Артикул')]" ).text.replace('Артикул: ', '')
    prices = driver.find_elements( By.XPATH, "//div[@data-widget='webPrice']//span" )
    card['price'] = min( [utils.normalizePrice(f.text) for f in prices] ) 
    card['datetime'] = str(datetime.now())
    card['typeSearch'] = type
    return card

@pauseW
def articleGone(driver) -> None:
    # Если по артикулу товара не найдено, перекидывает на страницу поиска по названию и артиклю, где предлогает пишет "Этот товар закончился" похожие товары.
    # Что приколько - если руками сгенерировать эту ссылку по существующему товару - тоже будет выдавать тоже самое. 
    # Шаблон строки "https://ozon.kz/category/knigi-16500/?text={title}&product_id={article}"
    # TODO нужно ли удалять такой артикул из базы?
    print("-->", driver.find_element( By.XPATH, "//h2[contains(text(),'Этот товар закончился')]" ).text)
    pass

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
                aURLs.append({'URL': URL, 'type': 'article'})
        return aURLs

    def _isbnURL(_book, _param) -> list:
        iURLs = []
        if _book['isbns']:
            for isbn in _book['isbns']:
                URL = f"https://ozon.kz/category/knigi-16500/?sorting=price{_param}&text={isbn}"
                iURLs.append({'URL': URL, 'type': 'isbn'})
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
    URLs.append({'URL': URL, 'type': 'text'})
    URLs.extend( _isbnURL(book, add_search_param) )
    URLs.extend( _articleURL(book) )

    return URLs

def getAllData() -> list:
    """Данные для поиска, по всем книгам.
    Возвращает список словарей 
    {book_id, title, {URL, type}}.
    Словарей на книгу может быть больше одного"""
    allData = []
    for book in database.getAllBooks():
        data = {'book_id': book['id'], 'title': book['title'], 'URLs': []}
        data['URLs'].extend( getSearhData(book) )
        if data['URLs'] != []:
            allData.append(data)
    return allData

def main():
    # TODO 
    # минимальную цену в переборе по артикулам и исбн (если их больше одного)
    # findOnSearchPage вместо всех / не обходить все, а вернуть первую, так как сортировка по цене?     sorting=price

    baseURL = "https://ozon.kz/"
    driver = getDriver(True)
    driver.get(baseURL)
    # driver.implicitly_wait(10)

    res = []
    # Переделать вывод, один результат на тип, +id +type
    for book in getAllData(): 
        print(book['title'])
        for item in book['URLs']:
            print(item)
            
            find = None

            driver.get(item['URL'])
            sleep(1)
            
            try:
                if (item["type"] == "article") and ("product_id" in driver.current_url):
                    pass # articleGone()
                elif (item["type"] == "article") and ("product" in driver.current_url):
                    find = findOnProductPage(driver, book['book_id'], book['title'], item['type'])
                elif "category/knigi-16500" in driver.current_url:
                    find = findOnSearchPage(driver, book['book_id'], book['title'], item['type'])

                if find is not None:
                    res.append(find)

            except Exception as ex:
                print(ex)

    # тута можно убрать лишние результаты по книге
                
    print("\n!!!---   ПАРСИНГ ЗАВЕРШЕН   ---!!!\n")

    with open('./tmp/out.json', 'w', encoding='utf8') as file:
        json.dump(res, file)
    utils.dictToCSV(res, f'./tmp/out.csv')

    sleep(2)
    driver.close()
    # driver.quit()


    pass

if __name__  == '__main__':
    main()