from subprocess import Popen, PIPE
import asyncio
import time
import math
import os


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
    results = []
    for dist, path, seed in data:
        results.append((dist, [int(x) for x in path.split(",")], seed))

    return results


def print_results(local_data, results):
    max_digits_dist = 1+int(math.log10(int(results[-1][0])))  # greater nb of digits
    max_digits_seed = 1+int(math.log10(max([x[2] for x in results])))  # greater nb of digits

    print(f"We get {len(results)} distinc(s) peaks travel(s) order(s) :")
    for distance, travel, seed in results:
        travel = str([local_data["peak"][x]["name"] for x in travel])[1:-1]

        a = f"{seed:{max_digits_seed}d}"
        b = local_data['traveler'][0]['name']
        c = f"{distance:{max_digits_dist+3}.2f}"  # +3 => '.xx'
        d = travel.replace("', '", " -> ")
        print(f"- (seed: {a}) {b} : {c}km with {d}")
