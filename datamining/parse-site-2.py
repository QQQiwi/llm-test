import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd

# links which contain MacBooks information
MAC_LIST = ["https://i-lite.ru/macbook?pag_page=1",
            "https://i-lite.ru/macbook?pag_page=2",
            "https://i-lite.ru/macbook?pag_page=3",
            "https://i-lite.ru/macbook?pag_page=4",
            "https://i-lite.ru/macbook?pag_page=5"]

# dictionary which will convert to dataset in csv
DATASET = {}

# unnecessary repeating part of the content of some website blocks
PARTS_TO_REMOVE = ["""К оплате принимаются платежные карты: VISA Inc, MasterCard WorldWide, НСПК МИР.
                  Для оплаты товара банковской картой при оформлении заказа в интернет-магазине выберите способ оплаты: банковской картой.
                  При оплате заказа банковской картой, обработка платежа происходит на авторизационной странице банка, где Вам необходимо ввести данные Вашей банковской карты:"""]


def get_mac_info(macbook_link):
    """
        Args:
            macbook_link (str): full link to MacBook

        Returns:
            mac_info (str): text about product parsed from MacBook link
    """
    r = requests.get(macbook_link)
    soup = BeautifulSoup(r.content, 'html.parser')
    mac_info_tags = soup.find_all("div", class_="post-content")
    mac_info = ""
    for cur_tag in mac_info_tags:
        info_part = cur_tag.find("p")
        if info_part is not None:
            mac_info += info_part.text

    for part in PARTS_TO_REMOVE:
        if part in mac_info:
            mac_info = mac_info.replace(part, "")
    
    return mac_info


def go_through_page(baseurl):
    """
        Args:
            baseurl (str): link to the site from which MacBooks info will be
                           parsed
        
        Returns:
            model_list (list): list with MacBook model names
            link_list (list): list with links to MacBooks
            price_list (list): list with prices of MacBooks
            info_list (list): list with info about MacBooks

            All of these lists are corresponding to each other.
    """
    r = requests.get(baseurl)
    soup = BeautifulSoup(r.content, 'html.parser')

    mac_list = soup.find_all("div", class_="col-xl-4 col-md-6")
    model_list = []
    link_list = []
    info_list = []
    price_list = []

    for mac in mac_list:
        model_list.append(mac.contents[1].contents[3].contents[1].text)
        
        cur_mac_link = mac.contents[1].contents[3].contents[-2].get("href")
        link_list.append(cur_mac_link)

        price = re.sub(r'\s+', '', mac.contents[1].contents[3].contents[3].text)
        price = price.split("₽")[0]
        price_list.append(price)

        info_list.append(get_mac_info(cur_mac_link))

    return model_list, link_list, price_list, info_list


def main():
    """
        This script is parsing information about MacBooks from site
        i-lite.ru

        This information will be saved as csv file and will be use as training
        data for LLM.
    """
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
    pd.DataFrame(DATASET).to_csv("i-lite.csv")


if __name__ == "__main__":
    main()
