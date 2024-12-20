from selenium_stealth import stealth
import undetected_chromedriver as uc

def getDriver():
    # options = uc.ChromeOptions()
    # options.add_argument("start-maximized")

    driver = uc.Chrome()
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''})
    
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
    return driver

def main():
    getDriver()

if __name__  == '__main__':
    main()