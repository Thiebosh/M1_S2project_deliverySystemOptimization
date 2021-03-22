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
    return args.file_name, file_path, heuristic_inputs, args.result_name


def fileline_peak(arc, file_name, lineNb):
    parser = argparse.ArgumentParser(f"Parsing line {lineNb+1} of file '{file_name}'")
    parser.add_argument("peak_name", type=str)
    parser.add_argument("x", type=float)
    parser.add_argument("y", type=float)
    parser.add_argument("origin", type=lambda x: strtobool(x))  # wrap into bool for real object but break program
    parser.add_argument("link", type=str)
    parser.add_argument("max_cost", type=float, nargs='?', default=0.0)
    args = parser.parse_args(arc.replace('\n', '').split(','))

    if args.max_cost < 0:
        parser.error("max_cost value must be greater or equal to 0")

    return args.peak_name, args.x, args.y, args.origin, args.link, args.max_cost


def fileline_traveler(line, file_name, lineNb):
    parser = argparse.ArgumentParser(f"Parsing line {lineNb+1} of file '{file_name}'")
    parser.add_argument("traveler_name", type=str)
    parser.add_argument("x", type=float)
    parser.add_argument("y", type=float)
    parser.add_argument("speed", type=float)
    args = parser.parse_args(line.replace('\n', '').split(','))

    return args.traveler_name, args.x, args.y, args.speed
