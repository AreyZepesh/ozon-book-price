from selenium_stealth import stealth
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager

def getDriver(headless=False):
    # опции нужны для линукс версии, особенно без гпу и сандбокса
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # options.add_argument("--disable-setuid-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(headless=headless, options=options, 
                       driver_executable_path=ChromeDriverManager().install(),
                       )
    
    # Эти параменты теоретически могут отличаться на разных системах
    # При этом - те же параментры прекрастно гуглятся, поэтому - оставлю
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''})
    
    # Скрываем работу селениум, юзерагента нагуглил
    stealth(driver = driver,
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/83.0.4103.53 Safari/537.36',
            languages = ["ru-RU", "ru"],
            vendor = "Google Inc.",
            platform = "Win32",
            webgl_vendor = "Intel Inc.",
            renderer = "Intel Iris OpenGL Engine",
            fix_hairline = True,
            run_on_insecure_origins = True,)
    driver.implicitly_wait(10)
    return driver

def main():
    pass

    print(ChromeDriverManager().install())
    #return getDriver()

if __name__  == '__main__':
    main()