import os.path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from utils import (parse_date_locale_fr, parse_date_locale_fr_wout_day, create_quarter_ranges, name_quarter,
                   write_to_pdf, parse_date_locale_en, parse_date_locale_en_2)
import json
import pdfkit

html_base = """
    <!DOCTYPE html>
    <html>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <head>
    <title>Page Title</title>
    </head>
    <body>
    
    @HTML_PDF
    
    </body>
    </html>
"""

base_file_path = "C:/Users/AYSIF/PycharmProjects/TwikitTest/files"


def read_page(driver, page_url):
    driver.get(page_url)
    title = driver.find_element(By.TAG_NAME, 'h1')
    time = driver.find_element(By.TAG_NAME, 'time')
    body = driver.find_element(By.XPATH, '//div[@class="news news-single"]')
    links = body.find_elements(By.TAG_NAME, 'a')
    for i in range(len(links)):
        driver.execute_script("arguments[0].setAttribute('href',arguments[1])", links[i], "#")
    images = body.find_elements(By.TAG_NAME, 'img')
    for i in range(len(images)):
        driver.execute_script("arguments[0].setAttribute('src',arguments[1])", images[i], "")
    # print(body.get_attribute('innerHTML'))
    return f'''
        <h1>{title.text}</h1>
        <span style="font-weight:bold;font-size:1.5em;">{time.text}</span>
        {body.get_attribute('innerHTML')}
    '''


