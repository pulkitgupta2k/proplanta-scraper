from bs4 import BeautifulSoup
import requests
from pprint import pprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time

def getHTML(link):
    try:
        req = requests.get(link)
        html = req.content
    except:
        time.sleep(60)
        req = requests.get(link)
        html = req.content
    return html

def append_rows(self, values, value_input_option='RAW'):
    params = {
            'valueInputOption': value_input_option
    }
    body = {
            'majorDimension': 'ROWS',
            'values': values
    }
    return self.spreadsheet.values_append(self.title, params, body)

def gsheet_load(butter_arrays, egg_arrays):
    scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)

    butter_final = []
    egg_final = []

    butter_sheet = client.open('proplanta_').worksheet('Butter')
    egg_sheet = client.open('proplanta_').worksheet('Egg')

    butter_final = butter_sheet.get_all_values()
    egg_final = egg_sheet.get_all_values()

    butter_sheet.clear()
    egg_sheet.clear()

    butter_ctr = 2
    for butter_array in butter_arrays:
        if butter_array in butter_final:
            break
        butter_final.insert(butter_ctr, butter_array)
        butter_ctr = butter_ctr+1

    egg_ctr = 2
    for egg_array in egg_arrays:
        if egg_array in egg_final:
            break
        egg_final.insert(egg_ctr, egg_array)
        egg_ctr = egg_ctr+1

    append_rows(butter_sheet, butter_final)
    append_rows(egg_sheet, egg_final)
    print("MODIFIED")


def proplanta(link):
    ret = {}
    next_page = ""
    product_links = []
    html = getHTML(link)
    soup = BeautifulSoup(html, "html.parser")


    next_page_link = soup.find("a", {"class": "a_modul_pagination_next_right_active_bottom"})
    
    articles = soup.findAll("table", {"class": "FARBE_KATALOG_MITTE"})
    for article in articles:
        try:
            product_link = article.find("a")['href']
            product_link = "https://www.proplanta.de" +  product_link
            product_links.append(product_link)
        except:
            pass
    ret["next_page"] = next_page
    ret["product_links"] = product_links

    try:
        next_page = "https://www.proplanta.de/markt-und-preis/" + next_page_link["href"]
    except:
        return ret

    ret["next_page"] = next_page
    return ret


def get_products(link, egg, milk, products):
    ctr = 1
    egg_flag = 0
    milk_flag = 0
    egg_ctr = 0
    milk_ctr = 0
    while(True):
        print(ctr)
        ctr = ctr+1
        try:
            page_dets = proplanta(link)
        except:
            time.sleep(10)
            page_dets = proplanta(link)
        if not page_dets["next_page"]:
            break
        else:
            for product_link in page_dets['product_links']:
                if egg in product_link:
                    if product_link not in products['egg']:
                        products['egg'].insert(egg_ctr,product_link)
                        egg_ctr = egg_ctr + 1
                    else:
                        egg_flag = 1
                elif milk in product_link:
                    if product_link not in products['milk']:
                        products['milk'].insert(milk_ctr,product_link)
                        milk_ctr = milk_ctr + 1
                    else:
                        milk_flag = 1
                if egg_flag and milk_flag:
                    return products
            link = page_dets["next_page"]
    return products

def get_new_products(link, egg, milk, products):
    new_products = {}
    new_products['egg'] = []
    new_products['milk'] = []
    ctr = 1
    egg_flag = 0
    milk_flag = 0
    egg_ctr = 0
    milk_ctr = 0
    while(True):
        print(ctr)
        ctr = ctr+1
        try:
            page_dets = proplanta(link)
        except:
            time.sleep(10)
            page_dets = proplanta(link)
        if not page_dets["next_page"]:
            break
        else:
            for product_link in page_dets['product_links']:
                if egg in product_link:
                    if product_link not in products['egg']:
                        products['egg'].insert(egg_ctr,product_link)
                        new_products['egg'].insert(egg_ctr,product_link)
                        egg_ctr = egg_ctr + 1
                    else:
                        egg_flag = 1
                elif milk in product_link:
                    if product_link not in products['milk']:
                        products['milk'].insert(milk_ctr,product_link)
                        new_products['milk'].insert(milk_ctr,product_link)
                        milk_ctr = milk_ctr + 1
                    else:
                        milk_flag = 1
                if egg_flag and milk_flag:
                    return new_products
            link = page_dets["next_page"]
    return new_products

