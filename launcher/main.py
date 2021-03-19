import pathlib
import asyncio
import math

from parse import user_args
from common import load_data, execute_heuristic, make_graph


if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    file_name, file_path, heuristic_inputs, result_name = user_args(path)

    local_data, to_compute = load_data(file_name, file_path)
    results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

    max_digits = 1+int(math.log10(int(results[-1][0])))  # greater nb of digits
    for distance, travel in results:
        travel = str([x+1 for x in travel])[1:-1]
        print(f"- {distance:{max_digits+3}.2f}km for {travel}")  # +3 => '.xx'

    make_graph(local_data, results, result_name)
