import pathlib
import asyncio
import os
import json
from datetime import datetime

from parse import user_args, config_verif
from synchronize import Synchronize
from loader import compile_loader, load_data
from files import load_file, save_csv
from common import execute_heuristic, print_results, format_csv
from graph import make_graph

from defines import RESULT_FOLDER, DASHBOAD_URL

if __name__ == "__main__":
    print(f"{datetime.now().time()} - Initializing...\n")
    compile_loader()
    path = str(pathlib.Path(__file__).parent.absolute())

    if not os.path.exists(path+RESULT_FOLDER):
        os.makedirs(path+RESULT_FOLDER)

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
        if config["input_datafile"][-5:] != ".data":
            config["input_datafile"] += ".data"
        datafile = load_file(path+"\\..\\"+config["input_datafile"])

    print(f"{datetime.now().time()} - Parsing input...\n")
    local_data, to_compute = load_data(datafile)

    print(f"{datetime.now().time()} - Simulate paths...\n")
    inputs = (config["path_generation"]["batch_size"],
                config["path_generation"]["nb_process"],
                config["path_generation"]["algorithm"])
    results = asyncio.run(execute_heuristic(to_compute, *inputs))

    if config["results"]["print_console"]:
        print(f"{datetime.now().time()} - Display results...\n")
        print_results(local_data, results)

    print(f"{datetime.now().time()} - Prepare CSV...\n")
    path_csv, cities_csv = format_csv(local_data, results)
    if config["results"]["keep_local"]:
        result_path = path+RESULT_FOLDER+"\\"+config['input_datafile']+"_{0}.csv"
        save_csv(result_path.format("paths"), path_csv)
        save_csv(result_path.format("cities"), cities_csv)

    if config["results"]["graph"]["make"]:
        print(f"{datetime.now().time()} - Generate graphs...\n")
        inputs = (config["input_datafile"],
                    config["results"]["graph"]["show_names"],
                    config["results"]["graph"]["link_vertices"],
                    config["results"]["graph"]["map_background"],
                    config["results"]["graph"]["gif_mode"],
                    config["results"]["graph"]["fps"])
        files = make_graph(path, local_data, to_compute, results, *inputs)

    if online:
        print(f"{datetime.now().time()} - Upload data...\n")
        if config["results"]["graph"]["make"]:
            drive.upload_imgs(config["results"]["graph"]["gif_mode"])
        else:
            path_csv[1].append("--")
            drive.upload_csv(path_csv, cities_csv)

    if config["results"]["graph"]["make"] and \
            not config["results"]["keep_local"]:
        print(f"{datetime.now().time()} - Clear directory...\n")
        [os.remove(file) for file in files if os.path.exists(file)]

    print(f"{datetime.now().time()} - Everything done!\n")

    if online:
        print(f"Please consult results on dashboard :\n{DASHBOAD_URL}\n")
