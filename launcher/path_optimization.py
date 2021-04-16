from subprocess import Popen, PIPE
import asyncio
import time


async def path_optimization(exe_path, file_path, nb_process, generated_paths):
    running_procs = [Popen([exe_path, str(id), generated_paths["seed"],
                            file_path, generated_paths["path"]],
                     stdout=PIPE, stderr=PIPE, text=True)
                     for id in range(nb_process)]

    # results = []
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

        # seed = lines[1]
        # kpi = lines[2]
        # paths = [line[:-1] for line in lines[3:3+nb_trav]]

        # preprocess results rather than sleep
        # results = make_unique(seed, kpi, kpi_weights, paths, results)

    time2 = time.time()
    print(f'Improvement executions took {(time2-time1)*1000.0:.3f} ms\n')

    return
