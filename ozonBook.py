from getDriver import getDriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

try:
    baseUrl = "https://ozon.kz/"

    driver = getDriver()
    driver.implicitly_wait(5)
    driver.get(baseUrl)
    driver.maximize_window()
    sleep(1)
        
    with open("bookList.txt", 'r', encoding="utf8") as file:
        bookList = [b.strip() for b in file.readlines()]


    # listURLs = []
    for book in bookList:
        urlSearch = f"https://ozon.kz/category/knigi-16500/?text={book}"
        driver.get(urlSearch)
        # sleep(1)
        # elS = driver.find_elements(By.XPATH, '//a[contains(@href, "product")]')
        # for el in elS:
        #     listURLs.append('/'.join(el.get_attribute('href').split('/')[:-1]))
        sleep(1)
    # listURLs = list(set(listURLs))
    # for listURL in listURLs:
    #     print(listURL)
    sleep(10)
except Exception as ex:
    pass
    # print(ex)

finally:
    pass
    driver.close()
    driver.quit()