import pathlib
import asyncio
import time

from parse import user_args
from common import execute_heuristic, print_results, export_csv
from loader import load_data
from graph import make_graph
import os
import sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from dashboard import synchronize

if __name__ == "__main__":
    try:
        path = str(pathlib.Path(__file__).parent.absolute())+"\\"

        file_path, heuristic_inputs, result_name, save_gif = user_args(path)

        local_data, to_compute = load_data(file_path)

        results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))
        # export_csv(local_data, results)
        # print_results(local_data, results)

        # make_graph(local_data, results, result_name, save_gif)
        # synchronize.remove_images()
        # if save_gif:
        #     synchronize.upload_images()
        # synchronize.upload_res()
    except Exception as e:
        traceback.print_exc(e)
