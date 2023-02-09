import json
import time
import requests
import csv
import sys
import random
from lxml import etree
import cloudscraper
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup as bs

headers = ['brand', 'price', 'color', 'Name', 'details']

with open('boots_details.csv', 'w') as b:
    writer = csv.writer(b)
    writer.writerow(headers)

with open("urls.txt") as f:
    urls = f.readlines()

class Boot():
    def __init__(self, config_path, details_url):
        self.session = cloudscraper.CloudScraper.create_scraper()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        x = self.session.get(details_url)
        self.details_url = details_url
        print(x.status_code)
        self.config_file = json.load(open(config_path))
        time.sleep(10)
        
    def products_link(self):
        try:
            page_num = 1
            self.obj_link = []
            for pro_url in urls:
                while True:
                    search_url = f"{pro_url}{page_num}"
                    print(search_url)
                    api_result = self.session.get(url=search_url)
                    api_soup = bs(api_result.content, "lxml")
                    pg = api_soup.find("div", class_="c-list-header__counter")
                    page = int(pg['data-total-pages-count'])
                    page_num += 1
                    url = api_soup.find_all("div", class_="c-listing-items__item")
                    links_value = []
                    for links in url:
                        links_value.append(links.find(
                            "a", class_="c-prod-card__images"))
                    for ob_link in links_value:
                        self.obj_link.append(
                            "https://www.selfridges.com"+ob_link['href'])
                       
                    if page_num > page:
                        page_num=1
                        break
        except requests.exceptions.MissingSchema:
            pass

    def products_detail(self):
        sleep_time = random.randint(3,6)
        for url in self.obj_link:
            prod_page = self.session.get(url)
            soup = bs(prod_page.text, "lxml")
            dom = etree.HTML(str(soup))
            try:
                color = url.split("colour=")[1]
            except IndexError:
                color = "Not Available"
            
            try:
                brand = dom.xpath(self.config_file['brand'])
                brand = " ".join(brand)
            except Exception as e:
                brand ="Not Available"
                print(e)

            try:
                details = dom.xpath(self.config_file['details'])
                details = " ".join(details)
            except Exception as e:
                details = "Not Available"
                print(e)

            try:    
                price = dom.xpath(self.config_file['price'])
                price = " ".join(price)
                price = "£ " + price
            except Exception as e:
                price = "Not Availabel"
                print(e)

            try:    
                name = dom.xpath(self.config_file['name'])
                name = " ".join(name)
            except Exception as e:
                name = "Not Avaialble"
                print(e)
            time.sleep(sleep_time)

            row_ = [brand, price, color, name, details]

            try:
                with open('boots_details.csv', 'a', newline='') as b:
                    writer = csv.writer(b)
                    writer.writerow(row_)
            except UnicodeEncodeError:
                pass

config_name = sys.argv[1]
url = sys.argv[-1]

obj = Boot(config_name, url)
obj.products_link()
obj.products_detail()
