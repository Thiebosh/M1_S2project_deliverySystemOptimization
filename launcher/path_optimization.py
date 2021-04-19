from subprocess import Popen, PIPE
import asyncio
from distutils.util import strtobool
import time
import math


async def path_optimization(exe_path, file_path, generated_paths, nb_tries, kpi_weights):
    # .\localSearch.exe id seed datafile path nb_tries
    running_procs = [Popen([exe_path, str(id), generated_paths[id][0],
                            file_path, generated_paths[id][-1]],
                     stdout=PIPE, stderr=PIPE, text=True)
                     for id in range(len(generated_paths))]

    nb_trav = len(generated_paths[0][-1])
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
            print(f"process {int(lines[0])} return error '{retcode}'")
            print(lines[1:])
            continue

        id = int(lines[0])
        generated_paths[id].append(strtobool(lines[1]))  # is better

        if generated_paths[id][-1]:
            kpi = lines[2]
            paths = [line[:-1] for line in lines[3:3+nb_trav]]

            # # preprocess results rather than sleep
            # generated_paths[id][1] = total score
            # generated_paths[id][2] = kpi bien parsé
            # generated_paths[id][-1] = paths bien parsé

    time2 = time.time()
    print(f'Improvement executions took {(time2-time1)*1000.0:.3f} ms\n')

    return generated_paths


def print_optimized(local_data, results, kpi_names, algo):
    for line in [line for line in results if line[-1]]:  # print only better
        pass
