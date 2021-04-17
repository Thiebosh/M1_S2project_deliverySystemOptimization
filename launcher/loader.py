import re
import math
import numpy as np
from numba import njit
from sys import maxsize
import parse

np.set_printoptions(formatter={'float': "{:.2f}".format}, threshold=maxsize)


def load_data(file_content):
    vehicule_lines, travel_lines, peak_lines = acquire_data(file_content)

    # intialize
    nb_traveler = len(travel_lines)
    nb_peak = len(peak_lines) + sum([x.count(" - ") for x in peak_lines])

    # apply vehicules to travelers
    vehicules = {x[0]: ','+x[1]+','+x[2] for x in [line.split(',') for line in vehicule_lines]}
    for i in range(nb_traveler):
        trav = travel_lines[i]
        travel_lines[i] += vehicules[trav[trav.rfind(',')+1:]]

    # pre allocate everything in the fastest way, without memory share
    ids = {"local_peak": 0, "compute_peak": 0, "compute_arc": 0}
    local_data = {"traveler": [{"name": '', "x": 0.0, "y": 0.0, "vehicule": ""} for _ in range(nb_traveler)],
                  "peak":     [{"name": '', "x": 0.0, "y": 0.0, "origin": False} for _ in range(nb_peak)]}
    compute_data = {"peak":     [{"origin": 0, "link": 0, "qty": 1} for _ in range(nb_peak)],
                    # matrix of lat1, long1, lat2, long2
                    "arc":      np.array([np.empty((nb_peak, nb_peak), dtype='float32'), \
                                          np.empty((nb_peak, nb_peak), dtype='float32'), \
                                          np.empty((nb_peak, nb_peak), dtype='float32'), \
                                          np.empty((nb_peak, nb_peak), dtype='float32')]),
                    "traveler": [{"speed": 0.0,
                                  "qty": 0,
                                  # vector of lat1, long1, lat2, long2
                                  "arc": np.array([np.empty((nb_peak), dtype='float32'), \
                                                   np.empty((nb_peak), dtype='float32'), \
                                                   np.empty((nb_peak), dtype='float32'), \
                                                   np.empty((nb_peak), dtype='float32')])}
                                 for _ in range(nb_traveler)]}

    list_travelers(travel_lines, local_data, compute_data, nb_peak)
    list_peaks_arcs(peak_lines, local_data, compute_data, nb_peak, nb_traveler, ids)

    for i in range(nb_traveler):
        compute_data["traveler"][i]["arc"] = compute_traveler(compute_data["traveler"][i]["arc"])
    compute_data["arc"] = compute_arcs(compute_data["arc"])

    return local_data, compute_data


def acquire_data(file_content):
    try:
        all_lines = file_content.splitlines()

        if all_lines[-1][-1] != "\n":
            all_lines[-1] += "\n"
        all_lines.append("\n")  # delimit last data block

        last = -1
        data_lines = []
        reg = re.compile(r"^\s*$")  # empty_lines : only spaces or \t, \r, \n
        for id in [id for id, line in enumerate(all_lines) if reg.match(line)]:
            if id > last and id-1 != last:
                data_lines.append((last+1, id))
            last = id
        # throw headers lines
        vehicule_lines = all_lines[data_lines[0][0]+1:data_lines[0][1]]
        travel_lines = all_lines[data_lines[1][0]+1:data_lines[1][1]]
        peak_lines = all_lines[data_lines[2][0]+1:data_lines[2][1]]

        return vehicule_lines, travel_lines, peak_lines

    except Exception as e:
        print(f"Data acquisition error : {e}")
        exit()


def list_travelers(travel_lines, local_data, compute_data, nb_peak):
    for count, line in enumerate(travel_lines):
        name, x, y, vehicule, speed, qty = parse.traveler_line(line)

        local_data["traveler"][count]["name"] = name
        local_data["traveler"][count]["x"] = x
        local_data["traveler"][count]["y"] = y
        local_data["traveler"][count]["vehicule"] = vehicule

        compute_data["traveler"][count]["speed"] = speed
        compute_data["traveler"][count]["qty"] = qty

        for i in range(nb_peak):
            compute_data["traveler"][count]["arc"][0][i] = x
            compute_data["traveler"][count]["arc"][1][i] = y


