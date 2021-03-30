import pathlib
import asyncio
import time

from parse import user_args
from common import execute_heuristic, print_results, save_csv, format_csv
from loader import load_data
from graph import make_graph
import os
import sys
import traceback

from dashboard.synchronize import Synchronize


DASHBOAD_URL = "https://datastudio.google.com/u/2/reporting/cd241e7b-cec2-4227-976e-857c5c7bf6c0/page/qRZ9B"

if __name__ == "__main__":
    try:
        path = str(pathlib.Path(__file__).parent.absolute())+"\\"
        path = path[:path.rfind("launcher\\")]

        filename, heuristic_inputs, result_name, save_gif = user_args(path)  # combine filename and result_name : graphs are named after input file | add display results true/false

        drive = Synchronize(filename)

        print("Gathering input...\n")
        local_data, to_compute = load_data(drive.read_input_file())

        print("Simulate paths...\n")
        results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

        print_results(local_data, results)  # if wanted

        path_csv, cities_csv = format_csv(local_data, results)
        save_csv(path+"launcher\\dashboard\\paths.csv", path_csv)  # if wanted
        save_csv(path+"launcher\\dashboard\\cities.csv", cities_csv)  # if wanted

        print("Generate graphs...\n")
        make_graph(local_data, results, result_name, save_gif)  # if wanted -- else, must do path_csv[1].push_back("-")
        drive.upload_imgs()  # if graph wanted

        print("Upload data...\n")
        drive.upload_csv(path_csv, cities_csv)

        print(f"Everything done! Please consult results on dashboard :\n{DASHBOAD_URL}\n")

    except Exception as e:
        traceback.print_exc(e)
