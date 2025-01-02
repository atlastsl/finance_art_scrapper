from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd


if __name__ == "__main__":
    cService = webdriver.ChromeService(executable_path="C:/Users/AYSIF/Documents/Programmes/chromedriver-win64"
                                                       "/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=cService)
    driver.get("https://webscraper.io/test-sites/e-commerce/allinone")

    prices = driver.find_elements(By.XPATH, '//h4[@class="price float-end card-title pull-right"]')
    names = driver.find_elements(By.XPATH, '//a[@class="title"]')
    descriptions = driver.find_elements(By.XPATH, '//p[@class="description card-text"]')

    prices_list = []
    names_list = []
    descriptions_list = []
    for p in range(len(prices)):
        prices_list.append(prices[p].text)
    for s in range(len(names)):
        names_list.append(names[s].text)
    for d in range(len(descriptions)):
        descriptions_list.append(descriptions[d].text)

    dataframe = pd.DataFrame({'Name': names_list, 'Price': prices_list, 'Description': descriptions_list})
    driver.close()

    print(dataframe)

