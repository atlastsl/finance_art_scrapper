from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd


def f():
    df = pd.DataFrame(columns=['Player', 'Salary', 'Year'])  # creates master dataframe

    cService = webdriver.ChromeService(
        executable_path="C:/Users/AYSIF/Documents/Programmes/chromedriver-win64"
                        "/chromedriver-win64/chromedriver.exe")  # '/Users/bpfalz/Downloads/chromedriver' for my macbook
    driver = webdriver.Chrome(service=cService)

    for yr in range(1990, 2023):
        page_num = str(yr) + '-' + str(yr + 1) + '/'
        url = 'https://hoopshype.com/salaries/players/' + page_num
        driver.get(url)

        players = driver.find_elements(By.XPATH, '//td[@class="name"]')
        salaries = driver.find_elements(By.XPATH, '//td[@class="hh-salaries-sorted"]')

        players_list = []
        for p in range(len(players)):
            players_list.append(players[p].text)

        salaries_list = []
        for s in range(len(salaries)):
            salaries_list.append(salaries[s].text)

        p = int(
            len(players_list) / 2) + 1  # marks position of first player in players_list -- first half of list is empty
        s = int(
            len(salaries_list) / 2) - 1  # marks position of last salary of salaries_list -- second half of list is empty

        data_tuples = list(
            zip(players_list[p:], salaries_list[1:s]))  # list of each players name and salary paired together
        temp_df = pd.DataFrame(data_tuples, columns=['Player', 'Salary'])  # creates dataframe of each tuple in list
        temp_df['Year'] = yr + 1  # adds season ending year to each dataframe

        print(temp_df)

        df = pd.concat([df, temp_df], ignore_index=True)

    driver.close()


if __name__ == '__main__':
    f()
