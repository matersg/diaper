import datetime
import re
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import chromedriver_binary

def setup_chrome():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1500x900')
    return webdriver.Chrome(options=options)

def parse_product_container(html_doc):
    if 'SOLD OUT' in html_doc:
        availability = 'SOLD OUT'
    else:
        availability = 'IN STOCK'
    soup = BeautifulSoup(html_doc, 'html.parser')
    name = soup.find('h4', 'RedmartProductCard-title').get_text()
    href = soup.find('a', 'RedmartProductCard-link')['href']
    units = soup.find('div', 'RedmartProductCard-weight').get_text()
    price = soup.find('div', 'RedmartProductCard-price sg').get_text().strip('$')
    return name, f'https:{href}', availability, units, price

if __name__=='__main__':
    wd = setup_chrome()
    redmart_urls = pd.read_csv('redmart_urls.csv')
    diaper_list = []
    for r in redmart_urls.itertuples():
        wd.get(r.products_url)
        print(f'redmart: Scraping {r.brand} {r.size}')
        date_crawled = datetime.datetime.today()
        containers = wd.find_elements_by_xpath('//div[@class="RedmartProductCard-container"]')
        for container in containers:
            inner_html = container.get_attribute('innerHTML')
            result = parse_product_container(inner_html)
            diaper_list.append((*result, r.brand, r.size, r.type, date_crawled))
        wd.close()
    wd.quit()

    fname = 'redmart.csv'
    pd.DataFrame(
        diaper_list,
        columns=['name','url','availability','units','price','brand','size','type', 'date_crawled']
    ).to_csv(
        fname,
        index=False,
    )
    print(f'Saved {fname}')
