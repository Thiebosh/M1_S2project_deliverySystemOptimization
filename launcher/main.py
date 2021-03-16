import argparse
import os
import pathlib
from subprocess import Popen, PIPE
import time


def get_user_parameters(path):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file_name", type=str, help="You must enter the name of the file you want to use")
    arg_parser.add_argument("nb_process", type=int, help="You must enter the number of process you want to start")
    args = arg_parser.parse_args()

    if args.nb_process < 1:
        print("Number of process must be superior to 1")
        exit()

    file_path = path+args.file_name
    if not os.path.exists(file_path):
        print("This file doesn't exist")
        exit()

    return args.nb_process, file_path


def acquire_data(file_path):
    file = open(file_path, "r")
    data = {"distances": []}

    for line in file.readlines():
        cur_line_data = [float(x) for x in line[:-1].split()]
        data["distances"].append(cur_line_data)

    return data


def execute_heuristic(nb_process, data, exe_path):
    running_procs = [Popen([exe_path, data, str(id)], stderr=PIPE, stdout=PIPE)
                     for id in range(nb_process)]
    print([str(id) for id in range(nb_process)])

    results = []
    while running_procs:
        for proc in running_procs:
            retcode = proc.poll()  # check if available
            if retcode is not None:  # Process finished.
                running_procs.remove(proc)
                break

            else:  # No process is done, wait a bit and check again.
                print(proc.communicate()[0].decode("utf-8")[:-2])
                time.sleep(.1)
                continue

        # Here, `proc` has finished with return code `retcode`
        if retcode != 0:
            print(f"c'est louche : {retcode}")

        results.append(proc.communicate()[0].decode("utf-8")[:-2])

    return results


if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    nb_process, file_path = get_user_parameters(path)

    data = acquire_data(file_path)

    results = execute_heuristic(nb_process, data, path+"test.exe")

    for res in results:
        print(res)

    # sorting part
    tasks = [(12, "4,5,8"), (2, "8,5,4"), (8, "5,8,4")]

    for task in sorted(tasks, key=lambda x: x[0]):
        print(f"{task[1]} took {task[0]}")
