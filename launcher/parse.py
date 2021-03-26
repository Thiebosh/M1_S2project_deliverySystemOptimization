import os
import re
import argparse
from distutils.util import strtobool


def user_args(path):
    path = path[:path.rfind("launcher\\")]
    engine_path = path + "core\\"
    nb_versions = len([x for x in os.listdir(engine_path) if re.match(r"^(v|V)[0-9]+$", x)]) - 1  # start with v0

    parser = argparse.ArgumentParser("Parsing script args")
    parser.add_argument("file_name", type=str, help="You must enter the name of the file you want to use")
    parser.add_argument("batch_size", type=int, help="You must enter the number of closest peeks you want to consider")
    parser.add_argument("nb_process", type=int, help="You must enter the number of process you want to start")
    parser.add_argument("engine", type=int, nargs='?', default=nb_versions, help="You can specify the version of the engine you want to use")
    parser.add_argument("result_name", type=str, nargs='?', default="savedFile", help="You can specify the name of the file you want to get")
    parser.add_argument("save_gif", type=lambda x: strtobool(x), nargs="?", default=False, help="You can specify whether you want to save gif or not")
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("Batch size must be superior to 0")

    if args.nb_process < 1:
        parser.error("Number of process must be superior to 0")

    file_path = path+args.file_name
    if not os.path.exists(file_path):
        parser.error("This file doesn't exist")

    engine_path += "v"+str(args.engine)+"\\engine.exe"
    if not os.path.exists(engine_path):
        parser.error("This engine doesn't exist")

    args.result_name = path + args.result_name
    if args.result_name[:-4] != ".png":
        # verifier s'il existe ? si oui, ajouter un increment ?
        args.result_name += ".png"

    heuristic_inputs = (args.batch_size, engine_path, args.nb_process)
    return file_path, heuristic_inputs, args.result_name, args.save_gif


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
        max_cost = float(optional[1]) if len(optional) >= 2 else 0.0

    except Exception as e:
        print(e)
        exit()

    return name, x, y, qty, max_cost
