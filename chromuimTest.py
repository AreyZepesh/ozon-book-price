from utils import getEnv, makeDir
from getDriver import getDriver
from time import sleep
from datetime import datetime as dt

def main():
    DATE = dt.now().strftime("%Y-%m-%d  %H-%M")
    print(DATE)
    chrome_version = getEnv("CHROMIUM_VERSION")
    baseURL = "https://pvd.dmed.kz/"
    driver = getDriver(True, chrome_version)
    driver.get(baseURL)
    driver.save_screenshot(f"{makeDir('./tmp/screenshots')}/{DATE}.png")
    sleep(2)
    print("Вроде норм, закрываю хром")
    driver.quit()

if __name__  == '__main__':
    main()