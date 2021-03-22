from subprocess import Popen, PIPE
import asyncio
import time
import re
import os
import copy
import numpy as np


import graph
import parse
from Arc import Arc


def load_data(file_name, file_path):
    local_data = []
    to_compute_data = {"peak": [], "arc": [],"traveler": []}

    try:

        with open(file_path) as file:
            all_lines = [line for line in file.readlines()]
            peaks_line= all_lines[:all_lines.index("\n")]
            travelers_line = all_lines[all_lines.index("\n")+1:]
    except Exception as e:
        print(f"Data acquisition error : {e}")
        exit()

    nb_peak = len(peaks_line)
    for count, line in enumerate(peaks_line):
        peak_name, x, y, max_cost = parse.fileline_data(line, file_name, count)

        local_data.append({"name": peak_name, "x": x, "y": y})

        to_compute_data["peak"].append({"maxCost": max_cost})

        arc_line = [Arc(x, y) for _ in range(nb_peak)]
        to_compute_data["arc"].append(arc_line)

    for count, peak in enumerate(local_data):
        for i in range(nb_peak):
            arc = to_compute_data["arc"][i][count]
            dist = arc.set_peakDest(peak["x"], peak["y"]).compute_distance()
            to_compute_data["arc"][i][count] = dist


    nb_travelers = len(travelers_line)
    for count, line in enumerate(travelers_line):
        traveler_name, x, y, speed = parse.fileline_traveler(line, file_name, count)
        to_compute_data["traveler"].append({"name":traveler_name,"x": x,"y": y,"speed": speed})

    return local_data, to_compute_data


async def execute_heuristic(data, batch_size, exe_path, nb_process):
    data = str(data).replace("'", '"')
    batch_size = str(batch_size)
    running_procs = [Popen([exe_path, str(os.getpid()+id), data, batch_size],
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

        data = lines[1][:-1]

        # preprocess results rather than sleep
        results = make_unique(data, results)

    time2 = time.time()
    print(f'heuristics executions took {(time2-time1)*1000.0:.3f} ms\n')

    return sorted(format_result(results), key=lambda x: x[0])


def make_unique(data, current):
    dist, path = data.split(";")
    dist = float(dist)

    # generate match list
    comparing = [(path in f"{x[1]},{x[1]}") for x in current]

    # no match
    if len(comparing) == 0 or not comparing.__contains__(True):
        current.append((dist, path))

    else:  # match: replace if shorter
        index = comparing.index(True)
        if current[index][0] > dist:
            current[index] = (dist, path)

    return current


def format_result(data):
    results = []
    for dist, path in data:
        results.append((dist, [int(x) for x in path.split(",")]))

    return results




    
