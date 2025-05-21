from selenium_stealth import stealth
import undetected_chromedriver as uc
from time import sleep

# from datetime import datetime as dt
import os

def getDriver(headless=False, version_main = None, testMode = False):
    driver = None
    last_exception = None

    for attempt in range(3):
        try:
            options = uc.ChromeOptions()
            # if headless:
            #     options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            # options.add_argument("--disable-extensions") #
            # options.add_argument("--disable-application-cache") #
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            # options.add_argument("--disable-setuid-sandbox") #
            # options.add_argument("--disable-dev-shm-usage") #

            # options.add_argument("--remote-debugging-port=0") #
            # options.add_argument("--disable-software-rasterize") #
            # Ниже сомнительная опция
            # options.add_argument(f"–-user-data-dir={!}") ##
            # опции для отладки
            # options.add_argument("--enable-logging") #
            # options.add_argument("--v=1") #
            # options.add_argument(f"--log-file={os.getcwd()}/logs/{dt.now().strftime("%Y-%m-%d  %H-%M")}chromium.log") #
            # опции нужны для линукс версии, особенно без гпу и сандбокса
            
            sleep(attempt*5)

            browser_executable_path = None
            # driver_executable_path = None
            if os.path.exists('./chrome-linux64/chrome'):
                browser_executable_path = './chrome-linux64/chrome'
            if os.path.exists('./chrome-win64/chrome.exe'):
                browser_executable_path = './chrome-win64/chrome.exe'
            # if os.path.exists('./chromedriver-linux64/chromedriver'):
            #     driver_executable_path = './chromedriver-linux64/chromedriver'

            driver = uc.Chrome(
                headless=headless, 
                options=options, 
                version_main = version_main,
                # driver_executable_path = driver_executable_path,
                browser_executable_path = browser_executable_path,
                            )
            # print(driver.options.arguments)
        except Exception as ex:
            last_exception = ex
            print(f"Try {attempt+1}: \n {ex} \n\n")
            continue
        else:
            break
    
    if driver is None:
        raise last_exception
    
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
                   'Chrome/136.0.4103.53 Safari/537.36',
            languages = ["ru-RU", "ru"],
            vendor = "Google Inc.",
            platform = "Win32",
            webgl_vendor = "Intel Inc.",
            renderer = "Intel Iris OpenGL Engine",
            fix_hairline = True,
            run_on_insecure_origins = True,)
    driver.command_executor.set_timeout(1200)
    driver.implicitly_wait(120)
    return driver

def main():
    pass

if __name__  == '__main__':
    main()