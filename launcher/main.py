import pathlib
import asyncio
import time

from parse import user_args
from common import execute_heuristic, print_results, save_csv
from loader import load_data
from graph import make_graph
import os
import sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from dashboard.synchronize import Synchronize  # pylint: disable=import-error

if __name__ == "__main__":
    try:
        path = str(pathlib.Path(__file__).parent.absolute())+"\\"
        path = path[:path.rfind("launcher\\")]

        filename, heuristic_inputs, result_name, save_gif = user_args(path)  # combine filename and result_name : graphs are named after input file | add display results true/false

        drive = Synchronize(filename)

        local_data, to_compute = load_data(drive.read_input_file())

        results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

        # print_results(local_data, results)

        print_csv(path, local_data, results)

        make_graph(local_data, results, result_name, save_gif)
        drive.upload_imgs()

        drive.upload_csv()  # print_csv(path, local_data, results))

    except Exception as e:
        traceback.print_exc(e)
