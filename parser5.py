#!/usr/bin/python
# -*- coding: utf-8 -*-
# pip3 install lxml
# pip3 install pandas
# pip3 install bs4
import csv
from datetime import datetime
import time
import pandas as pd
import httplib2
import bs4
import sys
import requests
from httplib2 import HttpLib2Error
import re
    
def main():
    print("###www.diamants-infos.com### is started")
    # initialize variables
    # start with filter
    filterNumber = 1
    main_page = ""
    site_url= ""

    with open('filters/diamants-infos_settings.csv', 'r', encoding='utf-8',newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=';', quotechar='|')
        parameters = list(reader)[1]
        # filter_path = parameters[0]
        # filterNumber = int(parameters[1])
        site_url = parameters[0]
        main_page = parameters[1]
    
    # tempo results
    # output_file_raw = 'raw.json'
    diamond_listing_tempo = "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_diamants-infos' +'_tempo.csv'
    # file with results
    diamond_listing_results = "tempo/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_diamants-infos' + '_diamond_listing.csv' 
    diamond_listing_results_xlsx =  "results/" + datetime.now().strftime('%Y%m%d%H%M%S') + '_diamants-infos' +'_diamond_listing.xlsx'
    # file headings
    
    csv_headers = ['ID','Shape','Carat','Color','Clarity','Cut','Polish','Symmetry','Fluorescence','Certificate Laboratory','Prix']

    filter_data = 'tempo/'+ datetime.now().strftime('%Y%m%d%H%M%S') + '_diamants-infos_filter.txt'
    filters_to_precise = 'tempo/'+ datetime.now().strftime('%Y%m%d%H%M%S') + '_diamants-infos_filter_to_precise.txt'

    tailles = ['B','PR','O','H','R','C','E','P','M','AS','T']
    prices = ['price_diapason1','price_diapason2','price_diapason3','price_diapason4','price_diapason5','price_diapason6','price_diapason7','price_diapason8','price_diapason9','price_diapason10','price_diapason11','price_diapason12','price_diapason13','price_diapason14','price_diapason15','price_diapason16','price_diapason17','price_diapason18','price_diapason19','price_diapason20','price_diapason21','price_diapason22']
    poids = ['poids_diapason1','poids_diapason2','poids_diapason3','poids_diapason4','poids_diapason5','poids_diapason6','poids_diapason7','poids_diapason8','poids_diapason9','poids_diapason10','poids_diapason11','poids_diapason12','poids_diapason13','poids_diapason14','poids_diapason15','poids_diapason16','poids_diapason17','poids_diapason18','poids_diapason19','poids_diapason20','poids_diapason21']
    colors = ['N','M','L','K','J','I','H','G','F','E','D']
    puretes = ['X','WSI2','WSI1','VS2','VS1','KVVS2','KVVS1','IF','FL']
    
    filter_links_list = create_filter_links(site_url,tailles,prices,poids,colors,puretes)
    with open(filter_data, 'w') as filter_data:
        filter_data.writelines(filter_links_list)


    # add header to file with results
    with open(diamond_listing_results, 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=';', quotechar='|')
        writer.writerow(csv_headers)

    print("All filters quantity: " + str(len(filter_links_list)))
    
    # get cookie
    cookie = get_cookie(main_page)
    
    # get data, add to file, save filter to file if more than 50 items found
    with open(filters_to_precise, 'w', encoding='utf-8',newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=';', quotechar='|')    
        for filter_link in filter_links_list[filterNumber-1:]:
            print("###www.diamants-infos.com### Filter N: " + str(filterNumber) + " from " + str(len(filter_links_list)) + " is in progress...")
            # print(filter_link)       
            list_data = get_response_data(filter_link,cookie)
            items_by_filter = add_page_product_data_to_csv(list_data,diamond_listing_tempo,csv_headers,diamond_listing_results)
            
            if items_by_filter>50:
                filter_link = filter_link.replace("tri=prix_1","tri=prix_2")
                list_data = get_response_data(filter_link,cookie)
                items_by_filter = add_page_product_data_to_csv(list_data,diamond_listing_tempo,csv_headers,diamond_listing_results)
                if items_by_filter>100:
                    writer.writerow([str(items_by_filter)+": ",filter_link])
            
            filterNumber = filterNumber + 1
    
    create_excel(diamond_listing_results,diamond_listing_results_xlsx)
    print("###www.diamants-infos.com### is completed")

