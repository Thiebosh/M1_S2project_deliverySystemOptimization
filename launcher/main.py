import pathlib
import asyncio
from parse import user_args
from common import load_data, execute_heuristic


if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    file_name, file_path, heuristic_inputs = user_args(path)

    local_data, to_compute = load_data(file_name, file_path)

    results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

    print(f"We get {len(results)} distinc(s) peaks travel(s) order(s) :")
    for distance, travel in results:
        print(f"- {str(travel)[1:-1]} take {distance}km")