def list_peaks_arcs(peak_lines, local_data, compute_data, nb_peak, nb_trav, ids):
    for count, line in enumerate(peak_lines):
        peaks = line.split(" - ")
        origin = peaks[0]
        dests = peaks[1:] if type(peaks[1:]) is list else [peaks[1:]]

        name, x, y = parse.origin_line(origin)

        dest_id = ids["local_peak"]
        ids["local_peak"] += 1
        local_data["peak"][dest_id]["name"] = name
        local_data["peak"][dest_id]["x"] = x
        local_data["peak"][dest_id]["y"] = y
        local_data["peak"][dest_id]["origin"] = True

        # attribue toutes les destinations pour le sommet origine
        for i in range(nb_peak):
            compute_data["arc"][2][i][dest_id] = x
            compute_data["arc"][3][i][dest_id] = y
        for i in range(nb_trav):
            compute_data["traveler"][i]["arc"][2][dest_id] = x
            compute_data["traveler"][i]["arc"][3][dest_id] = y

        origin_id = ids["compute_peak"]
        ids["compute_peak"] += 1
        compute_data["peak"][origin_id]["origin"] = 1
        compute_data["peak"][origin_id]["link"] = []
        del compute_data["peak"][origin_id]["qty"]

        init_id = ids["compute_arc"]
        ids["compute_arc"] += 1
        for i in range(nb_peak):
            compute_data["arc"][0][init_id][i] = x
            compute_data["arc"][1][init_id][i] = y

        for p_count, peak in enumerate(dests):
            list_dests(local_data, compute_data, count, p_count, peak, origin_id, nb_peak, nb_trav, ids)


def list_dests(local_data, compute_data, count, p_count, peak, origin_id, nb_peak, nb_trav, ids):
    name, x, y, qty = parse.dest_line(peak)

    dest_id = ids["local_peak"]
    ids["local_peak"] += 1
    local_data["peak"][dest_id]["name"] = name
    local_data["peak"][dest_id]["x"] = x
    local_data["peak"][dest_id]["y"] = y

    # attribue toutes les destinations pour le sommet destination
    for i in range(nb_peak):
        compute_data["arc"][2][i][dest_id] = x
        compute_data["arc"][3][i][dest_id] = y
    for i in range(nb_trav):
        compute_data["traveler"][i]["arc"][2][dest_id] = x
        compute_data["traveler"][i]["arc"][3][dest_id] = y

    dest_id = ids["compute_peak"]
    ids["compute_peak"] += 1
    compute_data["peak"][origin_id]["link"].append(dest_id)
    compute_data["peak"][dest_id]["link"] = origin_id
    compute_data["peak"][dest_id]["qty"] = qty

    init_id = ids["compute_arc"]
    ids["compute_arc"] += 1
    for i in range(nb_peak):
        compute_data["arc"][0][init_id][i] = x
        compute_data["arc"][1][init_id][i] = y


@njit(nogil=True, fastmath=True)
def distance(const, demiconst, lat1, long1, lat2, long2):
    phi1 = lat1*const
    phi2 = lat2*const

    deltaPhi = math.sin((lat2 - lat1)*demiconst)
    deltaLambda = math.sin((long2 - long1)*demiconst)

    a = deltaPhi * deltaPhi + math.cos(phi1) * math.cos(phi2) * deltaLambda * deltaLambda

    return 12742 * math.atan2(math.sqrt(a), math.sqrt(1 - a))  # earth diameter


@njit(nogil=True, fastmath=True)
def compute_arcs(datas):
    const = math.pi/180
    demiconst = const/2
    result = np.empty_like(datas[0])
    for i in range(len(datas[0])):
        for j in range(len(datas[0])):
            result[i][j] = distance(const, demiconst, datas[0][i][j], datas[1][i][j], datas[2][i][j], datas[3][i][j])

    return result


@njit(nogil=True, fastmath=True)
def compute_traveler(datas):
    const = math.pi/180
    demiconst = const/2
    result = np.empty_like(datas[0])
    for i in range(len(datas[0])):
        result[i] = distance(const, demiconst, datas[0][i], datas[1][i], datas[2][i], datas[3][i])

    return result


def compile_loader():
    compute_arcs(np.array([np.empty((1, 1), dtype='float32')]*4))  # compile
    compute_traveler(np.array([np.empty((1), dtype='float32')]*4))  # compile
    distance(0, 0, 0, 0, 0, 0)