# create links for different filter states
def create_filter_links(list_url,tailles,prices,poids,colors,puretes):
    links_list = []

    for taille in tailles[0]:
        for poid in poids:
            for color in colors:
                for purete in puretes:
                    for price in prices:
                        # for qualite_taille in qualite_tailles:
                        first_page = list_url
                            #price
                        if (price == 'price_diapason1'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "600")                           
                        if (price == 'price_diapason2'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "601")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "950")   
                        if (price == 'price_diapason3'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "951")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "999")  
                        if (price == 'price_diapason4'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1000")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1100") 
                        if (price == 'price_diapason5'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1101")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1199")  
                        if (price == 'price_diapason6'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1200")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1300") 
                        if (price == 'price_diapason7'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1301")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1450")  
                        if (price == 'price_diapason8'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1451")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1550")  
                        if (price == 'price_diapason9'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1551")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1650")  
                        if (price == 'price_diapason10'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1651")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1750")  
                        if (price == 'price_diapason11'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1751")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1864")  
                        if (price == 'price_diapason12'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1865")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1999")  
                        if (price == 'price_diapason13'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "2000")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "2500")  
                        if (price == 'price_diapason14'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "2501")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "3200")  
                        if (price == 'price_diapason15'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "3201")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "3999") 
                        if (price == 'price_diapason16'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "4000")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "5000")  
                        if (price == 'price_diapason17'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "5001")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "6500") 
                        if (price == 'price_diapason18'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "6501")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "7000") 
                        if (price == 'price_diapason19'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "7001")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "9000") 
                        if (price == 'price_diapason20'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "9001")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "15000") 
                        if (price == 'price_diapason21'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "15001")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "19000") 
                        if (price == 'price_diapason22'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "19001")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "190000000")                             
                            #poids
                        if (poid == 'poids_diapason1'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.01")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.29")   
                        if (poid == 'poids_diapason2'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.30")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.39")                           
                        if (poid == 'poids_diapason3'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.40")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.40")    
                        if (poid == 'poids_diapason4'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.41")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.45")  
                        if (poid == 'poids_diapason5'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.46")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.49") 
                        if (poid == 'poids_diapason6'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.50")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.50") 
                        if (poid == 'poids_diapason7'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.51")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.52")  
                        if (poid == 'poids_diapason8'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.53")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.59") 
                        if (poid == 'poids_diapason9'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.60")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.60") 
                        if (poid == 'poids_diapason10'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.61")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.69") 
                        if (poid == 'poids_diapason11'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.70")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.70") 
                        if (poid == 'poids_diapason12'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.71")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.80")   
                        if (poid == 'poids_diapason13'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.81")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.99")  
                        if (poid == 'poids_diapason14'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "1.00")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "1.00")  
                        if (poid == 'poids_diapason15'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "1.01")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "1.09")  
                        if (poid == 'poids_diapason16'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "1.10")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "1.50") 
                        if (poid == 'poids_diapason17'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "1.51")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "1.70") 
                        if (poid == 'poids_diapason18'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "1.71")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "1.99")  
                        if (poid == 'poids_diapason19'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "2.00")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "2.49")  
                        if (poid == 'poids_diapason20'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "2.50")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "3.49")  
                        if (poid == 'poids_diapason21'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "3.50")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "40.00") 
                        first_page = first_page.replace("?taille=","?taille=" + taille)
                        if (color == 'N'):
                            first_page = first_page.replace("couleur_inf=","couleur_inf=N")
                            first_page = first_page.replace("couleur_sup=","couleur_sup=Z")
                        else:
                            first_page = first_page.replace("couleur_inf=","couleur_inf=" + color)
                            first_page = first_page.replace("couleur_sup=","couleur_sup=" + color)
                        if (purete == 'X'):
                            first_page = first_page.replace("purete_inf=","purete_inf=XI1")
                            first_page = first_page.replace("purete_sup=","purete_sup=XI3")
                        else:
                            first_page = first_page.replace("purete_inf=","purete_inf=" + purete)
                            first_page = first_page.replace("purete_sup=","purete_sup=" + purete)
                        # first_page = first_page.replace("qualite_taille=","qualite_taille=" + qualite_taille)
                        links_list.append(first_page) #+";")
    for taille in tailles[1:]:
        for poid in poids[0:4]:
            for color in colors:
                for purete in puretes:
                    for price in prices[0:4]:
                        first_page = list_url
                        if (price == 'price_diapason1'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "1500")                           
                        if (price == 'price_diapason2'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "1501")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "2500")   
                        if (price == 'price_diapason3'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "2501")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "5000") 
                        if (price == 'price_diapason4'):
                            first_page = first_page.replace("prix_inf=","prix_inf=" + "5001")
                            first_page = first_page.replace("prix_sup=","prix_sup=" + "10000000") 
                        if (poid == 'poids_diapason1'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.01")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.50")   
                        if (poid == 'poids_diapason2'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.50")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "0.69")                           
                        if (poid == 'poids_diapason3'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "0.70")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "1.40")    
                        if (poid == 'poids_diapason4'):
                            first_page = first_page.replace("poids_inf=","poids_inf=" + "1.40")
                            first_page = first_page.replace("poids_sup=","poids_sup=" + "40.40")   
                        first_page = first_page.replace("?taille=","?taille=" + taille)
                        if (color == 'N'):
                            first_page = first_page.replace("couleur_inf=","couleur_inf=N")
                            first_page = first_page.replace("couleur_sup=","couleur_sup=Z")
                        else:
                            first_page = first_page.replace("couleur_inf=","couleur_inf=" + color)
                            first_page = first_page.replace("couleur_sup=","couleur_sup=" + color)
                        if (purete == 'X'):
                            first_page = first_page.replace("purete_inf=","purete_inf=XI1")
                            first_page = first_page.replace("purete_sup=","purete_sup=XI3")
                        else:
                            first_page = first_page.replace("purete_inf=","purete_inf=" + purete)
                            first_page = first_page.replace("purete_sup=","purete_sup=" + purete)
                        links_list.append(first_page) #+";")
    return links_list

