import os
import re
import argparse
from distutils.util import strtobool


def user_args(path):
    engine_path = path[:path.rfind("\\")]+"\\core"
    regex = re.compile(r"^(v|V)[0-9]+$")
    nb_versions = [x for x in os.listdir(engine_path) if regex.match(x)]
    nb_versions = sorted(nb_versions, key=lambda x: int(x[1:]))[-1][1:]

    parser = argparse.ArgumentParser("Parsing script args")
    parser.add_argument("file_name", type=str, help="You must enter the name of the file you want to use")
    parser.add_argument("batch_size", type=int, help="You must enter the number of closest peeks you want to consider")
    parser.add_argument("nb_process", type=int, help="You must enter the number of process you want to start")
    parser.add_argument("engine", type=int, nargs='?', default=nb_versions, help="You can specify the version of the engine you want to use")
    parser.add_argument("make_graph", type=lambda x: strtobool(x), nargs="?", default=True, help="You can specify whether you want to generate graphs or not")
    parser.add_argument("gif_mode", type=lambda x: strtobool(x), nargs="?", default=False, help="You can specify whether you want to save gif or not")
    parser.add_argument("print_results", type=lambda x: strtobool(x), nargs="?", default=True, help="You can specify whether you want to print results in console or not")
    parser.add_argument("keep_local_results", type=lambda x: strtobool(x), nargs="?", default=False, help="You can specify whether you want to conserve local result files or not")
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("Batch size must be superior to 0")

    if args.nb_process < 1:
        parser.error("Number of process must be superior to 0")

    args.engine = engine_path + f"\\v{args.engine}\\engine.exe"
    if not os.path.exists(args.engine):
        parser.error("This engine doesn't exist")

    return args.__dict__.values()


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
