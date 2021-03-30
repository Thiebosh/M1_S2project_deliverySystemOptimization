import pathlib
import asyncio
import time
import traceback

from parse import user_args
from synchronize import Synchronize
from loader import load_data
from common import execute_heuristic, print_results, save_csv, format_csv
from graph import make_graph


DASHBOAD_URL = "https://datastudio.google.com/u/2/reporting/cd241e7b-cec2-4227-976e-857c5c7bf6c0/page/qRZ9B"

if __name__ == "__main__":
    try:
        path = str(pathlib.Path(__file__).parent.absolute())

        filename, heuristic_inputs, save_gif = user_args(path)  # add display results true/false

        drive = Synchronize(filename)

        print("Gathering input...\n")
        local_data, to_compute = load_data(drive.read_input_file())

        print("Simulate paths...\n")
        results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

        print_results(local_data, results)  # if wanted

        path_csv, cities_csv = format_csv(local_data, results)
        save_csv(path+"\\results\\paths.csv", path_csv)  # if wanted
        save_csv(path+"\\results\\cities.csv", cities_csv)  # if wanted

        print("Generate graphs...\n")
        make_graph(path, local_data, results, filename, save_gif)  # if wanted -- else, must do path_csv[1].push_back("-")
        drive.upload_imgs()  # if graph wanted

        print("Upload data...\n")
        drive.upload_csv(path_csv, cities_csv)

        print(f"Everything done! Please consult results on dashboard :\n{DASHBOAD_URL}\n")

    except Exception as e:
        traceback.print_exc(e)