def get_prices_egg(link):
    html = getHTML(link)
    soup = BeautifulSoup(html, "html.parser")
    ret_inf = []
    product_detail = {}
    date = soup.find("td", {"class": "FARBE_KATALOG_TITEL_MITTE"}).find("span",{"class": "SCHRIFT_KATALOG_INHALT_MITTE"}).text.split("|")[0].strip()
    date = date.replace(".", "/")
    ret_inf.append(date)
    table = soup.find("div", {"id": "NachrichtDetailInhalt"})
    details = table.findAll("tr")

    product_detail["1-DE"] = {}
    product_detail["2-DE"] = {}

    product_detail["1-DE"]["Güteklasse A, Gewichtsklasse XL"] = details[1].findAll("td")[1].text.replace("\xa0", "").replace(",",".").split(" - ")
    product_detail["1-DE"]["Güteklasse A, Gewichtklasse L"] = details[2].findAll("td")[1].text.replace("\xa0", "").replace(",",".").split(" - ")
    product_detail["1-DE"]["Güteklasse A, Gewichtsklasse M"] = details[3].findAll("td")[1].text.replace("\xa0", "").replace(",",".").split(" - ")
    product_detail["1-DE"]["Marktentwicklung"] = details[4].findAll("td")[1].text.replace("\xa0", "")

    product_detail["2-DE"]["Güteklasse A, Gewichtsklasse XL"] = details[6].findAll("td")[1].text.replace("\xa0", "").replace(",",".").split(" - ")
    product_detail["2-DE"]["Güteklasse A, Gewichtklasse L"] = details[7].findAll("td")[1].text.replace("\xa0", "").replace(",",".").split(" - ")
    product_detail["2-DE"]["Güteklasse A, Gewichtsklasse M"] = details[8].findAll("td")[1].text.replace("\xa0", "").replace(",",".").split(" - ")
    product_detail["2-DE"]["Marktentwicklung"] = details[9].findAll("td")[1].text.replace("\xa0", "")
    ret_inf.append(product_detail)
    return ret_inf

def get_prices_milk_butter(link):
    html = getHTML(link)
    soup = BeautifulSoup(html, "html.parser")
    ret_inf = []
    product_detail = {}
    date = soup.find("td", {"class": "FARBE_KATALOG_TITEL_MITTE"}).find("span",{"class": "SCHRIFT_KATALOG_INHALT_MITTE"}).text.split("|")[0].strip()
    date = date.replace(".", "/")
    ret_inf.append(date)

    tables = soup.find("div", {"id": "NachrichtDetailInhalt"})
    table1 = tables.findAll("table")[1].findAll('tr')
    table2 = tables.findAll("table")[3].findAll('tr')

    product_detail["Allgäu"] = {}
    product_detail["Hannover"] = {}

    product_detail["Allgäu"]["Markenbutter_geformt"] = ['', '', '']
    product_detail["Allgäu"]["Markenbutter_lose"] = ['', '', '']
    product_detail["Allgäu"]["Allgäuer Emmentaler"] = ['', '', '']
    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"] = ['', '', '']
    product_detail["Allgäu"]["Kleinlimburger"] = ['', '', '']

    product_detail["Hannover"]["Tagespreis Blockware"] = ['', '', '', '']
    product_detail["Hannover"]["Tagespreis Brotware"] = ['', '', '', '']
    
    product_detail["Allgäu"]["Markenbutter_geformt"][0] = table1[1].findAll("td")[1].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Markenbutter_geformt"][1] = table1[1].findAll("td")[2].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Markenbutter_geformt"][2] = table1[1].findAll("td")[3].text.replace("\xa0", "").replace(",",".")

    product_detail["Allgäu"]["Markenbutter_lose"][0] = table1[2].findAll("td")[1].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Markenbutter_lose"][1] = table1[2].findAll("td")[2].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Markenbutter_lose"][2] = table1[2].findAll("td")[3].text.replace("\xa0", "").replace(",",".")

    product_detail["Allgäu"]["Allgäuer Emmentaler"][0] = table1[3].findAll("td")[1].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Allgäuer Emmentaler"][1] = table1[3].findAll("td")[2].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Allgäuer Emmentaler"][2] = table1[3].findAll("td")[3].text.replace("\xa0", "").replace(",",".")

    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"][0] = table1[4].findAll("td")[1].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"][1] = table1[4].findAll("td")[2].text.replace("\xa0", "").replace(",",".")
    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"][2] = table1[4].findAll("td")[3].text.replace("\xa0", "").replace(",",".")
    try:
        product_detail["Allgäu"]["Kleinlimburger"][0] = table1[5].findAll("td")[1].text.replace("\xa0", "").replace(",",".")
        product_detail["Allgäu"]["Kleinlimburger"][1] = table1[5].findAll("td")[2].text.replace("\xa0", "").replace(",",".")
        product_detail["Allgäu"]["Kleinlimburger"][2] = table1[5].findAll("td")[3].text.replace("\xa0", "").replace(",",".")
    except:
        pass
    product_detail["Hannover"]["Tagespreis Blockware"][0] = table2[2].findAll("td")[1].text.replace("\xa0", "").replace(",",".")
    product_detail["Hannover"]["Tagespreis Blockware"][1] = table2[2].findAll("td")[2].text.replace("\xa0", "").replace(",",".")
    product_detail["Hannover"]["Tagespreis Blockware"][2] = table2[2].findAll("td")[3].text.replace("\xa0", "").replace(",",".")
    product_detail["Hannover"]["Tagespreis Blockware"][3] = table2[2].findAll("td")[4].text.replace("\xa0", "").replace(",",".")

    product_detail["Hannover"]["Tagespreis Brotware"][0] = table2[3].findAll("td")[1].text.replace("\xa0", "").replace(",",".")
    product_detail["Hannover"]["Tagespreis Brotware"][1] = table2[3].findAll("td")[2].text.replace("\xa0", "").replace(",",".")
    product_detail["Hannover"]["Tagespreis Brotware"][2] = table2[3].findAll("td")[3].text.replace("\xa0", "").replace(",",".")
    product_detail["Hannover"]["Tagespreis Brotware"][3] = table2[3].findAll("td")[4].text.replace("\xa0", "").replace(",",".")
    ret_inf.append(product_detail)
    return ret_inf


