from subprocess import Popen, PIPE
import asyncio
import time
import math
from numpy import average


async def path_optimization(exe_path, file_path, generated_paths, nb_tries, kpi_weights):
    running_procs = [Popen([exe_path, str(id), str(generated_paths[id][0]),
                            file_path, str([path for _, path in generated_paths[id][-1]]),
                            str(nb_tries)],
                     stdout=PIPE, stderr=PIPE, text=True)
                     for id in range(len(generated_paths))]

    nb_trav = len(generated_paths[0][-1])
    results = []
    time1 = time.time()
    while running_procs:
        for proc in running_procs:
            retcode = proc.poll()  # check if available
            if not retcode:  # Process finished.
                running_procs.remove(proc)
                break

            else:  # No process is done, wait a bit and check again.
                await asyncio.sleep(.1)
                continue

        lines = proc.communicate()[0].split("\n")
        if retcode and retcode != 0:  # execution error
            print(f"process {int(lines[0])} return error '{retcode}'")
            print(lines[1:])
            if proc in running_procs:
                running_procs.remove(proc)
            continue

        if int(lines[1]):  # is_better
            results.append(generated_paths[int(lines[0])])  # id

            results[-1][2] = tuple(float(x) for x in lines[2].split(","))
            results[-1][1] = average(results[-1][2], weights=kpi_weights)

            dist = []
            path = []
            for line in [line[:-1] for line in lines[3:3+nb_trav]]:
                line = line.split(";")
                dist.append(float(line[0]))  # 0 if not used
                path.append([int(x) for x in line[1].split(",")])  # -1 if not used

            results[-1][3] = list(zip(dist, path))

    time2 = time.time()
    print(f'Improvement executions took {(time2-time1)*1000.0:.3f} ms\n')

    return results


def print_optimized(local_data, results, kpi_names, algo):
    for line in [line for line in results if line[-1]]:  # print only better
        pass
