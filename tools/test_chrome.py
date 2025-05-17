from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get("https://live.euronext.com/en/popout-page/getIndexComposition/NL0000000107-XAMS")
print(driver.title)
driver.quit()
