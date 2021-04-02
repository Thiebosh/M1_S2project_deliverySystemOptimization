import requests
from zipfile import ZipFile
import os
import re

from defines import RESULT_FOLDER, MAPS_FOLDER, CONFIGURED_FLAG


def setup_project(path):
    if not os.path.exists(path+RESULT_FOLDER):
        os.makedirs(path+RESULT_FOLDER)

    if not os.path.exists(path+MAPS_FOLDER):
        os.makedirs(path+MAPS_FOLDER)

    # if not os.path.exists(path+CONFIGURED_FLAG):
    #     import_country_maps(path)

    #     with open(path+CONFIGURED_FLAG, "w"):
    #         pass


def import_country_maps(path):
    path += MAPS_FOLDER

    reg = re.compile(r"^[A-Z]{3}.shp$")
    dl_countries = {file[:-4] for file in os.listdir(path) if reg.match(file)}

    res = requests.get("https://gadm.org/download_country_v3.html", allow_redirects=True)
    all_countries = {line[1:4] for line in str(res.content).split('value=')[1:][1:]}

    remaining = list(all_countries - dl_countries)[:3]  # test avec les 3 premiers

    for country_code in remaining:
        print(country_code)
        try:
            res = requests.get("https://data.biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_"+country_code+"_shp.zip", allow_redirects=True)
            if res.status_code == 200:
                with open(path+"\\"+country_code+".zip", "wb") as file:
                    file.write(res.content)
        except requests.ConnectionError:
            print("Distant server is down right now. Try later")
            exit()
        except requests.Timeout:
            print("maybe just unlucky for this one ?")

    exit()
    # zip_files = [file for file in os.listdir(path) if file[:-3]==".zip" and zipfile != "extracted"]

    for zipfile in os.listdir(path):
        if zipfile == "extracted":
            continue
        with ZipFile(path+"\\"+zipfile, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            shpFound = False
            shxFound = False
            for fileName in listOfFileNames:
                if fileName.endswith('.shp') and shpFound == False:
                    shpFound = True
                    zipObj.extract(fileName, path+"\\extracted")
                elif fileName.endswith('.shx') and shxFound == False:
                    shxFound = True
                    zipObj.extract(fileName, path+"\\extracted")
                if shpFound and shxFound:
                    break

    exit()

    files = os.listdir(path+"\\extracted")
    for file in files:
        ext = file[len(file)-4:]
        os.rename(path+"\\extracted\\"+file, path+"\\extracted\\"+file.split("gadm36_")[1][:3]+ext)
    # newName = fileName.split("gadm36_")[1][:3]+".shx"
