import argparse
import os
import pathlib
from subprocess import Popen, PIPE, run
import asyncio
import time
import re
import math


def remove_duplicates_from_results(res):
    returnedArray = list()
    for data in res:
        if data not in returnedArray:
            returnedArray.append(data)
    return returnedArray


def get_user_parameters(path):
    path = path[:path.rfind("launcher\\")]
    engine_path = path + "core\\"
    nb_versions = len([x for x in os.listdir(engine_path) if re.match(r"^(v|V)[0-9]+$", x)]) - 1  # start with v0

    parser = argparse.ArgumentParser("Parsing script args")
    parser.add_argument("file_name", type=str, help="You must enter the name of the file you want to use")
    parser.add_argument("batch_size", type=int, help="You must enter the number of closest peeks you want to consider")
    parser.add_argument("nb_process", type=int, help="You must enter the number of process you want to start")
    parser.add_argument("engine", type=int, nargs='?', default=nb_versions, help="You can specify the version of the engine you want to use")
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("Batch size must be superior to 0")

    if args.nb_process < 1:
        parser.error("Number of process must be superior to 0")

    file_path = path+args.file_name
    if not os.path.exists(file_path):
        parser.error("This file doesn't exist")

    engine_path += "v"+str(args.engine)+"\\engine.exe"
    if not os.path.exists(engine_path):
        parser.error("This engine doesn't exist")

    return args.file_name, file_path, args.batch_size, engine_path, args.nb_process


class Arc:
    def __init__(self, x, y):
        self.x1 = x
        self.y1 = y
        self.x2 = x
        self.y2 = y

    def set_peakDest(self, x, y):
        self.x2 = x
        self.y2 = y
        return self

    def compute_distance(self):
        x = self.x2 - self.x1
        y = self.y2 - self.y1
        return round(math.sqrt(x*x + y*y), 2)

    def get(self):
        print(self.x1, self.y1)


def normalize_sanitize(arc, file_name, line):
    parser = argparse.ArgumentParser(f"Parsing line {line+1} of file '{file_name}'")
    parser.add_argument("peak_name", type=str)
    parser.add_argument("x", type=float)
    parser.add_argument("y", type=float)
    parser.add_argument("max_cost", type=float)
    args = parser.parse_args(arc.replace('\n', '').split(','))

    if args.max_cost < 0:
        parser.error("max_cost value must be greater or equal to 0")

    return args.peak_name, args.x, args.y, args.max_cost


def load_data(file_name, file_path):
    local_data = []
    to_compute_data = {"peak": [], "arc": []}

    try:
        with open(file_path) as file:
            all_lines = [line for line in file.readlines() if not re.match(r"^\s*$", line)]  # remove if only spaces or \t, \r, \n
    except Exception as e:
        print(f"Data acquisition error : {e}")
        exit()

    nb_peak = len(all_lines)
    for count, line in enumerate(all_lines):
        peak_name, x, y, max_cost = normalize_sanitize(line, file_name, count)

        local_data.append({"name": peak_name, "x": x, "y": y})

        to_compute_data["peak"].append({"maxCost": max_cost})

        arc_line = [Arc(x, y) for _ in range(nb_peak)]
        to_compute_data["arc"].append(arc_line)

    for count, peak in enumerate(local_data):
        for i in range(nb_peak):
            arc = to_compute_data["arc"][i][count]
            dist = arc.set_peakDest(peak["x"], peak["y"]).compute_distance()
            to_compute_data["arc"][i][count] = dist

    return local_data, to_compute_data


async def execute_heuristic(data, batch_size, exe_path, nb_process):
    running_procs = [Popen([exe_path, str(os.getpid()+id), str(data).replace("'", '"'), str(batch_size)],
                     stdout=PIPE, stderr=PIPE, text=True)
                     for id in range(nb_process)]

    results = []
    time1 = time.time()
    while running_procs:
        for proc in running_procs:
            retcode = proc.poll()  # check if available
            if not retcode:  # Process finished.
                running_procs.remove(proc)
                break

            else:  # No process is done, wait a bit and check again.
                await asyncio.sleep(.4)
                continue

        lines = proc.communicate()[0].split("\n")

        if retcode and retcode != 0:  # execution error
            print(f"process {lines[0]} return error '{retcode}'")
            print(lines[1:])
            continue

        results.append(lines[1][:-1])

    time2 = time.time()
    print(f'heuristics executions took {(time2-time1)*1000.0:.3f} ms\n')

    return results


def format_sort_result(data):
    results = []

    for line in data:
        sep = line.split(";")
        results.append((float(sep[0]), [int(x) for x in sep[1].split(",")]))

    return remove_duplicates_from_results(sorted(results, key=lambda x: x[0]))


if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    file_name, file_path, batch_size, engine_path, nb_process = get_user_parameters(path)

    local_data, to_compute_data = load_data(file_name, file_path)

    print(to_compute_data)
    results = asyncio.run(execute_heuristic(to_compute_data, batch_size, engine_path, nb_process))
    print(results)

    for task in format_sort_result(results):
        print(f"peaks travel in '{task[1]}' order take {task[0]}km")
