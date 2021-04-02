from sys import executable as exe, version_info
from subprocess import check_call
from zipfile import ZipFile
import pathlib
import requests
import platform
import os
import re


REQUIRE_FILE = "\\requirements.txt"
EXT_FOLDER = "\\extern_libs\\"

DEPENDENCIES_FLAG = "\\dep_v1.flag"  # dependencies versionning
COUNTRIES_FLAG = "\\countries.flag"

PATH_TO_PROJECT = "\\..\\launcher"
MAPS_FOLDER = PATH_TO_PROJECT+"\\country_maps"
DRIVE_FOLDER = PATH_TO_PROJECT+"\\driveAccess"
CREDS_REQUIRED = 2


def install_dependencies(path):
    if version_info[:2] < (3, 7) or version_info[:2] > (3, 9):
        print("This project support python from version 3.7 to 3.9 :", end=" ")
        print(f"You use python{version_info[0]}.{version_info[1]}.")
        exit()

    print("Install pip libraries...\n")
    check_call([exe, "-m", "pip", "install", "-q", "-r", path+REQUIRE_FILE])

    print("Collect extension packages...")
    path += EXT_FOLDER
    if not os.path.exists(path):
        os.makedirs(path)

    libs = ["GDAL-3.2.2-cp3{0}-cp3{0}{1}-win{2}.whl",
            "pyproj-3.0.1-cp3{0}-cp3{0}{1}-win{2}.whl",
            "Fiona-1.8.18-cp3{0}-cp3{0}{1}-win{2}.whl",
            "Shapely-1.7.1-cp3{0}-cp3{0}{1}-win{2}.whl"]

    minor = version_info[1]
    extra = "m" if minor == 7 else ""
    archi = "_amd64" if int(platform.architecture()[0][:2]) == 64 else "32"
    libs = [lib.format(minor, extra, archi) for lib in libs]
    libs.append("geopandas-0.9.0-py3-none-any.whl")

    remaining = set(libs) - set(os.listdir(path))
    try:
        for id, lib in enumerate(remaining):
            print(f"Download lib {id+1}/{len(remaining)}...")
            url = "https://download.lfd.uci.edu/pythonlibs/w4tscw6k/"+lib
            r = requests.get(url, headers={'user-agent': 'pip-agent/0.0.1'})
            with open(path+lib, 'wb') as f:
                f.write(r.content)
    except requests.ConnectionError:
        print("Distant server is down right now. Try later")
        exit()
    except requests.Timeout:
        print("maybe just unlucky for this one ?")

    print("\nInstall extension packages...\n")
    [check_call([exe, "-m", "pip", "install", "-q", path+lib]) for lib in libs]

    print("Dependencies install is done!\n")


def import_country_maps(path):
    path += MAPS_FOLDER

    if not os.path.exists(path):
        os.makedirs(path)

    print("List zip files to download...\n")
    reg = re.compile(r"^[A-Z]{3}.shp$")
    dl_countries = {file[:-4] for file in os.listdir(path) if reg.match(file)}

    res = requests.get("https://gadm.org/download_country_v3.html", allow_redirects=True)
    all_countries = {line[1:4] for line in str(res.content).split('value=')[1:][1:]}

    print("Download zip...\n")
    for country_code in list(all_countries - dl_countries)[:2]:  # test avec les 2 premiers
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

    print("Unzip files...\n")
    for zipfile in [file for file in os.listdir(path) if file[-4:] == ".zip"]:
        with ZipFile(path+"\\"+zipfile, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            shpFound = False
            shxFound = False
            for fileName in listOfFileNames:
                if fileName.endswith('.shp') and not shpFound:
                    shpFound = True
                    zipObj.extract(fileName, path)
                elif fileName.endswith('.shx') and not shxFound:
                    shxFound = True
                    zipObj.extract(fileName, path)
                if shpFound and shxFound:
                    break

        os.remove(path+"\\"+zipfile)

    print("Country files download is done!\n")


if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())

    if not os.path.exists(path+DEPENDENCIES_FLAG):
        install_dependencies(path)

        with open(path+DEPENDENCIES_FLAG, "w"):
            pass
    else:
        print("Already installed dependencies\n")

    if not os.path.exists(path+COUNTRIES_FLAG):
        import_country_maps(path)

        with open(path+COUNTRIES_FLAG, "w"):
            pass
    else:
        print("Already installed country files\n")

    if not os.path.exists(path+DRIVE_FOLDER):
        os.makedirs(path+DRIVE_FOLDER)

    reg = re.compile(r"^credentials.+\.json")
    creds = [file for file in os.listdir(path+DRIVE_FOLDER) if reg.match(file)]
    if len(creds) < CREDS_REQUIRED:
        print("Put the credential files of your google drive account here :")
        print(path+DRIVE_FOLDER)

    else:
        print("Required number of credentials\n")

    print("Setup done, ready to execute project")