def make_link_file():
    link = "https://www.proplanta.de/markt-und-preis/"
    with open("links.json", "r") as f:
        product_links = json.load(f)
    new_products = get_new_products("https://www.proplanta.de/markt-und-preis/", "aktuelle-eierpreise", "butterpreise-und-kaesepreise", product_links )
    product_links = get_products(link, "aktuelle-eierpreise", "butterpreise-und-kaesepreise", product_links)
    with open("links.json", "w") as f:
        json.dump(product_links, f)
    return new_products


def driver():
    product_links = make_link_file()
    butter_milk_list = product_links["milk"]
    eggs_list = product_links["egg"]
    # with open("links.json", "r") as f:
    #     product_links = json.load(f)
    #     butter_milk_list = product_links["milk"]
    #     eggs_list = product_links["egg"]
    butter_milk_inf = []
    for butter_milk in butter_milk_list:
        try:
            temp = get_prices_milk_butter(butter_milk)
            temp_l = []
            temp_l.append(temp[0])
            temp_l.append(temp[1]['Allgäu']['Markenbutter_geformt'][0])
            temp_l.append(temp[1]['Allgäu']['Markenbutter_geformt'][1])
            temp_l.append(temp[1]['Allgäu']['Markenbutter_lose'][0])
            temp_l.append(temp[1]['Allgäu']['Markenbutter_lose'][1])
            temp_l.append(temp[1]['Allgäu']['Allgäuer Emmentaler'][0])
            temp_l.append(temp[1]['Allgäu']['Allgäuer Emmentaler'][1])
            temp_l.append(temp[1]['Allgäu']['Emmentaler und Viereckhartkäse'][0])
            temp_l.append(temp[1]['Allgäu']['Emmentaler und Viereckhartkäse'][1])
            temp_l.append(temp[1]['Allgäu']['Kleinlimburger'][0])
            temp_l.append(temp[1]['Allgäu']['Kleinlimburger'][1])

            temp_l.append(temp[1]['Hannover']['Tagespreis Blockware'][0])
            temp_l.append(temp[1]['Hannover']['Tagespreis Blockware'][1])
            temp_l.append(temp[1]['Hannover']['Tagespreis Blockware'][2])

            temp_l.append(temp[1]['Hannover']['Tagespreis Brotware'][0])
            temp_l.append(temp[1]['Hannover']['Tagespreis Brotware'][1])
            temp_l.append(temp[1]['Hannover']['Tagespreis Brotware'][2])
            print(temp[0])
            butter_milk_inf.append(temp_l)
        except:
            pass

    eggs_inf = []
    for eggs in eggs_list:
        try:
            temp = get_prices_egg(eggs)
            temp_l = []
            temp_l.append(temp[0])
            temp_l.append(" - ".join(temp[1]['1-DE']['Güteklasse A, Gewichtklasse L']))
            temp_l.append(" - ".join(temp[1]['1-DE']['Güteklasse A, Gewichtsklasse M']))
            temp_l.append(" - ".join(temp[1]['1-DE']['Güteklasse A, Gewichtsklasse M']))
            temp_l.append(temp[1]['1-DE']['Marktentwicklung'])

            
            temp_l.append(" - ".join(temp[1]['2-DE']['Güteklasse A, Gewichtklasse L']))
            temp_l.append(" - ".join(temp[1]['2-DE']['Güteklasse A, Gewichtsklasse M']))
            temp_l.append(" - ".join(temp[1]['2-DE']['Güteklasse A, Gewichtsklasse M']))
            temp_l.append(temp[1]['2-DE']['Marktentwicklung'])
            print(temp[0])
            eggs_inf.append(temp_l)
        except:
            pass
    
    gsheet_load(butter_milk_inf, eggs_inf)