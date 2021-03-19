from subprocess import Popen, PIPE
import asyncio
import time
import re
import os
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


def remove_duplicates_from_results(res):
    return res


def format_sort_result(data):
    results = []

    for line in data:
        sep = line.split(";")
        results.append((float(sep[0]), [int(x) for x in sep[1].split(",")]))

    return remove_duplicates_from_results(sorted(results, key=lambda x: x[0]))


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
