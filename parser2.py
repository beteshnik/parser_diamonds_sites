#!/usr/bin/python
# -*- coding: utf-8 -*-
# pip3 install pandas
# pip3 install pyquery
import csv
from datetime import datetime
import time
import pandas as pd
import bs4
import httplib2
import re
import requests
from httplib2 import HttpLib2Error
    
def main():
    print("###www.celinni.com### is started")
    # initialize variables
    # start from page
    page = 1
    # urls
    main_page = "https://www.celinni.com/fr/recherche-diamants-certifies-GIA-HRD-IGI"
    list_url = "https://www.celinni.com/modules/diamondsearch/fetch_diamonds.php?page="
    paging_url = "https://www.celinni.com/modules/diamondsearch/functions.php"

    with open('filters/filter_cellini.txt', 'r') as filter_file:
        filter_text = filter_file.read()

    # tempo results
    # output_file_raw = 'raw.json'
    diamond_listing_tempo = "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_www.celinni.com' +'_tempo.csv'
    # file with results
    diamond_listing_results = "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_www.celinni.com' + '_diamond_listing.csv' 
    diamond_listing_results_xlsx =  "results/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_www.celinni.com' +'_diamond_listing.xlsx'
    # file headings
    
    csv_headers = ['ID','Shape','Carat','Color','Clarity','Cut','Polish','Symmetry','Fluorescence','Certificate Laboratory','Prix']

    with open(diamond_listing_results, 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=';', quotechar='|')
        writer.writerow(csv_headers)

# get cookie
    cookie = get_cookie(main_page)
# get quantities of pages
    paging_url_response = post_response_content(paging_url,cookie,filter_text)
    pages = get_pages_quantity(paging_url_response)
    print("###www.celinni.com### Pages: "+ str(pages))


    # parse each page
    while (page <= pages):
        print("###www.celinni.com### Page " + str(page) + " from "+ str(pages) + " is in progress...")
            
        next_url = list_url + str(page) 
        # print(next_url)  
        # print(headers)    
        list_data =  post_response_content(next_url,cookie,filter_text)
        add_page_product_data_to_csv(list_data,diamond_listing_tempo,csv_headers)
        add_page_data_to_all_data(diamond_listing_tempo,diamond_listing_results)
        page = page + 1
        # time.sleep(2)
    create_excel(diamond_listing_results,diamond_listing_results_xlsx)
    print("###www.celinni.com### is completed")

# get cookie from request
def get_cookie(url_path):
    connection_error = "no"
    try:
        response = requests.head(url_path)
        status = response.status_code

    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
       connection_error = e
       status = "connection_error"
       print("Lost Internet Connection")
       time.sleep(10)  
           
   
    while status != 200:
        try:
            response = requests.head(url_path)
            status = response.status_code
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10) 

    cookies = response.cookies
    cookie = list(cookies)[0].name + "=" + list(cookies)[0].value + ";" + list(cookies)[1].name + "=" + list(cookies)[1].value
    # print(cookie)
    return cookie


# get data from request
def post_response_content(url_path,cookie,filter_text):
    headers = {'cookie': cookie,'content-type':'application/x-www-form-urlencoded; charset=UTF-8'}
    # print(headers)
    connection_error = "no"
    try:
        h = httplib2.Http()
        response, content = h.request(url_path, method="POST", body=filter_text, headers=headers)
        status = response["status"]
    except (TimeoutError, OSError, HttpLib2Error) as e:
       connection_error = e
       status = "connection_error"
       print("Lost Internet Connection")
       time.sleep(10)  
    while status != "200":
        try:
            h = httplib2.Http()
            response, content = h.request(url_path, method="POST", body=filter_text, headers=headers)
            status = response["status"]
        except (TimeoutError, OSError, HttpLib2Error) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10) 

    # print(response)
    content_data = content.decode('utf-8') #, errors="ignore")
    # with open('raw.xml', 'w', encoding='utf-8') as data_to_file_raw:
    #     data_to_file_raw.write(str(content_data))
    return content_data

