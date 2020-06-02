#!/usr/bin/python
# -*- coding: utf-8 -*-
# pip3 install lxml
# pip3 install requests
# pip3 install pandas
import json
import requests
import csv
import datetime
import time
import pandas as pd
import urllib.parse
import httplib2
import re
from httplib2 import HttpLib2Error
    
def main():
    print("###www.bluenile.com### is started")
    # initialize variables
    # start with filter
    filterNumber = 1
    list_url= ""
    with open('filters/site_url_bluenile.txt', 'r') as url_file:
        list_url = url_file.read()
    
        # tempo results
    # output_file_raw = 'raw.json'
    diamond_listing_tempo = "tempo/" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_www.bluenile.com' + '_tempo.csv'
    # file with results
    diamond_listing_results = "tempo/" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_www.bluenile.com' + '_diamond_listing.csv'
    diamond_listing_results_xlsx =  "results/" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_www.bluenile.com' +'_diamond_listing.xlsx'
    # file headings
    csv_headers = ['ID','Shape','Carat','Color','Clarity','Cut','Polish','Symmetry','Fluorescence','Certificate Laboratory','Prix']
    filter_data = "tempo/" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_www.bluenile.com' + '_filter.txt'

    shapes = ['RD','PR','EC','AS','CU','MQ','RA','OV','PS','HS']
    cuts = ['Good','Very%20Good','Ideal','Astor%20Ideal']
    colors = ['K','J','I','H','G','F','E','D']
    clarities = ['SI2','SI1','VS2','VS1','VVS2','VVS1','IF','FL']
    prices = ['price_diapason1','price_diapason2','price_diapason3','price_diapason4']

    filter_links_list = create_filter_links(list_url,shapes,cuts,colors,clarities,prices)
    with open(filter_data, 'w') as filter_data:
        filter_data.writelines(filter_links_list)

    with open(diamond_listing_results, 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=';', quotechar='|')
        writer.writerow(csv_headers)

    print("###www.bluenile.com### All filters quantity: " + str(len(filter_links_list)))
    

    for filter_link in filter_links_list[filterNumber-1:]:
        print("###www.bluenile.com### Filter N: " + str(filterNumber) + " from " + str(len(filter_links_list)) + " is in progress...")
        # print(filter_link)
        # get quantities of pages
        first_page_json = get_response_json(filter_link)
        pages = get_pages_quantity(first_page_json)
        if(pages > 10):
           print("###"+ filter_link + "###")
        # print("###www.bluenile.com### All pages quantity: " + str(pages))

        startIndex = 0
        page = 1
        # parse each page
        while (page <= pages):
            # print("###www.bluenile.com### Page " + str(page) + " from " + str(pages) + " is in progress...")
            next_url = filter_link.replace("startIndex=0","startIndex=" + str(startIndex))
            # print(next_url)         
            list_json = get_response_json(next_url)
            add_page_product_data_to_csv(list_json,diamond_listing_tempo,csv_headers)
            add_page_data_to_all_data(diamond_listing_tempo,diamond_listing_results)

            startIndex = startIndex + 500
            page = page + 1
        filterNumber = filterNumber + 1

    create_excel(diamond_listing_results,diamond_listing_results_xlsx)
    print("###www.bluenile.com### is completed")

# get data from API, parse to JSON
def get_response_json(url_path):
    connection_error = "no"
    try:
        h = httplib2.Http()
        response, content = h.request(url_path)
        status = response["status"]
    except (TimeoutError, OSError,HttpLib2Error) as e:
       connection_error = e
       status = "connection_error"
       print("Lost Internet Connection")
       time.sleep(10)  
    while status != "200":
        try:
            h = httplib2.Http()
            response, content = h.request(url_path)
            status = response["status"]
        except (TimeoutError, OSError,HttpLib2Error) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10) 

    data_json = json.loads(content.decode('utf-8'))
    # with open(output_file_raw, 'w', encoding='utf-8') as data_to_file_raw:
    #     data_to_file_raw.write(str(data_json))
    return data_json

