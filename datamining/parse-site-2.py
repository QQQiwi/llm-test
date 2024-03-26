import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd

MAC_LIST = ["https://i-lite.ru/macbook?pag_page=1",
            "https://i-lite.ru/macbook?pag_page=2",
            "https://i-lite.ru/macbook?pag_page=3",
            "https://i-lite.ru/macbook?pag_page=4",
            "https://i-lite.ru/macbook?pag_page=5"]

DATASET = {}

parts_to_remove = ["""К оплате принимаются платежные карты: VISA Inc, MasterCard WorldWide, НСПК МИР.
                  Для оплаты товара банковской картой при оформлении заказа в интернет-магазине выберите способ оплаты: банковской картой.
                  При оплате заказа банковской картой, обработка платежа происходит на авторизационной странице банка, где Вам необходимо ввести данные Вашей банковской карты:"""]

def get_mac_info(macbook_link):
    r = requests.get(macbook_link)
    soup = BeautifulSoup(r.content, 'html.parser')
    mac_info_tags = soup.find_all("div", class_="post-content")
    mac_info = ""
    for cur_tag in mac_info_tags:
        info_part = cur_tag.find("p")
        if info_part is not None:
            mac_info += info_part.text

    for part in parts_to_remove:
        if part in mac_info:
            mac_info = mac_info.replace(part, "")
    
    return mac_info



def go_through_page(baseurl):
    r = requests.get(baseurl)
    soup = BeautifulSoup(r.content, 'html.parser')

    mac_list = soup.find_all("div", class_="col-xl-4 col-md-6")
    model_list = []
    link_list = []
    info_list = []
    price_list = []

    hi = False
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