# get pages quantity
def get_pages_quantity(paging_url):
    paging_string =  re.sub(r'[^0-9]+', r'', str(paging_url))
    print("Items: "+ paging_string)
    return int(paging_string) // 300 + 1

# remove not wanted duplications, remove garbage, set encoding
def add_page_data_to_all_data(tempo_csv,all_csv):
    df_tempo = pd.read_csv(tempo_csv, sep=';', encoding='utf-8')
    df_tempo.dropna(subset=['Prix'], inplace=True)

    df_all = pd.read_csv(all_csv, sep=';', encoding='utf-8')
    df_all_with_tempo = pd.concat([df_all,df_tempo])  
    df_all_with_tempo.drop_duplicates(subset=None, inplace=True)
    df_all_with_tempo.to_csv(all_csv, sep=';',index=False, encoding='utf-8')

#create beautiful excel file
def create_excel(diamond_listing_results,diamond_listing_results_xlsx):
    df_tempo = pd.read_csv(diamond_listing_results, sep=';', encoding='utf-8')
    df_tempo.to_excel(diamond_listing_results_xlsx, index=False)

#dictionaries
def getShapeFromDictionary(shape):
    sDict = {"Rond":"ROUND","Princesse":"PRINCESS","Émeraude":"EMERALD","":"NO DATA","Asscher":"Asscher",
    "Coussin":"Cushion","Marquise":"Marquise","Radiant":"Radiant","Ovale":"Oval","Poire":"Pear","Coeur":"Heart"}
    return sDict.get(shape,"OTHER")

def getCutFromDictionary(cut):
    cutDict = {"n/c":"no data","s-Idéal":"EXCELLENT","Bonne":"GOOD","s-Très bonne":"VERY GOOD"}
    return cutDict.get(cut,"OTHER")

def getFluoFromDictionary(fluo):
    fDict = {"Non":"None","Med":"Medium","Fnt":"Slight","Stg":"Strong","Vst":"Very Strong"}
    return fDict.get(fluo,"OTHER")

#parse product list to csv file
def add_page_product_data_to_csv(list_data,output_file_csv,csv_headers):
    parser = bs4.BeautifulSoup(list_data, 'lxml')
    data_items = parser.select('div.diamonds-list-item')
    # print(data_items)
    length_data = len(data_items)
    # print(data_items[length_data-1])
    with open(output_file_csv, 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=';', quotechar='|')
        writer.writerow(csv_headers)

        for data_item in data_items:
            id = "NO DATA"
            shape = "NO DATA"
            carat = "NO DATA"
            color = "NO DATA"
            clarity = "NO DATA"
            cut = "NO DATA"
            polish = "NO DATA"
            symmetry = "NO DATA"
            fluorescence = "NO DATA"
            certificat = "NO DATA"
            prix = "NO DATA"

            id = data_item.select('input')[0].get('value')
            data_item_parameters = data_item.select('div')
            shape =  getShapeFromDictionary(data_item_parameters[1].text).upper()
            carat = data_item_parameters[2].text.replace(".",",")
            # prix_ht = data_item_parameters[12].text
            prix = data_item_parameters[13].text
            prix = re.sub('[^0-9]','', prix) + ",00"
            # prix_per_carat = data_item_parameters[11].text
            cut = getCutFromDictionary(data_item_parameters[3].text).upper()
            color = data_item_parameters[4].text.upper()
            clarity = data_item_parameters[5].text.upper()
            fluorescence = getFluoFromDictionary(data_item_parameters[6].text).upper()
            polish = data_item_parameters[7].text.upper()
            symmetry = data_item_parameters[8].text.upper()
            certificat = data_item_parameters[9].text
            writer.writerow([id,shape,carat,color,clarity,cut,polish,symmetry,fluorescence,certificat,prix])

if __name__ == "__main__":
    main()