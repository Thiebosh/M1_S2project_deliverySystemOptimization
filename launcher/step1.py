from subprocess import Popen, PIPE
import asyncio
import time
import os
from numpy import average

from defines import TMP_FILE


async def execute_heuristic(exe_path, nb_process, kpi_weights, data):
    nb_trav = len(data["traveler"])
    current_pid = os.getpid()
    # 5 first rules belongs to numpy array print
    data = str(data).replace("\n", "") \
                    .replace("      ", "") \
                    .replace("array(", "") \
                    .replace(", dtype=float32)", "") \
                    .replace(",dtype=float32)", "") \
                    .replace("'", '"')
    file_path = exe_path[:exe_path.rfind("\\")]+TMP_FILE
    open(file_path, "w").write(data)
    running_procs = [Popen([exe_path, str(current_pid+id), file_path],
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
            print(f"process {current_pid - int(lines[0])} return error '{retcode}'")
            print(lines[1:])
            continue

        seed = lines[1]
        kpi = [line for line in lines[1:5]]
        paths = [line[:-1] for line in lines[6:6+nb_trav]]

        # preprocess results rather than sleep
        results = make_unique(seed, kpi, kpi_weights, paths, results)

    time2 = time.time()
    print(f'heuristics executions took {(time2-time1)*1000.0:.3f} ms\n')

    return sorted(format_result(results), key=lambda x: x[1])


def make_unique(seed, kpi, weights, paths, current):
    seed = int(seed)
    # generate match list : same random = same path = ignored
    if [id for id, couple in enumerate(current) if seed == couple[0]]:
        return current

    kpi = tuple(float(x) if x != "inf" else 10000000 for x in kpi)
    score = average(kpi, weights=weights)
    dist = []
    path = []

    for line in paths:
        line = line.split(";")
        dist.append(float(line[0]))  # 0 if not used
        path.append(line[1])  # -1 if not used

    current.append((seed, score, kpi, list(zip(dist, path))))

    return current


def make_unique_old(seed, data, current):
    dist, path = data.split(";")
    dist = float(dist)
    seed = int(seed)

    # generate match list
    comparing_all = [(path in f"{x[1]},{x[1]}" or path in f"{x[1]},{x[1]}"[::-1]) for x in current]

    # no match
    if len(comparing_all) == 0 or not comparing_all.__contains__(True):
        current.append((dist, path, seed))

    else:  # match: replace if shorter
        index = comparing_all.index(True)
        if current[index][0] > dist:
            current[index] = (dist, path, seed)

    return current


def format_result(data):
    for id_line, line in enumerate(data):
        for id_tuple, (dist, path) in enumerate(line[-1]):
            data[id_line][-1][id_tuple] = (dist, [int(x) for x in path.split(",")])

    return data
