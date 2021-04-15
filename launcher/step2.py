from defines import TMP_FILE, TMP2_FILE
from subprocess import run


def path_fusion(distances, results, exe_path):
    file_path = exe_path[:exe_path.rfind("\\")]+TMP_FILE
    file2_path = exe_path[:exe_path.rfind("\\")]+TMP2_FILE

    smooth_paths = []
    for path in [exe[-1] for exe in results]:
        smooth_paths.append([x[1] for x in path if x[1][0] != -1])
        # smooth_paths => tableau de chemins => tableau de tableau d'ids

        if len(smooth_paths[-1]) != 1:  # plus d'un chemin : doit les assembler
            smooth_paths[-1] = assemble_travs(exe_path, file_path, file2_path,
                                              distances, smooth_paths[-1])

    data = "\n".join([str(path)[1:-1] for path in smooth_paths])
    open(file2_path, "w").write(data)
    # fusionned = run([exe_path, file_path, file2_path], capture_output=True, text=True)
    # print(fusionned)
    exit()

    return ""  # fusionned


def assemble_travs(exe_path, file_path, file2_path, distances, travs_paths):
    size = len(travs_paths)
    matrix = [
                [
                    [
                        distances[travs_paths[id_A][-1]][travs_paths[id_B][0]],
                        distances[travs_paths[id_A][-1]][travs_paths[id_B][-1]]
                    ]
                    if id_A != id_B
                    else [0]*2
                    for id_B in range(size)
                ]
                for id_A in range(size)
             ]

    open(file2_path, "w").write(str(matrix))
    # optimal = run([exe_path, file_path, file2_path], capture_output=True, text=True)
    # print(optimal)

    optimal = "0,-1,2"

    assembled = []
    for id in optimal.split(","):
        reverse = id[0] == '-'
        id = abs(int(id))

        if reverse:
            travs_paths[id].reverse()

        assembled += travs_paths[id]

    return assembled
