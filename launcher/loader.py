import re

import parse
from Arc import Arc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from dashboard import synchronize

def load_data(file_path):
    travel_lines, peak_lines = read_file(file_path)
    # intialize
    nb_traveler = len(travel_lines)
    nb_peak = len(peak_lines) + sum([x.count(" - ") for x in peak_lines])
    # pre allocate everything in the fastest way, without memory share
    ids = {"local_peak": 0, "compute_peak": 0, "compute_arc": 0}
    local_data = {"traveler": [{"name": '', "x": 0.0, "y": 0.0} for _ in range(nb_traveler)],
                  "peak":     [{"name": '', "x": 0.0, "y": 0.0} for _ in range(nb_peak)]}
    compute_data = {"traveler": [{"arc": [Arc()]*nb_peak, "speed": 0.0, "qty": 0}   for _ in range(nb_traveler)],
                    "peak":     [{"origin": 0, "link": 0, "qty": 1, "maxCost": 0.0} for _ in range(nb_peak)],
                    "arc":      [[Arc()]*nb_peak for _ in range(nb_peak)]}
    

    list_travelers(travel_lines, local_data, compute_data, nb_peak)
    list_peaks_arcs(peak_lines, local_data, compute_data, nb_peak, ids)

    compute_arcs(local_data, compute_data, nb_traveler, nb_peak)
    return local_data, compute_data


def read_file(file_path):
    try:
        all_lines = synchronize.get_inputs().splitlines()
        if all_lines[-1][-1] != "\n":
            all_lines[-1] += "\n"
        all_lines.append("\n")  # delimit last data block

        last = -1
        data_lines = []
        for id in [id for id, line in enumerate(all_lines) if re.match(r"^\s*$", line)]:  # empty_lines : only spaces or \t, \r, \n
            if id > last and id-1 != last:
                data_lines.append((last+1, id))
            last = id

        # throw headers lines
        travel_lines = all_lines[data_lines[0][0]+1:data_lines[0][1]]
        peak_lines = all_lines[data_lines[1][0]+1:data_lines[1][1]]
        

        return travel_lines, peak_lines

    except Exception as e:  
        print(f"Data acquisition error : {e}")
        exit()

    


def list_travelers(travel_lines, local_data, compute_data, nb_peak):
    for count, line in enumerate(travel_lines):
        name, x, y, speed, qty = parse.traveler_line(line)

        local_data["traveler"][count]["name"] = name
        local_data["traveler"][count]["x"] = x
        local_data["traveler"][count]["y"] = y

        compute_data["traveler"][count]["speed"] = speed
        compute_data["traveler"][count]["qty"] = qty

        for i in range(nb_peak):
            compute_data["traveler"][count]["arc"][i].set_peakInit(x, y)


def list_peaks_arcs(peak_lines, local_data, compute_data, nb_peak, ids):
    for count, line in enumerate(peak_lines):
        peaks = line.split(" - ")
        origin = peaks[0]
        dests = peaks[1:] if type(peaks[1:]) is list else [peaks[1:]]

        name, x, y = parse.origin_line(origin)

        local_data["peak"][ids["local_peak"]]["name"] = name
        local_data["peak"][ids["local_peak"]]["x"] = x
        local_data["peak"][ids["local_peak"]]["y"] = y
        ids["local_peak"] += 1

        origin_id = ids["compute_peak"]
        compute_data["peak"][ids["compute_peak"]]["origin"] = 1
        compute_data["peak"][ids["compute_peak"]]["link"] = []
        del compute_data["peak"][ids["compute_peak"]]["qty"]
        ids["compute_peak"] += 1

        for i in range(nb_peak):
            compute_data["arc"][ids["compute_arc"]][i].set_peakInit(x, y)
        ids["compute_arc"] += 1

        for p_count, peak in enumerate(dests):
            list_dests(local_data, compute_data, count, p_count, peak, origin_id, nb_peak, ids)


def list_dests(local_data, compute_data, count, p_count, peak, origin_id, nb_peak, ids):
    name, x, y, qty, max_cost = parse.dest_line(peak)

    local_data["peak"][ids["local_peak"]]["name"] = name
    local_data["peak"][ids["local_peak"]]["x"] = x
    local_data["peak"][ids["local_peak"]]["y"] = y
    ids["local_peak"] += 1

    compute_data["peak"][origin_id]["link"].append(ids["compute_peak"])
    compute_data["peak"][ids["compute_peak"]]["link"] = origin_id
    compute_data["peak"][ids["compute_peak"]]["qty"] = qty
    compute_data["peak"][ids["compute_peak"]]["maxCost"] = max_cost
    ids["compute_peak"] += 1

    for i in range(nb_peak):
        compute_data["arc"][ids["compute_arc"]][i].set_peakInit(x, y)
    ids["compute_arc"] += 1


def compute_arcs(local_data, compute_data, nb_traveler, nb_peak):
    for count, peak in enumerate(local_data["peak"]):
        for i in range(nb_traveler):
            compute_data["traveler"][i]["arc"][count] = compute_data["traveler"][i]["arc"][count]\
                                                        .set_peakDest(peak["x"], peak["y"])\
                                                        .compute_distance()

        for i in range(nb_peak):
            compute_data["arc"][i][count] = compute_data["arc"][i][count]\
                                            .set_peakDest(peak["x"], peak["y"])\
                                            .compute_distance()
