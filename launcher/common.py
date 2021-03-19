from subprocess import Popen, PIPE
import asyncio
import time
import re
import os
import copy
import matplotlib.pyplot as plt
import numpy as np

import parse
from Arc import Arc


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
        if data not in results:
            results.append(data)

    time2 = time.time()
    print(f'heuristics executions took {(time2-time1)*1000.0:.3f} ms\n')

    return format_sort_result(results)


def format_sort_result(data):
    results = []

    for line in data:
        sep = line.split(";")
        results.append((float(sep[0]), [int(x) for x in sep[1].split(",")]))

    return remove_duplicates_from_results(sorted(results, key=lambda x: x[0]))


def remove_duplicates_from_results(res):
    returnedArray = list()

    for data in res:
        dataCpy = copy.deepcopy(data)
        path = dataCpy[1]
        path.pop()
        pathReversed = list(reversed(path))
        pathExists = False

        for _ in range(len(path)):
            path.insert(0, path.pop())
            pathReversed.insert(0, pathReversed.pop())

            for existingData in returnedArray:
                if existingData[1][:-1] == path or existingData[1][:-1] == pathReversed:
                    pathExists = True
                    break

            if pathExists:
                break

        if not pathExists:
            returnedArray.append(data)

    return returnedArray


def make_graph(local_data, results):
    cities = []
    for i in range(len(results[0][1])-1):
        x = local_data[i]["x"]
        y = local_data[i]["y"]
        cities.append([x, y])

    minX = min([coord[0] for coord in cities])
    maxX = max([coord[0] for coord in cities])
    minY = min([coord[1] for coord in cities])
    maxY = max([coord[1] for coord in cities])

    nb_graph = min(5, len(results))
    fig, axes = plt.subplots(figsize=(10, 10), ncols=nb_graph, sharey=True)
    if type(axes) is not np.ndarray:
        axes = [axes]

    for idGraph, axe in enumerate(axes):
        axe.set_box_aspect(1)
        axe.title.set_text(f"{str(results[idGraph][0])}km\n{str([x+1 for x in results[idGraph][1]])[1:-1]}")
        axe.set_xlim(minX-1, maxX+1)
        axe.set_ylim(minY-1, maxY+1)

        for i in range(len(results[0][1])-1):
            x = local_data[i]["x"]
            y = local_data[i]["y"]
            axe.scatter(x, y, c="black")
            axe.text(x, y+0.5, local_data[i]["name"])

        for idCity, city in enumerate(results[idGraph][1]):
            index = (0 if idCity == len(results[idGraph][1])-1 else idCity+1)
            nexCity = cities[results[idGraph][1][index]]
            city = cities[city]
            axe.arrow(city[0], city[1], nexCity[0]-city[0], nexCity[1]-city[1],
                      head_width=0.15*nb_graph, head_length=0.35*nb_graph,
                      length_includes_head=True, color="red")

        origin = local_data[results[idGraph][1][0]]
        axe.scatter(origin["x"], origin["y"], c="blue")

    plt.show()
    fig.savefig("savedFile.png")
