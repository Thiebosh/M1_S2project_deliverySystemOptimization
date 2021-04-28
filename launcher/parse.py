import os
import re
import argparse
from distutils.util import strtobool

from defines import ENGINE_FOLDER
from defines import GENERATOR_FOLDER, GENERATOR_EXE
from defines import OPTIMIZER_FOLDER, OPTIMIZER_EXE
from defines import TRAV_INF_CAPACITY


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
    path += ENGINE_FOLDER

    if not config_json["path_generation"]["nb_process"]:
        print("Asked for 0 path generation : done.")
        exit()

    # step1 : path_generation
    generator_path = path+GENERATOR_FOLDER
    if config_json["path_generation"]["algorithm"] == "default":
        regex = re.compile(r"^"+GENERATOR_EXE[1:]+r"[0-9]+\.exe$")
        nb_versions = [x for x in os.listdir(generator_path) if regex.match(x)]
        nb_versions = sorted(nb_versions, key=lambda x: int(x[len(GENERATOR_EXE)-1:-4]))
        generator_path += "\\"+nb_versions[-1]
        config_json["path_generation"]["algorithm"] = nb_versions[-1][:-4]

    else:
        generator_path += GENERATOR_EXE+str(config_json['path_generation']['algorithm'])+".exe"
        if not os.path.exists(generator_path):
            print(f"Engine '{GENERATOR_EXE[1:]}{config_json['path_generation']['algorithm']}.exe' doesn't exist")
            exit()
        config_json["path_generation"]["algorithm"] = GENERATOR_EXE[1:]+str(config_json['path_generation']['algorithm'])
    config_json["path_generation"]["path"] = generator_path

    # step2 : path_optimization
    optimizer_path = path+OPTIMIZER_FOLDER
    for id, opt_algo in enumerate(config_json["path_optimization"]):
        if not opt_algo["apply"]:
            continue

        opti_path = optimizer_path+OPTIMIZER_EXE+opt_algo['algorithm']+".exe"
        if not os.path.exists(opti_path):
            print(f"Engine '{OPTIMIZER_EXE[1:]}{opt_algo['algorithm']}.exe' doesn't exist")
            exit()
        config_json["path_optimization"][id]["path"] = opti_path

    # # step3 : path_fusion
    # fusionner_path = path+FUSIONNER_FOLDER
    # if config_json["path_fusion"]["algorithm"] != "default":
    #     fusionner_path += FUSIONNER_EXE+config_json['path_fusion']['algorithm']+".exe"
    #     if not os.path.exists(generator_path):
    #         print(f"Engine '{FUSIONNER_EXE[1:]}{config_json['path_fusion']['algorithm']}.exe' doesn't exist")
    #         exit()
    #     config_json["path_fusion"]["algorithm"] = fusionner_path

    # # step3 : path_fusion

    return config_json


def traveler_line(line, id_line):
    name, x, y, vehicule, speed, qty = line.split(",")
    try:
        x = float(x)
        y = float(y)
        speed = float(speed)
        qty = int(qty)

    except Exception as e:
        print(f"Traveler block, line {id_line+1} : {e}")
        exit()

    if qty == 0:
        qty = TRAV_INF_CAPACITY  # "infinite"

    return name, x, y, vehicule, speed, qty


def origin_line(line, id_line):
    name, x, y = line.split(",")

    try:
        x = float(x)
        y = float(y)

    except Exception as e:
        print(f"Vertice block, deposit line {id_line+1} : {e}")
        exit()

    return name, x, y


def dest_line(line, id_line, id_vertice):
    name, x, y, *optional = line.split(",")

    try:
        x = float(x)
        y = float(y)
        qty = int(optional[0]) if len(optional) >= 1 else 1

    except Exception as e:
        print(f"Vertice block, line {id_line+1}, client {id_vertice+1} : {e}")
        exit()

    return name, x, y, qty