def paginated_list_scrapper(base_url, first_path, articles_finder, next_page_finder, date_parser):
    page = 1
    stop_navigation = False

    cService = webdriver.ChromeService(executable_path="C:/Users/AYSIF/Documents/Programmes/chromedriver-win64"
                                                       "/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=cService)
    driver.get(base_url + first_path)

    articles = []
    while stop_navigation is False:
        articles_urls, articles_dates = articles_finder(driver)
        for a in range(len(articles_urls)):
            # page_article = page_articles[a]
            # link_elm = page_article.find_element(By.XPATH, '//a[@class="search-result-title"]')
            # date_elm = page_article.find_element(By.XPATH, '//span[@class="search-result-date"]')
            link_elm = articles_urls[a]
            date_elm = articles_dates[a]
            page_url = link_elm.get_attribute('href')
            page_title = link_elm.text
            page_date = date_parser(str(date_elm.text).lower())
            articles.append({"url": page_url, "title": page_title, "date": page_date, "site": base_url})
        next_page_url, next_page_number = next_page_finder(driver)
        if next_page_url is not None and next_page_number > page:
            page = next_page_number
            driver.get(base_url + next_page_url if not next_page_url.startswith("https") else next_page_url)
        else:
            stop_navigation = True

    return articles


def write_articles_in_json(articles, outfile_name):
    with open(f"{base_file_path}/articles/{outfile_name}.json", "w", encoding='utf-8') as outfile:
        json.dump(articles, outfile, indent=4)


def f_organize_articles(articles):
    ordered_articles = list(reversed(articles))
    start_date = ordered_articles[0]["date"]
    end_date = ordered_articles[len(articles) - 1]["date"]
    quarters = create_quarter_ranges(start_date, end_date)
    organized_articles = []
    for q in quarters:
        q_articles = [article for article in articles if q[0] <= article["date"].timestamp() < q[1]]
        organized_articles.append((q, q_articles))
    return organized_articles


def g_organize_articles(articles):
    ordered_articles = list(reversed(articles))
    start_date = ordered_articles[0]["date"]
    end_date = ordered_articles[len(articles) - 1]["date"]
    quarters = create_quarter_ranges(start_date, end_date)
    organized_articles = []
    for q in quarters:
        q_articles = [{**article, "date": article['date'].isoformat()}
                      for article in articles if q[0] <= article["date"].timestamp() < q[1]]
        organized_articles.append({"quarter": name_quarter(q), "articles": q_articles})
    return organized_articles


def f_download_articles(organized_articles):
    cService = webdriver.ChromeService(executable_path="C:/Users/AYSIF/Documents/Programmes/chromedriver-win64"
                                                       "/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=cService)
    qc_amf_base_path = base_file_path + "/" + "qc_amf"
    if not os.path.exists(qc_amf_base_path):
        os.makedirs(qc_amf_base_path)
    for q, articles in organized_articles:
        html = ""
        for article in articles:
            html_article = read_page(driver, page_url=article['url'])
            html = html + html_article
        q_path = base_file_path + "/" + name_quarter(q) + ".pdf"
        html = html_base.replace("@HTML_PDF", html)
        write_to_pdf(html, q_path)

    driver.close()


def qc_amf_scrapper():
    base_url = "https://lautorite.qc.ca"
    first_path = "/grand-public/salle-de-presse/actualites?tx_solr%5Bcontroller%5D=Search&tx_solr%5Bpage%5D=1"

    def _articles_finder(driver):
        articles_urls = driver.find_elements(By.XPATH, '//a[@class="search-result-title"]')
        articles_dates = driver.find_elements(By.XPATH, '//span[@class="search-result-date"]')
        return articles_urls, articles_dates

    def _next_page_finder(driver):
        next_page_number = 0
        next_page_url = None
        navigation_pages = driver.find_elements(By.XPATH, '//li[@class="pagination-element"]')
        if len(navigation_pages) > 0:
            next_page = navigation_pages[len(navigation_pages) - 1]
            next_page_a_tag = next_page.find_elements(By.XPATH, '//a[@class="btn btn-primary btn-arrow-right '
                                                                'appendtoken"]')
            if len(next_page_a_tag) > 0:
                next_page_url = next_page_a_tag[0].get_attribute('href')
                next_page_number = list(reversed(next_page_url.split("=")))[0]
                next_page_number = int(next_page_number)
        return next_page_url, next_page_number

    articles = paginated_list_scrapper(base_url, first_path,
                                       lambda _driver: _articles_finder(_driver),
                                       lambda _driver: _next_page_finder(_driver),
                                       lambda date: parse_date_locale_fr(date),
                                       )

    return articles


def bn_can_scrapper():
    base_url = "https://www.banqueducanada.ca"
    first_path = "/nouvelles/?mt_page=1&utility%5B%5D=791"

    def _articles_finder(driver):
        articles_body = driver.find_elements(By.XPATH, '//div[@class="media-body"]')
        articles_urls = []
        articles_dates = []
        for a in range(len(articles_body)):
            date_elm = articles_body[a].find_elements(By.CSS_SELECTOR, 'span.bocss-margin-left-medium.media-date.pull'
                                                                       '-right')
            title_elm = articles_body[a].find_elements(By.CSS_SELECTOR, 'h3.media-heading')
            if len(date_elm) > 0 and len(title_elm) > 0:
                url_elm = title_elm[0].find_element(By.TAG_NAME, 'a')
                articles_urls.append(url_elm)
                articles_dates.append(date_elm[0])
        return articles_urls, articles_dates

    def _next_page_finder(driver):
        next_page_number = 0
        next_page_url = None
        next_pages = driver.find_elements(By.XPATH, '//a[@class="next page-numbers"]')
        if len(next_pages) > 0:
            next_page_url = next_pages[0].get_attribute('href')
            next_page_number = next_page_url.split("&")[0]
            next_page_number = list(reversed(next_page_number.split("=")))[0]
            next_page_number = int(next_page_number)
        return next_page_url, next_page_number

    articles = paginated_list_scrapper(base_url, first_path,
                                       lambda _driver: _articles_finder(_driver),
                                       lambda _driver: _next_page_finder(_driver),
                                       lambda date: parse_date_locale_fr(date)
                                       )

    return articles


def fd_stl_scrapper():
    base_url = "https://fredblog.stlouisfed.org"
    first_path = "/"

    def _articles_finder(driver):
        articles_list = driver.find_element(By.XPATH, "//iframe/following-sibling::div["
                                                      "@class='widget-title']/following-sibling::ul")
        articles_list_items = articles_list.find_elements(By.TAG_NAME, "li")
        articles_urls = []
        articles_dates = []
        for a in range(len(articles_list_items)):
            url_elm = articles_list_items[a].find_element(By.TAG_NAME, 'a')
            articles_urls.append(url_elm)
            articles_dates.append(url_elm)
        return articles_urls, articles_dates

    def _next_page_finder(driver):
        next_page_number = 0
        next_page_url = None
        return next_page_url, next_page_number

    articles = paginated_list_scrapper(base_url, first_path,
                                       lambda _driver: _articles_finder(_driver),
                                       lambda _driver: _next_page_finder(_driver),
                                       lambda date: parse_date_locale_fr_wout_day(date)
                                       )

    return articles


def hm_tgv_scrapper():
    base_url = "https://home.treasury.gov"
    first_path = "/news/press-releases"

    def _articles_finder(driver):
        articles_list_container = driver.find_element(By.CLASS_NAME, "content--2col__body")
        articles_list_items = articles_list_container.find_elements(By.TAG_NAME, "div")
        articles_urls = []
        articles_dates = []
        for a in range(len(articles_list_items)):
            url_elm = articles_list_items[a].find_element(By.TAG_NAME, 'a')
            date_elm = articles_list_items[a].find_element(By.TAG_NAME, 'time')
            articles_urls.append(url_elm)
            articles_dates.append(date_elm)
        return articles_urls, articles_dates

    def _next_page_finder(driver):
        next_page_number = 0
        next_page_url = None
        next_page_container = driver.find_elements(By.CSS_SELECTOR, 'nav.pager')
        if len(next_page_container) > 0:
            next_page_container = next_page_container[0].find_elements(By.CLASS_NAME, "pager__items")
            if len(next_page_container) > 0:
                next_page_container = next_page_container[0].find_elements(By.CLASS_NAME, "pager__item--next")
                if len(next_page_container) > 0:
                    next_page_url = next_page_container[0].find_element(By.TAG_NAME, 'a')
                    next_page_url = next_page_url.get_attribute('href')
                    next_page_number = list(reversed(next_page_url.split("=")))[0]
                    next_page_number = int(next_page_number)+1
        return next_page_url, next_page_number

    articles = paginated_list_scrapper(base_url, first_path,
                                       lambda _driver: _articles_finder(_driver),
                                       lambda _driver: _next_page_finder(_driver),
                                       lambda date: parse_date_locale_en(date)
                                       )

    return articles


def sec_gv_scrapper():
    base_url = "https://www.sec.gov"
    first_path = "/newsroom/press-releases?page=0"

    def _articles_finder(driver):
        articles_list_items = driver.find_elements(By.XPATH, '//tr[@class="pr-list-page-row"]')
        articles_urls = []
        articles_dates = []
        for a in range(len(articles_list_items)):
            url_elm = articles_list_items[a].find_element(By.TAG_NAME, 'a')
            date_elm = articles_list_items[a].find_element(By.TAG_NAME, 'time')
            articles_urls.append(url_elm)
            articles_dates.append(date_elm)
        return articles_urls, articles_dates

    def _next_page_finder(driver):
        next_page_number = 0
        next_page_url = None
        next_page_container = driver.find_elements(By.CSS_SELECTOR, 'nav.usa-pagination')
        if len(next_page_container) > 0:
            next_page_container = next_page_container[0].find_elements(By.CLASS_NAME, "pager__items")
            if len(next_page_container) > 0:
                next_page_container = next_page_container[0].find_elements(By.CLASS_NAME, "usa-pagination__next-page")
                if len(next_page_container) > 0:
                    next_page_url = next_page_container[0].get_attribute('href')
                    next_page_number = list(reversed(next_page_url.split("=")))[0]
                    next_page_number = int(next_page_number) + 1
        return next_page_url, next_page_number

    articles = paginated_list_scrapper(base_url, first_path,
                                       lambda _driver: _articles_finder(_driver),
                                       lambda _driver: _next_page_finder(_driver),
                                       lambda date: parse_date_locale_en_2(date)
                                       )

    return articles


def qc_amf_test_page():
    cService = webdriver.ChromeService(executable_path="C:/Users/AYSIF/Documents/Programmes/chromedriver-win64"
                                                       "/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=cService)
    p = read_page(driver, "https://lautorite.qc.ca/grand-public/salle-de-presse/actualites/fiche-dactualite/lautorite"
                          "-accueille-deux-nouveaux-membres-au-sein-de-son-comite-consultatif-sur-les-produits"
                          "-dinvestissement")
    wkhtml_path = pdfkit.configuration(
        wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
    )  # by using configuration you can add path value.
    p = html_base.replace("@HTML_PDF", p)
    pdfkit.from_string(p, "C:/Users/AYSIF/PycharmProjects/TwikitTest/src/test.pdf", configuration=wkhtml_path)


if __name__ == '__main__':
    _articles = sec_gv_scrapper()
    _organized_articles = g_organize_articles(articles=_articles)
    write_articles_in_json(articles=_organized_articles, outfile_name="sec_gv")
