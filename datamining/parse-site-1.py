import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd

BASEURL = "https://saratov.istudio-shop.ru"
MAC_LIST = ["https://saratov.istudio-shop.ru/catalog/Macbook/",
            "https://saratov.istudio-shop.ru/catalog/Macbook/?curPos=20",
            "https://saratov.istudio-shop.ru/catalog/Macbook/?curPos=40"]

DATASET = {}

parts_to_remove = ["федеральная сеть",
                   "Социальные сети"]

def get_mac_info(macbook_link):
    r = requests.get(macbook_link)
    soup = BeautifulSoup(r.content, 'html.parser')
    mac_info_tags = soup.find_all("p")
    mac_info = ""
    for tag in mac_info_tags:
        if tag.find() is None:
            mac_info += tag.text

    for part in parts_to_remove:
        if part in mac_info:
            mac_info = mac_info.replace(part, "")
    
    return mac_info


def go_through_page(baseurl):
    r = requests.get(baseurl)
    soup = BeautifulSoup(r.content, 'html.parser')

    mac_list = soup.find_all("div", class_="blk_name")
    price_list = soup.find_all("div", class_="blk_price normal_price")
    price_list = [re.sub(r'\s+', '', price.contents[0].text)
                  for price in price_list]
    model_list = []
    link_list = []
    info_list = []

    for mac in mac_list:
        model_list.append(mac.contents[1].contents[0].text)
        cur_mac_link = BASEURL + mac.contents[1].get('href')
        link_list.append(cur_mac_link)
        info_list.append(get_mac_info(cur_mac_link))

    return model_list, link_list, price_list, info_list


def main():
    model_list, link_list, price_list, info_list = [], [], [], []
    for url in MAC_LIST:
        page_model_list, page_link_list, page_price_list, page_info_list = go_through_page(url)
        model_list += page_model_list
        link_list += page_link_list
        price_list += page_price_list
        info_list += page_info_list
    
    DATASET["Model"] = model_list
    DATASET["Link"] = link_list
    DATASET["Price"] = price_list
    DATASET["Info"] = info_list
    pd.DataFrame(DATASET).to_csv("istudio-shop.csv")


if __name__ == "__main__":
    main()
