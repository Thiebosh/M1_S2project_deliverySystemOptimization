import pathlib
import asyncio

from parse import user_args
from common import load_data, execute_heuristic, print_results, export_csv
from graph import make_graph
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from dashboard import synchronize

if __name__ == "__main__":    
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"
    file_name, file_path, heuristic_inputs, result_name, save_gif = user_args(path)

    local_data, to_compute = load_data(file_name, file_path)
    results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))
    export_csv(local_data, results)
    print_results(local_data, results)
    make_graph(local_data, results, result_name, save_gif)
    synchronize.remove_images()
    if save_gif:
        synchronize.upload_images()
    synchronize.upload_res()
