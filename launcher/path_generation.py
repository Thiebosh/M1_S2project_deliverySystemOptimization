from subprocess import Popen, PIPE
import asyncio
import time
import os
from numpy import average
import math


async def path_generation(exe_path, recurs, back_origin, nb_process, file_path, kpi_weights, nb_trav):
    current_pid = os.getpid()
    running_procs = [Popen([exe_path, str(current_pid+id), str(recurs), str(back_origin), file_path],
                     stdout=PIPE, stderr=PIPE, text=True)
                     for id in range(nb_process)]

    results = []
    time1 = time.time()
    while running_procs:
        ended_proc = False
        for proc in running_procs:
            retcode = proc.poll()  # check if available
            if not retcode:  # Process finished.
                running_procs.remove(proc)
                ended_proc = True
                break

        if not ended_proc:  # No process is done, wait a bit and check again.
            await asyncio.sleep(.4)
            continue

        lines = proc.communicate()[0].split("\n")
        if lines[2] == "error":  # retcode and retcode != 0:  # execution error
            print(f"process {int(lines[0]) - current_pid} return error '{retcode}'")
            print(lines[1:])
            if proc in running_procs:
                running_procs.remove(proc)
            continue

        seed = lines[1]
        kpi = lines[2]
        paths = [line[:-1] for line in lines[3:3+nb_trav]]

        # preprocess results rather than sleep
        results = make_unique(seed, kpi, kpi_weights, paths, results)

    time2 = time.time()
    print(f'heuristics executions took {(time2-time1)*1000.0:.3f} ms\n')

    return sorted(results, key=lambda x: x[1])  # sort on score


def make_unique(seed, kpi, weights, paths, current):
    seed = int(seed)
    # generate match list : same random = same path = ignored
    if [id for id, couple in enumerate(current) if seed == couple[0]]:
        return current

    kpi = tuple(float(x) for x in kpi.split(","))
    score = average(kpi, weights=weights)
    dist = []
    path = []

    for line in paths:
        line = line.split(";")
        dist.append(float(line[0]))  # 0 if not used
        path.append([int(x) for x in line[1].split(",")])  # -1 if not used

    current.append([seed, score, kpi, list(zip(dist, path))])

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


def print_generated(local_data, results, kpi_names, algo):
    digit_seed = 1+int(math.log10(max([exe[0] for exe in results])))
    digit_score = 1+int(math.log10(max([exe[1] for exe in results])))+3
    digit_name = max([len(x["name"]) for x in local_data["traveler"]])
    digit_kpi = max([len(x) for x in kpi_names])

    print(f"{len(results)} distinc(s) peaks travel(s) order(s) generated with {algo}:")

    for id_exe, (seed, score, kpi_values, travel_list) in enumerate(results):
        print(f"- Generation {id_exe+1}, seed {seed:{digit_seed}d} :")
        print(f"    Score of {score:{digit_score}.2f}")
        print(f"\tKey performance indicators :")
        for id, name in enumerate(kpi_names):
            print(f"\t- {name:{digit_kpi}s} : {kpi_values[id]}")

        for id, (dist, travel) in enumerate(travel_list):
            travel = [local_data["peak"][x]["name"] for x in travel]

            a = f"{local_data['traveler'][id]['name']:{digit_name}s}"
            b = f"{dist:{digit_score+3}.2f}"
            c = "with "+" -> ".join(travel) if dist > 0 else ""
            print(f"\t\t{a} : {b}km {c}")

        print()
