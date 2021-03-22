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
    to_compute_data = {"traveler": [], "peak": [], "arc": []}

    # read file
    try:
        with open(file_path) as file:
            all_lines = [line for line in file.readlines()]

        all_lines.append("\n")  # delimit last data block
        last = -1
        data_lines = []
        for id in [id for id, line in enumerate(all_lines) if re.match(r"^\s*$", line)]:  # empty_lines : only spaces or \t, \r, \n
            if id > last and id-1 != last:
                data_lines.append((last+1, id))
            last = id

        # throw headers lines
        travelers_line = all_lines[data_lines[0][0]+1:data_lines[0][1]]
        peaks_line = all_lines[data_lines[1][0]+1:data_lines[1][1]]

    except Exception as e:
        print(f"Data acquisition error : {e}")
        exit()

    # list travelers
    for count, line in enumerate(travelers_line):
        traveler_name, x, y, speed = parse.fileline_traveler(line, file_name, count)
        to_compute_data["traveler"].append({"name": traveler_name, "x": x, "y": y, "speed": speed})

    # list peaks and prepare arcs
    nb_peak = len(peaks_line) * 2  # TEMPORARY : one origin = one dest
    for count, line in enumerate(peaks_line):
        origin, dests = line.split(" - ")

        peak_name, x, y = parse.fileline_origin(origin, file_name, count)

        local_data.append({"name": peak_name, "x": x, "y": y})

        origin_id = len(to_compute_data["peak"])
        to_compute_data["peak"].append({"origin": 1, "link": [], "maxCost": 0})

        arc_line = [Arc(x, y) for _ in range(nb_peak)]
        to_compute_data["arc"].append(arc_line)

        if type(dests) is not list:
            dests = [dests]
        for p_count, peak in enumerate(dests):
            peak_name, x, y, qty, max_cost = parse.fileline_dest(peak, file_name, count, p_count)

            local_data.append({"name": peak_name, "x": x, "y": y})

            to_compute_data["peak"][origin_id]["link"].append(len(to_compute_data["peak"]))
            to_compute_data["peak"].append({"origin": 0, "link": origin_id, "qty": qty, "maxCost": max_cost})

            arc_line = [Arc(x, y) for _ in range(nb_peak)]
            to_compute_data["arc"].append(arc_line)

    # compute arcs
    for count, peak in enumerate(local_data):
        print("begin matrix", count)
        for i in range(nb_peak):
            print("begin vector", count, i)
            arc = to_compute_data["arc"][i][count]
            dist = arc.set_peakDest(peak["x"], peak["y"]).compute_distance()
            to_compute_data["arc"][i][count] = dist
            print("end   vector", count, i)
        print("end   matrix", count)

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


def make_graph(local_data, results, result_name):
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

    fig.savefig(result_name)
    plt.show()
