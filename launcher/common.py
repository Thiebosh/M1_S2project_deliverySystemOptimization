from subprocess import Popen, PIPE
import asyncio
import time
import math
import os
import operator
from statistics import mean
from pprint import pprint
import sys
from defines import TMP_FILE


async def execute_heuristic(data, batch_size, nb_process, exe_path):
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
    with open(file_path, "w") as file:
        file.write(data)
    batch_size = str(batch_size)
    running_procs = [Popen([exe_path, file_path, str(current_pid+id), batch_size],
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
        data = [line[:-1] for line in lines[1:6+nb_trav]]

        # preprocess results rather than sleep
        results = make_unique(seed, data, results)

    time2 = time.time()
    print(f'heuristics executions took {(time2-time1)*1000.0:.3f} ms\n')
    return format_result(results)  # sorted(format_result(results), key=lambda x: x[0])


def make_unique(seed, data, current):
    seed = int(seed)
    dist = []
    path = []
    metrics = mean([float(x) if x != "in" else sys.float_info.max for x in data[:5]])

    for line in data[5:]:
        line = line.split(";")
        dist.append(float(line[0]))  # 0 if not used
        path.append(line[1])  # -1 if not used

    # generate match list
    duplicate = [id for id, couple in enumerate(current) if seed == couple[0]]

    # no match
    if not duplicate:
        current.append((seed, list(zip(dist, path)), metrics))

    # else : same random = same path = ignored

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
    data = sorted(data, key=operator.itemgetter(2))
    for id_line, (_, line, metric) in enumerate(data):
        for id_tuple, (dist, path) in enumerate(line):
            data[id_line][1][id_tuple] = (dist, [int(x) for x in path.split(",")])
    print("FORMATED DATA")
    pprint(data)
    return data


def print_results(local_data, results):
    # greater nbs of digits
    print(results)
    higher = max([value for sublist in [([travels[0] for travels in exe[1]]) for exe in results] for value in sublist])
    max_digits_dist = 1+int(math.log10(higher))
    max_digits_name = max([len(x["name"]) for x in local_data["traveler"]])

    print(f"{len(results)} distinc(s) peaks travel(s) order(s) :")

    for seed, travel_list,metric in results:
        print(f"- seed {seed} - score: {metric}:")

        for id, (dist, travel) in enumerate(travel_list):
            travel = [local_data["peak"][x]["name"] for x in travel]

            a = local_data['traveler'][id]['name']
            b = f"{dist:{max_digits_dist+3}.2f}"
            c = "with "+" -> ".join(travel) if dist != 0 else ""
            print(f"\t{a:{max_digits_name}s} : {b}km {c}")

        print()


def format_csv(local_data, results):
    path_data = [["id", "seed", "total_distance", "paths", "img"]]

    for id_travel, (seed, travels, metrics) in enumerate(results):

        total_dist = 0
        paths = ""
        for id_path, (dist, path) in enumerate(travels):
            total_dist += dist
            name = local_data['traveler'][id_path]['name']
            path = [local_data["peak"][x]["name"] if x != -1 else "none" for x in path]
            paths += f"{name} : {', '.join(path)}\n"

        total_dist = str(total_dist).replace(".", ",")
        line = [str(id_travel), str(seed), total_dist, '"'+paths[:-1]+'"']

        path_data.append(line)

    cities_data = [["city_name", "lat", "long"]]

    for city in local_data["peak"]:
        cities_data.append([city['name'], str(city['y']), str(city['x'])])

    return path_data, cities_data


def save_csv(path, data):
    with open(path, "w", encoding='utf-8-sig') as file:
        for line in data:
            file.write(";".join(line)+"\n")
