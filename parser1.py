#!/usr/bin/python
# -*- coding: utf-8 -*-

# pip3 install lxml
# pip3 install bs4
# pip3 install httplib2
# pip3 install pandas
# pip3 install openpyxl
import json
import csv
import bs4
import time
from datetime import datetime
import pandas as pd
import lxml
from httplib2 import HttpLib2Error
import httplib2
import re
    
def main():

    print("###www.i-diamants.com### is started")
    # initialize variables
    list_url = 'https://www.i-diamants.com/en/ajax_listing_diamants.html?ajax=1&all=2&search_forme=01&search_prix_min=600&search_prix_max=153800&search_poids_min=0.21&search_poids_max=5.77&count='
    diamond_listing_tempo = "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + "_www.i-diamants.com_" + '_tempo.csv'
    # file with results
    diamond_listing_results =  "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + "_www.i-diamants.com_" +'_diamond_listing.csv'
    diamond_listing_results_xlsx =  "results/" + datetime.now().strftime('%Y%m%d%H%M%S') + "_www.i-diamants.com_" +'_diamond_listing.xlsx'
    # result file headings
    csv_headers = ['ID','Shape','Carat','Color','Clarity','Cut','Polish','Symmetry','Fluorescence','Certificate Laboratory','Prix']

    with open(diamond_listing_results, 'w', encoding='utf-8', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=';')
        writer.writerow(csv_headers)
    
    # get quantities of pages
    main_url_text = get_response_text(list_url)
    pages = get_pages_quantity(main_url_text) 
    print("###www.i-diamants.com### All pages quantity: " + pages)

    page_indicator = 0
    # parse each page
    while (page_indicator < 15*int(pages)):
        next_url = list_url + str(page_indicator)
        list_text = get_response_text(next_url)
        add_product_data_to_csv(list_text,diamond_listing_tempo,csv_headers)
        add_page_data_to_all_data(diamond_listing_tempo,diamond_listing_results)
        page_indicator = page_indicator + 15
        print("###www.i-diamants.com### Next page is in progress...")
        # time.sleep(3)
    create_excel(diamond_listing_results,diamond_listing_results_xlsx)
    print("###www.i-diamants.com### is completed")

# get data from HTML
def get_response_text(url_path):
    connection_error = "no"
    try:
        h = httplib2.Http()
        response, content = h.request(url_path)
        status = response["status"]
    except (TimeoutError, HttpLib2Error) as e:
       connection_error = e
       status = "connection_error"
       print("Lost Internet Connection")
       time.sleep(10)  
    while status != "200":
        try:
            h = httplib2.Http()
            response, content = h.request(url_path)
            status = response["status"]
        except (TimeoutError, HttpLib2Error) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10) 
    data_text = content.decode('utf-8')
    return data_text

# get pages quantity
def get_pages_quantity(data_text):
    parser1 = bs4.BeautifulSoup(data_text, 'lxml')
    script_text = str(parser1.select('script')[0])

    start_index = script_text.find("html") + 6
    end_index = script_text.find("');")
    text_to_parse = script_text[start_index:end_index]

    parser1 = bs4.BeautifulSoup(text_to_parse, 'lxml')
    last_page = parser1.select('li[data-counter]:last-of-type')[0]

    return last_page.get('data-counter')

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

#cut dictionary
def getCutFromDictionary(cut):
    cutDict = {"EX":"EXCELLENT","VG":"VERY GOOD","G":"GOOD","":"NO DATA"}
    return cutDict.get(cut)

#parse product list to csv file
def add_product_data_to_csv(data_text,output_file_csv,csv_headers):
    parser2 = bs4.BeautifulSoup(data_text, 'lxml')
    products = parser2.select('div.results div.line')

    with open(output_file_csv, 'w', newline='', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=';')
        writer.writerow(csv_headers)
            
        for i in range(len(products)):
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

            shape = str(products[i].select('p.forme img')[0].get('title')).split(" ")[0].upper()
            id = str(products[i].select('p.ref')[0].text).strip()
            carat = str(products[i].select('p.carat')[0].text).replace(".",",")
            color = str(products[i].select('p.couleur')[0].text).upper()
            clarity = str(products[i].select('p.purete')[0].text).upper()
            cut = str(products[i].select('p.taille')[0].text).upper()
            cut = getCutFromDictionary(cut)
            certificat = str(products[i].select('p.certificat')[0].text).upper()
            prix = str(products[i].select('p.prixttc')[0].text)
            if prix != "Contact us":
                prix = re.sub('[^0-9]','', prix) + ",00"
            else:
            	prix = ""
            details_link = str(products[i].select('a.details')[0].get('href'))
            detailsPage = get_response_text(details_link)
            parser3 = bs4.BeautifulSoup(detailsPage, 'lxml')
            fluorescence = str(parser3.select('#inffluo + p')[0].text).upper()
            writer.writerow([id,shape,carat,color,clarity,cut,polish,symmetry,fluorescence,certificat,prix])



if __name__ == "__main__":
    main()