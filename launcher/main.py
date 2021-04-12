import pathlib
import asyncio
import traceback
import os
import json
from datetime import datetime

from parse import user_args, config_verif
from synchronize import Synchronize
from loader import load_data
from common import load_file, execute_heuristic, print_results, save_csv, format_csv
from graph import make_graph
from defines import RESULT_FOLDER, DASHBOAD_URL

if __name__ == "__main__":
    try:
        print(f"{datetime.now().time()} - Initializing...\n")
        # compile
        path = str(pathlib.Path(__file__).parent.absolute())

        if not os.path.exists(path+RESULT_FOLDER):
            os.makedirs(path+RESULT_FOLDER)

        print(f"{datetime.now().time()} - Retrieve inputs...\n")
        config_name, online = user_args(path)

        if online:
            drive = Synchronize(path)
            config = drive.set_configfile(config_name).read_config_file()
            # works but cause : json.decoder.JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig): line 1 column 1 (char 0)
        else:
            config = load_file(config_name)

        config = config_verif(path, json.loads(config))

        if online:
            datafile = drive.set_datafile(config["input_datafile"]).read_input_file()
        else:
            datafile = load_file(path+"\\..\\"+config["input_datafile"])

        filename = config["input_datafile"]
        _make_graph = config["results"]["graph"]["make"]
        gif_mode = config["results"]["graph"]["gif_mode"]
        _print_results = config["results"]["print_console"]
        local_results = config["results"]["keep_local"]
        heuristic_inputs = (config["path_generation"]["batch_size"],
                            config["path_generation"]["nb_process"],
                            config["path_generation"]["algorithm"])

        print(f"{datetime.now().time()} - Parsing input...\n")
        local_data, to_compute = load_data(datafile)

        print(f"{datetime.now().time()} - Simulate paths...\n")
        results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

        if _print_results:
            print(f"{datetime.now().time()} - Display results...\n")
            print_results(local_data, results)

        print(f"{datetime.now().time()} - Prepare CSV...\n")
        path_csv, cities_csv = format_csv(local_data, results)
        if local_results:
            save_csv(path+RESULT_FOLDER+f"\\{filename}_paths.csv", path_csv)
            save_csv(path+RESULT_FOLDER+f"\\{filename}_cities.csv", cities_csv)

        # if _make_graph:
        #     print(f"{datetime.now().time()} - Generate graphs...\n")
        #     files = make_graph(path, local_data, results, filename, gif_mode)

        if online:
            print(f"{datetime.now().time()} - Upload data...\n")
            # if _make_graph:
            #     drive.upload_imgs(gif_mode)  # if graph wanted
            # else:
            path_csv[1].append("--")
            drive.upload_csv(path_csv, cities_csv)

        # if _make_graph and not local_results:
        #     print(f"{datetime.now().time()} - Clear directory...\n")
        #     [os.remove(file) for file in files if os.path.exists(file)]

        print(f"{datetime.now().time()} - Everything done!\n")

        if online:
            print(f"Please consult results on dashboard :\n{DASHBOAD_URL}\n")

    except Exception as e:
        traceback.print_exc(e)
