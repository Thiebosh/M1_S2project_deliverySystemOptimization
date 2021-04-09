import pathlib
import asyncio
import traceback
import os
from datetime import datetime

from parse import user_args
from synchronize import Synchronize
from loader import load_data
from common import execute_heuristic, print_results, save_csv, format_csv
from graph import make_graph
from defines import RESULT_FOLDER, DASHBOAD_URL

if __name__ == "__main__":
    try:
        print(f"{datetime.now().time()} - Initializing...\n")
        path = str(pathlib.Path(__file__).parent.absolute())

        if not os.path.exists(path+RESULT_FOLDER):
            os.makedirs(path+RESULT_FOLDER)

        filename, *heuristic_inputs, _make_graph, gif_mode,\
            _print_results, local_results = user_args(path)

        drive = Synchronize(path, filename, gif_mode)

        print(f"{datetime.now().time()} - Gathering input...\n")
        local_data, to_compute = load_data(drive.read_input_file())

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

        print(f"{datetime.now().time()} - Upload data...\n")
        # if _make_graph:
        #     drive.upload_imgs()  # if graph wanted
        # else:
        path_csv[1].append("--")
        drive.upload_csv(path_csv, cities_csv)

        # if _make_graph and not local_results:
        #     print(f"{datetime.now().time()} - Clear directory...\n")
        #     [os.remove(file) for file in files if os.path.exists(file)]

        print(f"{datetime.now().time()} - Everything done!")
        print(f"Please consult results on dashboard :\n{DASHBOAD_URL}\n")

    except Exception as e:
        traceback.print_exc(e)
