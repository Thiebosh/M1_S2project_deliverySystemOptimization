from subprocess import check_call
from sys import executable as exe, version_info
import pathlib
import os
import requests
import platform

REQUIRE_FILE = "\\requirements.txt"
EXT_FOLDER = "\\extern_libs\\"


def install_dependencies(path):
    if version_info[:2] < (3, 7) or version_info[:2] > (3, 9):
        print("This project support python from version 3.7 to 3.9 :", end=" ")
        print(f"You use python{version_info[0]}.{version_info[1]}.")
        exit()

    print("install pip libraries...\n")
    check_call([exe, "-m", "pip", "install", "-q", "-r", path+REQUIRE_FILE])

    print("collect extension packages...")
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
    for id, lib in enumerate(remaining):
        print(f"Download lib {id+1}/{len(remaining)}...")
        url = "https://download.lfd.uci.edu/pythonlibs/w4tscw6k/"+lib
        r = requests.get(url, headers={'user-agent': 'pip-agent/0.0.1'})
        with open(path+lib, 'wb') as f:
            f.write(r.content)

    print("\ninstall extension packages...\n")
    [check_call([exe, "-m", "pip", "install", "-q", path+lib]) for lib in libs]

    print("Everything done!")


if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())

    install_dependencies(path)