# get cookie from request
def get_cookie(url_path):
    headers = {'Connection':'keep-alive','authority':'www.diamants-infos.com','upgrade-insecure-requests':'1','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
 
    connection_error = "no"
    try:
        response = requests.request("GET", url_path, headers=headers)
        status = response.status_code
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        connection_error = e
        status = "connection_error"
        print("Lost Internet Connection")
        time.sleep(10)  
           
    while status != 200:
        try:
            response = requests.request("GET", url_path, headers=headers)
            status = response.status_code
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10) 

    cookies = response.cookies
    # print(cookies)
    cookie = list(cookies)[0].name + "=" + list(cookies)[0].value + ";" + list(cookies)[1].name + "=" + list(cookies)[1].value
    return cookie

# get data from request
def get_response_data(url_path,cookie):

    headers = {'cookie': cookie,'Connection':'keep-alive','authority':'www.diamants-infos.com','upgrade-insecure-requests':'1','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

    connection_error = "no"
    try:
        h = httplib2.Http()
        response, content = h.request(url_path, headers=headers)
        status = response["status"]
    except (TimeoutError, OSError, HttpLib2Error) as e:
       connection_error = e
       status = "connection_error"
       print("Lost Internet Connection")
       time.sleep(10)  
    while status != "200":
        try:
            h = httplib2.Http()
            response, content = h.request(url_path, headers=headers)
            status = response["status"]
        except (TimeoutError, OSError, HttpLib2Error) as e:
            connection_error = e
            status = "connection_error"
            print("Lost Internet Connection")
            time.sleep(10) 

    data = content.decode('utf-8')
    # with open(output_file_raw, 'w', encoding='utf-8') as data_to_file_raw:
    #     data_to_file_raw.write(str(data))
    return data

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
    sDict = {"Rond Brillant":"ROUND","Princesse":"PRINCESS","Emeraude":"EMERALD","":"NO DATA","Asscher":"Asscher",
    "Coussin":"Cushion","Marquise":"Marquise","Radiant":"Radiant","Ovale":"Oval","Poire":"Pear","Coeur":"Heart","Triangle":"Triangle"}
    return sDict.get(shape,"OTHER")

def getCutFromDictionary(cut):
    cutDict = {"Excellente":"EXCELLENT","Bonne":"GOOD","Très Bonne":"VERY GOOD","Assez Bonne":"Fair","Mauvaise":"Poor","":"NO DATA"}
    return cutDict.get(cut,"OTHER")

def getSymmetryFromDictionary(sym):
    symDict = {"Excellente":"EXCELLENT","Bonne":"GOOD","Très Bonne":"VERY GOOD","Assez Bonne":"Fair","Mauvaise":"Poor","":"NO DATA"}
    return symDict.get(sym,"OTHER")

def getPoliFromDictionary(poli):
    poliDict = {"Excellente":"EXCELLENT","Bon":"GOOD","Très Bon":"VERY GOOD","Assez Bon":"Fair","Mauvais":"Poor","":"NO DATA"}
    return poliDict.get(poli,"OTHER")

def getFluoFromDictionary(fluo):
    fDict = {"Aucune":"None","Moyenne":"Medium","Légère":"Slight","Forte":"Strong","Très Forte":"Very Strong","":"NO DATA"}
    return fDict.get(fluo,"OTHER")

#parse product list to csv file
def add_page_product_data_to_csv(data,output_file_csv,csv_headers,result_file_csv):
    parser = bs4.BeautifulSoup(data, 'lxml')
    results_quantity = parser.select('h1')
    results_quantity_size = len(results_quantity)
    
    length_data = 0
    if results_quantity_size>0:
        results_quantity_text = results_quantity[0].text
        # print(results_quantity_text)
        results_quantity_parse = results_quantity_text.split(" ")
        length_data = int(results_quantity_parse[2])

    if(length_data>0):
        data_items = parser.select('tr')

        with open(output_file_csv, 'w', encoding='utf-8') as csvFile:
            writer = csv.writer(csvFile, delimiter=';', quotechar='|')
            writer.writerow(csv_headers)

            for i in range(1,min(length_data,50)*2,2):
                data_item = data_items[i]
                
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

                id = data_item.find('a').text
                shape = getShapeFromDictionary(data_item.find('td', {'data-title':'Forme Taille'}).text).upper()
                carat = data_item.find('td', {'data-title':'Poids'}).text
                carat = re.sub('[^0-9,]','', carat)
                color = data_item.find('td', {'data-title':'Couleur'}).text
                clarity = data_item.find('td', {'data-title':'Pureté'}).text
                cut = getCutFromDictionary(data_item.find('td', {'data-title':'Qualité Taille'}).text).upper()
                polish = getPoliFromDictionary(data_item.find('td', {'data-title':'Poli'}).text).upper()
                symmetry = getSymmetryFromDictionary(data_item.find('td', {'data-title':'Symétrie'}).text).upper()
                if data_item.find('td', {'data-title':'Fluorescence'}) is not None:
                    fluorescence = getFluoFromDictionary(data_item.find('td', {'data-title':'Fluorescence'}).text).upper()
                if data_item.find('a', {'class':'choix-certificat lien'}) is not None:
                    certificat = data_item.find('a', {'class':'choix-certificat lien'}).text
                prix = data_item.find('td', {'data-title':'Prix'}).text
                prix = re.sub('[^0-9,]','', prix)
                writer.writerow([id,shape,carat,color,clarity,cut,polish,symmetry,fluorescence,certificat,prix])
        add_page_data_to_all_data(output_file_csv,result_file_csv)
    
    return length_data

if __name__ == "__main__":
    main()