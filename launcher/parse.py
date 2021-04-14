import os
import re
import argparse
from distutils.util import strtobool

from defines import ENGINE_FOLDER


def user_args(path):
    parser = argparse.ArgumentParser("Parsing script args")
    parser.add_argument("config_name", type=str, help="You must specify the name of the config file you want to use")
    parser.add_argument("online", type=lambda x: strtobool(x), nargs="?", default="True", help="You can specify if files are online or local")
    args = parser.parse_args()

    if not args.online:
        args.config_name = path + "\\..\\" + args.config_name

        if args.config_name[-5:] != ".json":
            args.config_name += ".json"

        if not os.path.exists(args.config_name):
            parser.error(f"File config '{args.config_name}' doesn't exist")

    return args.__dict__.values()


def config_verif(path, config_json):
    # step1 : path_generation
    engine_path = path+ENGINE_FOLDER

    if config_json["path_generation"]["algorithm"] == "default":
        regex = re.compile(r"^(v|V)[0-9]+$")
        nb_versions = [x for x in os.listdir(engine_path) if regex.match(x)]
        last_engine = sorted(nb_versions, key=lambda x: int(x[1:]))[-1]
        config_json["path_generation"]["algorithm"] = \
            engine_path+f"\\v{last_engine}\\engine.exe"

    else:
        engine_path += f"\\v{config_json['path_generation']['algorithm']}\\engine.exe"
        if not os.path.exists(engine_path):
            print(f"Engine '{engine_path}' doesn't exist")
            exit()

        config_json["path_generation"]["algorithm"] = engine_path

    # step2 : path_fusion
    engine_path = path+ENGINE_FOLDER

    if config_json["path_fusion"]["algorithm"] == "default":
        config_json["path_fusion"]["algorithm"] = \
            engine_path+"\\v3\\fusion.exe"

    else:
        engine_path += f"\\v3\\fusion.exe"
        if not os.path.exists(engine_path):
            print(f"Engine '{engine_path}' doesn't exist")
            exit()

        config_json["path_fusion"]["algorithm"] = engine_path

    return config_json


def traveler_line(line):  # peut remettre précision nom fichier, no ligne...
    name, x, y, *optional = line.split(",")
    try:
        x = float(x)
        y = float(y)
        speed = float(optional[0]) if len(optional) >= 1 else 1.0
        qty = int(optional[1]) if len(optional) >= 2 else 1

    except Exception as e:
        print(e)
        exit()

    return name, x, y, speed, qty


def origin_line(line):  # peut remettre précision nom fichier, no ligne...
    name, x, y = line.split(",")

    try:
        x = float(x)
        y = float(y)

    except Exception as e:
        print(e)
        exit()

    return name, x, y


def dest_line(line):  # peut remettre précision nom fichier, no ligne...
    name, x, y, *optional = line.split(",")

    try:
        x = float(x)
        y = float(y)
        qty = int(optional[0]) if len(optional) >= 1 else 1

    except Exception as e:
        print(e)
        exit()

    return name, x, y, qty