# get pages quantity
def get_pages_quantity(main_url_json):
    recordsFiltered = int(main_url_json['countRaw'])
    if(recordsFiltered > 1200):
        print("###MORE THAN 1200 ITEMS FILTERED. FILTERS SHOULD BE SPECIFIED. OVERVISE DATA WILL NOT BE PARSED COMPLETLY###")
    return recordsFiltered // 500 + 1

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

# create links for different filter states
def create_filter_links(list_url,shapes,cuts,colors,clarities,prices):
    links_list = []

    # print(first_page)
    for shape in shapes:
        for cut in cuts:
            for color in colors:
                for clarity in clarities:
                    for price in prices:
                        first_page = list_url.replace("startIndex=","startIndex=" + "0")
                        if (price == 'price_diapason1'):
                            first_page = first_page.replace("minPrice=","minPrice=" + "0.00")
                            first_page = first_page.replace("maxPrice=","maxPrice=" + "800.00")                           
                        if (price == 'price_diapason2'):
                            first_page = first_page.replace("minPrice=","minPrice=" + "800.01")
                            first_page = first_page.replace("maxPrice=","maxPrice=" +  "1100.00")
                        if (price == 'price_diapason3'):
                            first_page = first_page.replace("minPrice=","minPrice=" + "1100.01")
                            first_page = first_page.replace("maxPrice=","maxPrice=" +  "2000.00")   
                        if (price == 'price_diapason4'):
                            first_page = first_page.replace("minPrice=","minPrice=" + "2000.01")
                            first_page = first_page.replace("maxPrice=","maxPrice=" +  "50000000.00")   
                        first_page = first_page.replace("minClarity=","minClarity=" + clarity)
                        first_page = first_page.replace("maxClarity=","maxClarity=" + clarity)
                        first_page = first_page.replace("minColor=","minColor=" + color)
                        first_page = first_page.replace("maxColor=","maxColor=" + color)
                        first_page = first_page.replace("minCut=","minCut=" + cut)
                        first_page = first_page.replace("maxCut=","maxCut=" + cut)
                        first_page = first_page.replace("shape=","shape=" + shape)
                        links_list.append(first_page) #+";")
    return links_list

def getCutFromDictionary(cut):
    cutDict = {"Astor Ideal":"EXCELLENT","Ideal":"EXCELLENT","Good":"GOOD","Very Good":"VERY GOOD"}
    return cutDict.get(cut,"OTHER")

def getFluoFromDictionary(fluo):
    fluo = re.sub(' Blue| White| Yellow','', fluo)
    fDict = {"None":"None","Medium":"Medium","Faint":"Slight","Strong":"Strong","Very Strong":"Very Strong"}
    return fDict.get(fluo,"OTHER")

#parse product list to csv file
def add_page_product_data_to_csv(data_json,output_file_csv,csv_headers):
    data_items = data_json['results']
    length_data = len(data_items)

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
            id = str(data_item['id']).strip().replace('\n',' ')
            carat = str(data_item['carat'][0]).strip().replace('\n',' ').replace(".",",")
            clarity = str(data_item['clarity'][0]).strip().replace('\n',' ').upper()
            cut = getCutFromDictionary(str(data_item['cut'][0]['label']).strip().replace('\n',' '))
            prix = str(data_item['price'][0]).strip().replace('\n',' ')
            prix = prix.replace(',','')
            prix = prix.replace('.',',')
            prix = re.sub('[^0-9,]','', prix)
            certificat = "GIA"
            fluorescence = getFluoFromDictionary(str(data_item['fluorescence'][0]).strip().replace('\n',' ')).upper()
            polish = str(data_item['polish'][0]).strip().replace('\n',' ').upper()
            shape = str(data_item['shapeName'][0]).strip().replace('\n',' ').upper()
            symmetry  = str(data_item['symmetry'][0]).strip().replace('\n',' ').upper()
            color  = str(data_item['color'][0]).strip().replace('\n',' ').upper()
            writer.writerow([id,shape,carat,color,clarity,cut,polish,symmetry,fluorescence,certificat,prix])

if __name__ == "__main__":
    main()