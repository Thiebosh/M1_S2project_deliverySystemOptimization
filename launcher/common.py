from subprocess import Popen, PIPE
import asyncio
import time
import math
import re
import os

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
        traveler_name, x, y, speed, qty = parse.fileline_traveler(line, file_name, count)
        to_compute_data["traveler"].append({"name": traveler_name, "x": x, "y": y, "speed": speed, "qty": qty})

    # list peaks and prepare arcs
    nb_peak = len(peaks_line) + sum([x.count(" - ") for x in peaks_line])
    for count, line in enumerate(peaks_line):
        peaks = line.split(" - ")
        origin = peaks[0]
        dests = peaks[1:] if type(peaks[1:]) is list else [peaks[1:]]

        peak_name, x, y = parse.fileline_origin(origin, file_name, count)

        local_data.append({"name": peak_name, "x": x, "y": y})

        origin_id = len(to_compute_data["peak"])
        to_compute_data["peak"].append({"origin": 1, "link": [], "maxCost": 0})

        arc_line = [Arc(x, y) for _ in range(nb_peak)]
        to_compute_data["arc"].append(arc_line)

        for p_count, peak in enumerate(dests):
            peak_name, x, y, qty, max_cost = parse.fileline_dest(peak, file_name, count, p_count)

            local_data.append({"name": peak_name, "x": x, "y": y})

            to_compute_data["peak"][origin_id]["link"].append(len(to_compute_data["peak"]))
            to_compute_data["peak"].append({"origin": 0, "link": origin_id, "qty": qty, "maxCost": max_cost})

            arc_line = [Arc(x, y) for _ in range(nb_peak)]
            to_compute_data["arc"].append(arc_line)

    # compute arcs
    for count, peak in enumerate(local_data):
        for i in range(nb_peak):
            arc = to_compute_data["arc"][i][count]
            dist = arc.set_peakDest(peak["x"], peak["y"]).compute_distance()
            to_compute_data["arc"][i][count] = dist

    return local_data, to_compute_data


async def execute_heuristic(data, batch_size, exe_path, nb_process):
    data = str(data).replace("'", '"')  # print raw string ?
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

        seed = lines[1][:-1]
        data = lines[2][:-1]

        # preprocess results rather than sleep
        results = make_unique(seed, data, results)

    time2 = time.time()
    print(f'heuristics executions took {(time2-time1)*1000.0:.3f} ms\n')

    return sorted(format_result(results), key=lambda x: x[0])


def make_unique(seed, data, current):
    dist, path = data.split(";")
    dist = float(dist)
    seed = int(seed)

    # generate match list (-2 because return to first peak and string)
    comparing_all = [(path[:-2] in f"{x[1][:-2]},{x[1][:-2]}" or path[:-2] in f"{x[1][:-2]},{x[1][:-2]}"[::-1]) for x in current]

    # no match
    if len(comparing_all) == 0 or not comparing_all.__contains__(True):
        current.append((dist, path, seed))

    else:  # match: replace if shorter
        index = comparing_all.index(True)
        if current[index][0] > dist:
            current[index] = (dist, path, seed)

    return current


def format_result(data):
    results = []
    for dist, path, seed in data:
        results.append((dist, [int(x) for x in path.split(",")], seed))

    return results


def print_results(local_data, results):
    print(f"We get {len(results)} distinc(s) peaks travel(s) order(s) :")
    max_digits_dist = 1+int(math.log10(int(results[-1][0])))  # greater nb of digits
    max_digits_seed = 4  # greater nb of digits
    for distance, travel, seed in results:
        travel = str([local_data[x]["name"] for x in travel])[1:-1]
        travel = travel.replace("', '", " -> ")
        print(f"- seed : {seed:{max_digits_seed}d} -> {distance:{max_digits_dist+3}.2f}km for {travel}")  # +3 => '.xx'
