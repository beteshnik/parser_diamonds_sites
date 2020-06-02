#!/usr/bin/python
# -*- coding: utf-8 -*-
# pip3 install lxml
# pip3 install requests
# pip3 install pandas
# pip3 install bs4
import json
import requests
import csv
from datetime import datetime
import time
import bs4
import pandas as pd
from httplib2 import HttpLib2Error
import re
    
def main():
    print("###www.diamant-gems.com### is started")
    # initialize variables
    list_url= ""
    with open('filters/diamant-gems_site_url.txt', 'r') as url_file:
        list_url = url_file.read()
    
    # tempo results
    # output_file_raw = 'raw.json'
    diamond_listing_tempo = "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_diamant-gems' +'_tempo.csv'
    # file with results
    diamond_listing_results = "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_diamant-gems' + '_diamond_listing.csv' 
    diamond_listing_results_xlsx =  "results/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_diamant-gems' +'_diamond_listing.xlsx'
    # file headings
    
    csv_headers = ['ID','Shape','Carat','Color','Clarity','Cut','Polish','Symmetry','Fluorescence','Certificate Laboratory','Prix']

    with open(diamond_listing_results, 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=';', quotechar='|')
        writer.writerow(csv_headers)

    # get quantities of pages
    main_url_json = get_response_json(list_url)
    pages = get_pages_quantity(main_url_json) 
    print("###www.diamant-gems.com### All pages quantity: " + str(pages))

    start = 0
    page = 1
    # parse each page
    while (page <= pages):
        print("###www.diamant-gems.com### Page " + str(page) + " from "+ str(pages) + " is in progress...")
        next_url = list_url.replace("draw=","draw=" + str(page))
        next_url = next_url.replace("start=","start=" + str(start))
        list_json = get_response_json(next_url)
        add_page_product_data_to_csv(list_json,diamond_listing_tempo,csv_headers)
        start = start + 50
        page = page + 1
        add_page_data_to_all_data(diamond_listing_tempo,diamond_listing_results)
    
    create_excel(diamond_listing_results,diamond_listing_results_xlsx)
    print("###www.diamant-gems.com### is completed")

# get data from API, parse to JSON
def get_response_json(url_path):
    connection_error = "no"
    try:
        response = requests.get(url_path)
        status = response.status_code
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
       connection_error = e
       status = "connection_error"
       print("Lost Internet Connection")
       time.sleep(10)  
           
    while status != 200:
        try:
            response = requests.get(url_path)
            status = response.status_code
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10) 

    data_json = response.json()
    return data_json

# get pages quantity
def get_pages_quantity(main_url_json):
    recordsFiltered = int(main_url_json['recordsFiltered'])

    return recordsFiltered // 50 + 1

# get data from HTML
def get_response_text(url_path):
    connection_error = "no"
    try:
        response = requests.get(url_path)
        status = response.status_code
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
       connection_error = e
       status = "connection_error"
       print("Lost Internet Connection")
       time.sleep(10)  
           
    while status != 200:
        try:
            response = requests.get(url_path)
            status = response.status_code
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10)

    response.encoding = 'utf-8'
    data_text = response.text
    return data_text

# get form by img
def get_item_form(forme_img):
    forme = 'Other'
    if 'Round' in  forme_img:
        forme = 'Round'
    if 'Princess' in  forme_img:
        forme = 'Princess'
    if 'Cushion' in  forme_img:
        forme = 'Cushion'
    if 'Emerald' in  forme_img:
        forme = 'Emerald'
    if 'Oval' in  forme_img:
        forme = 'Oval'
    if 'Radiant' in  forme_img:
        forme = 'Radiant'
    if 'Marquise' in  forme_img:
        forme = 'Marquise'
    if 'Heart' in  forme_img:
        forme = 'Heart'
    if 'Pear' in  forme_img:
        forme = 'Pear'
    if 'Assher' in  forme_img:
        forme = 'Asscher'
    if 'Baguette' in  forme_img:
        forme = 'Baguette'
    if 'Fancy' in  forme_img:
        forme = 'Fancy'
    if 'Half Moon' in  forme_img:
        forme = 'Half Moon'
    if 'Hexagon' in  forme_img:
        forme = 'Hexagon'
    if 'Kite' in  forme_img:
        forme = 'Kite'
    if 'Octagon' in  forme_img:
        forme = 'Octagon'
    if 'Old European' in  forme_img:
        forme = 'Old European'
    if 'Pentagon' in  forme_img:
        forme = 'Pentagon'
    if 'Rose' in  forme_img:
        forme = 'Rose'
    if 'Shield' in  forme_img:
        forme = 'Shield'
    if 'Square' in  forme_img:
        forme = 'Square'
    if 'Trapeze' in  forme_img:
        forme = 'Trapeze'
    if 'Triangle' in  forme_img:
        forme = 'Triangle'
    if 'Trilliant' in  forme_img:
        forme = 'Trilliant'
    return forme

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

#parse product list to csv file
def add_page_product_data_to_csv(data_json,output_file_csv,csv_headers):
    data_items = data_json['data']
    length_data = len(data_items)

    with open(output_file_csv, 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=';', quotechar='|')
        writer.writerow(csv_headers)

        for i in range(0, length_data):

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

            id = str(data_items[i][0]).strip().replace('\n',' ')
            carat = str(data_items[i][2]).strip().replace('\n',' ')
            carat = carat.replace(" Cts","")
            carat = carat.replace(".",",")
            certificat_html = bs4.BeautifulSoup(data_items[i][3], 'lxml')
            if certificat_html.a is None:
                certificat = "NO DATA"
            else:
                certificat = str(certificat_html.a.text).strip().replace('\n',' ')
            color = str(data_items[i][4]).strip().replace('\n',' ').upper()
            clarity = str(data_items[i][5]).strip().replace('\n',' ').upper()
            cut = str(data_items[i][7]).strip().replace('\n',' ')
            if cut == "":
                cut = "NO DATA"
            else:
                cut = cut.replace('Ideal','Excellent').upper()
            polish = str(data_items[i][8]).strip().replace('\n',' ')
            if polish == "":
                polish = "NO DATA"
            else:
                polish = polish.replace('Ideal','Excellent').upper()
            symmetry = str(data_items[i][9]).strip().replace('\n',' ')
            if symmetry == "":
                symmetry = "NO DATA"
            else:
                symmetry = symmetry.replace('Ideal','Excellent').upper()
            prix_html = bs4.BeautifulSoup(data_items[i][11], 'lxml')
            prix = str(prix_html.select('b')[0].text).strip().replace('\n',' ')
            prix = re.sub('[^0-9,]','', prix)
            fluorescence = str(data_items[i][10]).strip().replace('\n',' ')
            if fluorescence == "":
                fluorescence = "NO DATA"
            else:
                fluorescence = fluorescence.replace('Faint','Slight').upper()
            details_link_html = bs4.BeautifulSoup(data_items[i][13], 'lxml')
            details_link = str(details_link_html.select('a')[0].get('href')).strip().replace('\n',' ')
            shape = get_item_form(details_link).upper()
            writer.writerow([id,shape,carat,color,clarity,cut,polish,symmetry,fluorescence,certificat,prix])

if __name__ == "__main__":
    main()