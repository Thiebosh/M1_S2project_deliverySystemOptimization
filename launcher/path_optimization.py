from subprocess import Popen, PIPE
import asyncio
import time
import math
from numpy import average


async def path_optimization(exe_path, file_path, generated_paths, nb_tries, back_origin, kpi_weights):
    running_procs = [Popen([exe_path, str(id), str(generated_paths[id][0]),
                            file_path, str([path for _, path in generated_paths[id][-1]]),
                            str(nb_tries), str(back_origin)],
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
            kpi = tuple(float(x) for x in lines[2].split(","))
            score = average(kpi, weights=kpi_weights)

            if round(generated_paths[int(lines[0])][1]) == round(score):
                continue

            # deepcopy id
            results.append([value for value in generated_paths[int(lines[0])]])

            results[-1][2] = kpi
            results[-1][1] = score

            dist = []
            path = []
            for line in [line[:-1] for line in lines[3:3+nb_trav]]:
                line = line.split(";")
                dist.append(float(line[0]))  # 0 if not used
                path.append([int(x) for x in line[1].split(",")])  # -1 if not used

            results[-1][3] = list(zip(dist, path))

            results[-1].append(int(lines[0]))

    time2 = time.time()
    print(f'Improvement executions took {(time2-time1)*1000.0:.3f} ms\n')

    return results


def print_optimized(local_data, results, results_before, kpi_names, algo):
    digit_seed = 1+int(math.log10(max([exe[0] for exe in results])))
    digit_score = 1+int(math.log10(max([exe[1] for exe in results_before])))+3
    digit_name = max([len(x["name"]) for x in local_data["traveler"]])
    digit_kpi = max([len(x) for x in kpi_names])

    ratio = len(results)/len(results_before)*100
    print(f"{len(results)} travel(s) optimized with {algo} ({ratio}%) :")

    for seed, score, kpi_values, travel_list, id_exe in results:
        ratio = 100-score/results_before[id_exe][1]*100
        print(f"- Generation {id_exe}, seed {seed:{digit_seed}d} :")
        print(f"    Old score : {results_before[id_exe][1]:{digit_score}.2f}")
        print(f"    New score : {score:{digit_score}.2f} (+{ratio:.1f}%)")
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
