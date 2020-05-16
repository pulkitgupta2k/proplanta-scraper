from bs4 import BeautifulSoup
import requests
from pprint import pprint

def getHTML(link):
    req = requests.get(link)
    html = req.content
    return html

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


def get_products(link, checker):
    products = []
    while(True):
        page_dets = proplanta(link)
        if not page_dets["next_page"]:
            break
        else:
            for product_link in page_dets['product_links']:
                if(checker in product_link):
                    products.append(product_link)
            link = page_dets["next_page"]
    return(products)

def get_prices_egg(link):
    html = getHTML(link)
    soup = BeautifulSoup(html, "html.parser")
    product_detail = {}
    date = soup.find("td", {"class": "FARBE_KATALOG_TITEL_MITTE"}).find("span",{"class": "SCHRIFT_KATALOG_INHALT_MITTE"}).text.split("|")[0].strip()
    # print(date)
    product_detail["date"] = date
    table = soup.find("div", {"id": "NachrichtDetailInhalt"})
    details = table.findAll("tr")

    product_detail["1-DE"] = {}
    product_detail["2-DE"] = {}

    product_detail["1-DE"]["Güteklasse A, Gewichtsklasse XL"] = details[1].findAll("td")[1].text.replace("\xa0", "").split(" - ")
    product_detail["1-DE"]["Güteklasse A, Gewichtklasse L"] = details[2].findAll("td")[1].text.replace("\xa0", "").split(" - ")
    product_detail["1-DE"]["Güteklasse A, Gewichtsklasse M"] = details[3].findAll("td")[1].text.replace("\xa0", "").split(" - ")
    product_detail["1-DE"]["Marktentwicklung"] = details[4].findAll("td")[1].text.replace("\xa0", "")

    product_detail["2-DE"]["Güteklasse A, Gewichtsklasse XL"] = details[6].findAll("td")[1].text.replace("\xa0", "").split(" - ")
    product_detail["2-DE"]["Güteklasse A, Gewichtklasse L"] = details[7].findAll("td")[1].text.replace("\xa0", "").split(" - ")
    product_detail["2-DE"]["Güteklasse A, Gewichtsklasse M"] = details[8].findAll("td")[1].text.replace("\xa0", "").split(" - ")
    product_detail["2-DE"]["Marktentwicklung"] = details[9].findAll("td")[1].text.replace("\xa0", "")
    return(product_detail)

def get_prices_milk_butter(link):
    html = getHTML(link)
    soup = BeautifulSoup(html, "html.parser")
    product_detail = {}
    date = soup.find("td", {"class": "FARBE_KATALOG_TITEL_MITTE"}).find("span",{"class": "SCHRIFT_KATALOG_INHALT_MITTE"}).text.split("|")[0].strip()
    print(date)
    product_detail["date"] = date

    tables = soup.find("div", {"id": "NachrichtDetailInhalt"})
    table1 = tables.findAll("table")[1].findAll('tr')
    table2 = tables.findAll("table")[3].findAll('tr')
    
    # print(table1.text)
    # print(table2.text)
    product_detail["Allgäu"] = {}
    product_detail["Hannover"] = {}

    product_detail["Allgäu"]["Markenbutter_geformt"] = ['', '', '']
    product_detail["Allgäu"]["Markenbutter_lose"] = ['', '', '']
    product_detail["Allgäu"]["Allgäuer Emmentaler"] = ['', '', '']
    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"] = ['', '', '']

    product_detail["Hannover"]["Tagespreis Blockware"] = ['', '', '', '']
    product_detail["Hannover"]["Tagespreis Brotware"] = ['', '', '', '']
    
    product_detail["Allgäu"]["Markenbutter_geformt"][0] = table1[1].findAll("td")[1].text.replace("\xa0", "")
    product_detail["Allgäu"]["Markenbutter_geformt"][1] = table1[1].findAll("td")[2].text.replace("\xa0", "")
    product_detail["Allgäu"]["Markenbutter_geformt"][2] = table1[1].findAll("td")[3].text.replace("\xa0", "")

    product_detail["Allgäu"]["Markenbutter_lose"][0] = table1[2].findAll("td")[1].text.replace("\xa0", "")
    product_detail["Allgäu"]["Markenbutter_lose"][1] = table1[2].findAll("td")[2].text.replace("\xa0", "")
    product_detail["Allgäu"]["Markenbutter_lose"][2] = table1[2].findAll("td")[3].text.replace("\xa0", "")

    product_detail["Allgäu"]["Allgäuer Emmentaler"][0] = table1[3].findAll("td")[1].text.replace("\xa0", "")
    product_detail["Allgäu"]["Allgäuer Emmentaler"][1] = table1[3].findAll("td")[2].text.replace("\xa0", "")
    product_detail["Allgäu"]["Allgäuer Emmentaler"][2] = table1[3].findAll("td")[3].text.replace("\xa0", "")

    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"][0] = table1[4].findAll("td")[1].text.replace("\xa0", "")
    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"][1] = table1[4].findAll("td")[2].text.replace("\xa0", "")
    product_detail["Allgäu"]["Emmentaler und Viereckhartkäse"][2] = table1[4].findAll("td")[3].text.replace("\xa0", "")

    product_detail["Hannover"]["Tagespreis Blockware"][0] = table2[2].findAll("td")[1].text.replace("\xa0", "")
    product_detail["Hannover"]["Tagespreis Blockware"][1] = table2[2].findAll("td")[2].text.replace("\xa0", "")
    product_detail["Hannover"]["Tagespreis Blockware"][2] = table2[2].findAll("td")[3].text.replace("\xa0", "")
    product_detail["Hannover"]["Tagespreis Blockware"][3] = table2[2].findAll("td")[4].text.replace("\xa0", "")

    product_detail["Hannover"]["Tagespreis Brotware"][0] = table2[3].findAll("td")[1].text.replace("\xa0", "")
    product_detail["Hannover"]["Tagespreis Brotware"][1] = table2[3].findAll("td")[2].text.replace("\xa0", "")
    product_detail["Hannover"]["Tagespreis Brotware"][2] = table2[3].findAll("td")[3].text.replace("\xa0", "")
    product_detail["Hannover"]["Tagespreis Brotware"][3] = table2[3].findAll("td")[4].text.replace("\xa0", "")
    pprint(product_detail)
    return product_detail

def driver():
    butter_milk_list = get_products("https://www.proplanta.de/markt-und-preis/butterpreise_notierungen_r418a25s0_seite_1_von_17.html", "butterpreise-und-kaesepreise")
    eggs = get_products("https://www.proplanta.de/markt-und-preis/aktuelle+eierpreise_notierungen_r832a25s0_seite_1_von_34.html", "aktuelle-eierpreise")


# driver()
# get_prices_egg("https://www.proplanta.de/markt-und-preis/rheinische-warenboerse/aktuelle-eierpreise-08-05-2020_notierungen1588957359.html")
# pprint(proplanta("https://www.proplanta.de/markt-und-preis/butterpreise_notierungen_r418a25s0_seite_1_von_17.html"))
# get_prices_milk_butter("https://www.proplanta.de/markt-und-preis/agrarmarkt-berichte/butterpreise-und-kaesepreise-vom-13-05-2020_notierungen1589389483.html")