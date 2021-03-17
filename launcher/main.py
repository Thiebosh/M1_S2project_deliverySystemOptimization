import argparse
import os
import pathlib
from subprocess import Popen, PIPE, run
import asyncio
import time
import re


def get_user_parameters(path):
    path = path[:path.rfind("launcher\\")]
    engine_path = path + "core\\"
    nb_versions = len([x for x in os.listdir(engine_path) if re.match(r"^(v|V)[0-9]+$", x)]) - 1  # start with v0

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file_name", type=str, help="You must enter the name of the file you want to use")
    arg_parser.add_argument("nb_process", type=int, help="You must enter the number of process you want to start")
    arg_parser.add_argument("engine", type=int, nargs='?', default=nb_versions, help="You can specify the version of the engine you want to use")
    args = arg_parser.parse_args()

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

    return args.nb_process, file_path, engine_path


def normalize_sanitize(arc):
    arc = float(arc)
    if arc < 0:
        raise Exception
    return arc


def acquire_data(file_path):
    file = open(file_path, "r")
    data = {"peak": [], "arc": []}

    try:
        data["peak"].append(file.readline()[:-1])

        for line in file.readlines():
            if re.match(r"^\s*$", line):  # only spaces or \t, \r, \n
                continue

            cur_line_data = [normalize_sanitize(x) for x in line[:-1].split()]
            data["arc"].append(cur_line_data)

    except Exception as e:
        print(f"Data acquisition error : {e}")
        exit()

    return data


async def execute_heuristic(nb_process, data, exe_path):
    running_procs = [Popen([exe_path, str(id+1), str(data)], stderr=PIPE, stdout=PIPE, text=True)
                     for id in range(nb_process)]
    # running_procs = [run([exe_path, str(id+1), str(data)], capture_output=True, text=True)  #, timeout=1)  # en secondes
    #                  for id in range(nb_process)]

    results = []
    time1 = time.time()
    while running_procs:
        for proc in running_procs:
            retcode = proc.poll()  # check if available
            # retcode = proc.returncode  # with run but blocking
            if retcode is not None:  # Process finished.
                running_procs.remove(proc)
                break

            else:  # No process is done, wait a bit and check again.
                await asyncio.sleep(.4)
                continue

        if retcode != 0:  # execution error
            id = proc.communicate()[0].split("\\n\\r")[0][:-1]
            print(f"process {id} return error '{retcode}'")
            # print(f"process {id} return error '{proc.stderr}'")
            continue

        results.append(proc.communicate()[0][2:-1])
        # results.append(proc.stdout[2:-1])

    time2 = time.time()
    print(f'heuristics execution took {(time2-time1)*1000.0:.3f} ms')

    return results


def format_sort_result(data):
    results = []

    for line in data:
        sep = line.split(";")
        results.append((float(sep[0]), [int(x) for x in sep[1].split(",")]))

    return sorted(results, key=lambda x: x[0])


if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    nb_process, file_path, engine_path = get_user_parameters(path)

    data = acquire_data(file_path)

    results = asyncio.run(execute_heuristic(nb_process, data, engine_path))

    for task in format_sort_result(results):
        print(f"{task[1]} will take {task[0]}ms")
