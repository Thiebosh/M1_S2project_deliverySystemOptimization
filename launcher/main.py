import pathlib
import asyncio
import os
import json
from datetime import datetime

from parse import user_args, config_verif
from synchronize import Synchronize
from loader import compile_loader, load_data
from files import load_file, save_csv
from step1 import execute_heuristic
from step2 import path_fusion
from common import print_results, print_fusionned, format_csv
from graph import make_graph

from defines import RESULT_FOLDER, DASHBOAD_URL

if __name__ == "__main__":
    # step1 : compile numba functions, create dirs
    print(f"{datetime.now().time()} - Initializing...\n")
    compile_loader()
    path = str(pathlib.Path(__file__).parent.absolute())

    if not os.path.exists(path+RESULT_FOLDER):
        os.makedirs(path+RESULT_FOLDER)

    # step2 : get args, config, parse json config, get input data
    print(f"{datetime.now().time()} - Retrieve inputs...\n")
    config_name, online = user_args(path)

    if online:
        drive = Synchronize(path)
        config = drive.set_configfile(config_name).get_config()
    else:
        config = load_file(config_name)

    config = config_verif(path, json.loads(config))

    if online:
        datafile = drive.set_datafile(config["input_datafile"]).get_input()
    else:
        ext = "" if config["input_datafile"][-5:] == ".data" else ".data"
        datafile = load_file(path+"\\..\\"+config["input_datafile"] + ext)

    # step3 : parse input data, divide it : needed for computation and not
    print(f"{datetime.now().time()} - Parsing input...\n")
    local_data, to_compute = load_data(datafile)

    # step4 : compute data
    print(f"{datetime.now().time()} - Simulate paths...\n")
    inputs = (config["path_generation"]["batch_size"],
              config["path_generation"]["nb_process"],
              config["path_generation"]["algorithm"])
    results = asyncio.run(execute_heuristic(to_compute, *inputs))

    # step5 : optional print of results
    if config["results"]["print_console"]:
        print(f"{datetime.now().time()} - Display step1 results...\n")
        print_results(local_data, results)

    # stepx.1 : collect data for path fusion
    # fusionned_path = path_fusion()

    # stepx.2 : optional print of results
    # if config["results"]["print_console"]:
    #     print(f"{datetime.now().time()} - Display step2 results...\n")
    #     print_fusionned(fusionned_path)

    # step6 : csv formatting and optional saving
    print(f"{datetime.now().time()} - Prepare CSV...\n")
    path_csv, cities_csv = format_csv(local_data, results)
    if config["results"]["keep_local"]:
        result_path = path+RESULT_FOLDER+"\\"+config['input_datafile']+"_{0}.csv"
        save_csv(result_path.format("paths"), path_csv)
        save_csv(result_path.format("cities"), cities_csv)

    # step7 : optional graph generation
    if config["results"]["graph"]["make"]:
        print(f"{datetime.now().time()} - Generate graphs...\n")
        inputs = (config["input_datafile"],
                  config["results"]["graph"]["show_names"],
                  config["results"]["graph"]["link_vertices"],
                  config["results"]["graph"]["map_background"],
                  config["results"]["graph"]["gif_mode"],
                  config["results"]["graph"]["fps"])
        files = make_graph(path, local_data, to_compute, results, *inputs)

    # step8 : send results online
    if online:
        print(f"{datetime.now().time()} - Upload data...\n")
        if config["results"]["graph"]["make"]:
            drive.upload_imgs(config["results"]["graph"]["gif_mode"])
        else:
            path_csv[1].append("--")
            drive.upload_csv(path_csv, cities_csv)

    # step9 : optional cleaning
    if config["results"]["graph"]["make"] and \
            not config["results"]["keep_local"]:
        print(f"{datetime.now().time()} - Clear directory...\n")
        [os.remove(file) for file in files if os.path.exists(file)]

    # step10 : finish
    print(f"{datetime.now().time()} - Everything done!\n")
    if online:
        print(f"Please consult results on dashboard :\n{DASHBOAD_URL}\n")
