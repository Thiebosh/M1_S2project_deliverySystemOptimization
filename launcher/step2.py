from defines import TMP_FILE, TMP2_FILE
from subprocess import run


def path_fusion(distance_matrix, results, exe_path):
    file_path = exe_path[:exe_path.rfind("\\")]+TMP_FILE
    file2_path = exe_path[:exe_path.rfind("\\")]+TMP2_FILE

    smooth_paths = []
    for path in [exe[-1] for exe in results]:
        smooth_paths.append([x[1] for x in path if x[1][0] != -1])
        # smooth_paths => tableau de chemins => tableau de tableau d'ids

        if len(smooth_paths[-1]) != 1:  # plus d'un chemin : doit les assembler
            smooth_paths[-1] = assemble_travs(exe_path, file_path, file2_path,
                                             distance_matrix, smooth_paths[-1])

    data = "\n".join([str(path)[1:-1] for path in smooth_paths])
    open(file2_path, "w").write(data)
    # fusionned = run([exe_path, file_path, file2_path], capture_output=True, text=True)
    # print(fusionned)
    exit()

    return ""  # fusionned


def assemble_travs(exe_path, file_path, file2_path, distance_matrix, travs_paths):
    size = len(travs_paths)
    matrix = [[[0]*3 for _ in range(size)] for _ in range(size)]
    
    for id_A in range(size):
        beginA = travs_paths[id_A][0]
        endA = travs_paths[id_A][-1]

        for id_B in range(size):
            if id_A == id_B:
                continue

            beginB = travs_paths[id_B][0]
            endB = travs_paths[id_B][-1]

            matrix[id_A][id_B][0] = distance_matrix[beginA][beginB]
            matrix[id_A][id_B][1] = distance_matrix[endB][beginA]
            matrix[id_A][id_B][2] = distance_matrix[beginB][endB]

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
