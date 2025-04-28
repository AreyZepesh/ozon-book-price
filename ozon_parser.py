import utils
import plots
from getDriver import getDriver
from database import addPrice as addPriceToDB

from time import sleep
from datetime import datetime as dt
from selenium.webdriver.common.by import By

PAUSE = True
PRICEDCT = {'book_id': None, 'datetime': None, 'price': None, 'article': None, 'typeSearch': None}
DATE_TIME = dt.now().strftime("%Y-%m-%d %H:%M")

def pauseW(fn):
    def wrapper(*args, **kwargs):
        if PAUSE:
            sleep(1)  # ВРЕМЯ ПАУЗЫ
        return fn(*args, **kwargs)
    return wrapper
    
@pauseW
def findOnSearchPage(driver, book_id, book_title, type) -> dict:
    """Сбор данных по странице поиска. Возвращает словарь c минимальной"""
    def _cardData(cardOBJ) -> dict:
        """Подфункция сбора данных с одной карточки"""
        title = cardOBJ.find_element( By.XPATH, ".//a[@href]//span[contains(@class, 'tsBody500Medium')]" ).text
        # Для отладки
        # print(f", |{book_title}| >>>  |{title}|")
        if not utils.isTITLEinSTR(book_title, title):
            # Для отладки
            # print("Не совпадает")
            return
        card = PRICEDCT.copy()
        card['book_id'] = book_id
        href = cardOBJ.find_element( By.XPATH, ".//a[@href]" )
        card['article'] = href.get_attribute("href").split('/?')[0].split('-')[-1]
        card['price']  = utils.normalizePrice(cardOBJ.find_element( By.XPATH, ".//span[contains(@class, 'tsHeadline')]" ).text)
        card['datetime'] = DATE_TIME
        card['typeSearch'] = type
        return card
    
    cardsOBJs = driver.find_elements( By.XPATH, "//div[@data-index and @class]" )
    if cardsOBJs == []:
        return
    
    if 'sorting=price' not in driver.current_url:
        # Сбор всех цен и вывод минимальной в случае если сортировка не найдена
        finds = []
        for cardOBJ in cardsOBJs:
            d_find = _cardData(cardOBJ) 
            if d_find is not None:
                finds.append(d_find)
        # finds = [_cardData(cardOBJ) for cardOBJ in cardsOBJs]
        # finds = [find for find in finds if find is not None]
        if finds == []:
            return
        
        return utils.minPrice(finds)

    for cardOBJ in cardsOBJs:
        d_find = _cardData(cardOBJ) 
        if d_find is not None:
            return d_find

@pauseW
def findOnProductPage(driver, book_id, book_title, type) -> dict:
    """Сбор данных на странице товара"""
    card = PRICEDCT.copy()
    card['book_id'] = book_id
    
    title = driver.find_element( By.XPATH, "//h1[contains(@class, 'tsHeadline550Medium')]" ).text
    if not utils.isTITLEinSTR(book_title, title):
            return
    
    card['article'] = driver.find_element( By.XPATH, "//div[contains(text(),'Артикул')]" ).text.replace('Артикул: ', '')
    prices = driver.find_elements( By.XPATH, "//div[@data-widget='webPrice']//span" )
    card['price'] = min( [utils.normalizePrice(f.text) for f in prices] ) 
    card['datetime'] = DATE_TIME
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

def authToOzon(driver) -> None:
    driver.get('https://www.ozon.ru/ozonid')
    sleep(5)
    secret = utils.getEnv('OZON_NUMBER')

    numArea = driver.find_element(By.XPATH, '//input[@type="tel"]')
    numArea.send_keys(secret)


    submitButton = driver.find_element(By.XPATH, '//button[@type="submit"]')
    submitButton.click()

    codeArea = driver.find_element(By.XPATH, '//input[@type="number"]')
    sleep(30)
    code = None
    for x in range(5):
        code = utils.getCodeFromEmail()
        if code is None:
            sleep(30)
        else:
            break
    codeArea.send_keys(code)
    sleep(5)

"""Куки
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
"""



def main():
    chrome_version = utils.getEnv("CHROMIUM_VERSION")
    baseURL = "https://ozon.kz/"
    driver = getDriver(False, chrome_version)
    driver.get(baseURL)
    
    try:
        auth_msg = 'Начало попытки аутентификации'
        authToOzon(driver)
        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'Кабинет')]")
            auth_msg = "Парсим под логином"
        except:
            auth_msg = "Парсим без логина"
    except:
        auth_msg = "Аутентификация не удалась"
    finally:
        print('>>>   ', auth_msg, '   <<<\n')

    dataList = []
    for book in utils.getAllData(): 
        # Для отладки
        # if book.get('book_id') <= 127:
        #     continue
        print(book['title'])
        for item in book['URLs']:
            print(item)
            
            find = None

            driver.get(item['URL'])
            sleep(1)
            
            try:
                if (item["type"] == "article") and ("product_id" in driver.current_url):
                    pass # TODO ? articleGone()
                elif (item["type"] == "article") and ("product" in driver.current_url):
                    find = findOnProductPage(driver, book['book_id'], book['title'], item['type'])
                elif "category/knigi-16500" in driver.current_url:
                    find = findOnSearchPage(driver, book['book_id'], book['title'], item['type'])

                # Для отладки
                # if find is not None:
                #     print(find)

                if find is not None and find not in dataList:
                    dataList.append(find)

            except Exception as ex:
                print(ex)

            # Для отладки
            # input("\n   >>>   Next")
                
    sleep(2)
    driver.quit()
    print("\n!!!---   ПАРСИНГ ЗАВЕРШЕН   ---!!!\n")
    
    if len(dataList) > 0:
        dataList = utils.minPriceByKeys(dataList)
        dataList = utils.uniArticleByKeys(dataList)

        utils.toJSON(dataList)
        utils.dictToCSV(dataList)

        for data in dataList:
            addPriceToDB(data)

        plots.plotPriceTable()



if __name__  == '__main__':
    main()