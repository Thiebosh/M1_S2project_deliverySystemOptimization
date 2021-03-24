import pathlib
import asyncio
import time

from parse import user_args
from loader import load_data
from common import execute_heuristic, print_results
from graph import make_graph

if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    file_path, heuristic_inputs, result_name, save_gif = user_args(path)

    local_data, to_compute = load_data(file_path)

    results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

    print_results(local_data, results)

    make_graph(local_data, results, result_name, save_gif)
