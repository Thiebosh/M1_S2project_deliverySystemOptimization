import argparse
import os
import pathlib
from subprocess import Popen, PIPE, run
import asyncio
import time
import re

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

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file_name", type=str, help="You must enter the name of the file you want to use")
    arg_parser.add_argument("batch_size", type=int, help="You must enter the number of closest peeks you want to consider")
    arg_parser.add_argument("nb_process", type=int, help="You must enter the number of process you want to start")
    arg_parser.add_argument("engine", type=int, nargs='?', default=nb_versions, help="You can specify the version of the engine you want to use")
    args = arg_parser.parse_args()

    if args.batch_size < 1:
        print("Batch size must be superior to 0")
        exit()

    if args.nb_process < 1:
        print("Number of process must be superior to 0")
        exit()

    file_path = path+args.file_name
    if not os.path.exists(file_path):
        print("This file doesn't exist")
        exit()

    engine_path += "v"+str(args.engine)+"\\engine.exe"
    if not os.path.exists(engine_path):
        print("This engine doesn't exist")
        exit()

    return load_data(file_path), args.batch_size, engine_path, args.nb_process


def normalize_sanitize(arc):
    arc = float(arc)
    if arc < 0:
        raise Exception
    return arc


def load_data(file_path):
    file = open(file_path, "r")
    data = {"peak": [], "arc": []}

    try:
        data["peak"].append([float(x) for x in file.readline()[:-1].split()])

        for line in file.readlines():
            if re.match(r"^\s*$", line):  # only spaces or \t, \r, \n
                continue

            cur_line_data = [normalize_sanitize(x) for x in line[:-1].split()]
            data["arc"].append(cur_line_data)

    except Exception as e:
        print(f"Data acquisition error : {e}")
        exit()

    return data


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

    results = asyncio.run(execute_heuristic(*get_user_parameters(path)))

    for task in format_sort_result(results):
        print(f"peaks travel in '{task[1]}' order take {task[0]}km")
