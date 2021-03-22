import pathlib
import asyncio
import math

from parse import user_args
from common import load_data, execute_heuristic
from graph import make_graph

if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    file_name, file_path, heuristic_inputs, result_name, save_gif = user_args(path)

    local_data, to_compute = load_data(file_name, file_path)
    results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

    print(f"We get {len(results)} distinc(s) peaks travel(s) order(s) :")
    max_digits = 1+int(math.log10(int(results[-1][0])))  # greater nb of digits

    for distance, travel in results:
        travel = str([local_data[x]["name"] for x in travel])[1:-1]
        travel = travel.replace("', '", " -> ")
        print(f"- {distance:{max_digits+3}.2f}km for {travel}")  # +3 => '.xx'

    make_graph(local_data, results, result_name, save_gif)
