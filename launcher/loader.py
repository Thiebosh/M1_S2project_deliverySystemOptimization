import re
from numba import njit
import time
import numpy as np

import parse
from Arc import Arc


def load_data(file_path):
    travel_lines, peak_lines = read_file(file_path)

    # intialize
    nb_traveler = len(travel_lines)
    nb_peak = len(peak_lines) + sum([x.count(" - ") for x in peak_lines])

    local_data = {"traveler": [], "peak": []}
    to_compute_data = {"traveler": [], "peak": [], "arc": []}

    travel_parser = parse.traveler_line_parser()
    origin_parser = parse.origin_line_parser()
    dest_parser = parse.dest_line_parser()

    list_travelers(travel_parser, travel_lines, local_data, to_compute_data, nb_peak)
    list_peaks_arcs(origin_parser, dest_parser, peak_lines, local_data, to_compute_data, nb_peak)

    compute_arcs(local_data, to_compute_data, nb_traveler, nb_peak)

    return local_data, to_compute_data


def read_file(file_path):
    try:
        with open(file_path) as file:
            all_lines = [line for line in file.readlines()]

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

    except Exception as e:
        print(f"Data acquisition error : {e}")
        exit()

    return travel_lines, peak_lines


def list_travelers(parser, travel_lines, local_data, to_compute_data, nb_peak):
    for count, line in enumerate(travel_lines):
        name, x, y, speed, qty = parse.apply_traveler_parser(parser, line)

        local_data["traveler"].append({"name": name, "x": x, "y": y})

        arc = [Arc(x, y) for _ in range(nb_peak)]
        to_compute_data["traveler"].append({"arc": arc, "speed": speed, "qty": qty})


def list_peaks_arcs(parser, destin_parser, peak_lines, local_data, to_compute_data, nb_peak):
    for count, line in enumerate(peak_lines):
        peaks = line.split(" - ")
        origin = peaks[0]
        dests = peaks[1:] if type(peaks[1:]) is list else [peaks[1:]]

        name, x, y = parse.apply_origin_parser(parser, origin)

        local_data["peak"].append({"name": name, "x": x, "y": y})

        origin_id = len(to_compute_data["peak"])
        to_compute_data["peak"].append({"origin": 1, "link": [], "maxCost": 0})

        arc_line = [Arc(x, y) for _ in range(nb_peak)]
        to_compute_data["arc"].append(arc_line)

        for p_count, peak in enumerate(dests):
            list_dests(destin_parser, local_data, to_compute_data, count, p_count, peak, origin_id, nb_peak)


def list_dests(parser, local_data, to_compute_data, count, p_count, peak, origin_id, nb_peak):
    name, x, y, qty, max_cost = parse.apply_dest_parser(parser, peak)

    local_data["peak"].append({"name": name, "x": x, "y": y})

    to_compute_data["peak"][origin_id]["link"].append(len(to_compute_data["peak"]))
    to_compute_data["peak"].append({"origin": 0, "link": origin_id, "qty": qty, "maxCost": max_cost})

    arc_line = [Arc(x, y) for _ in range(nb_peak)]
    to_compute_data["arc"].append(arc_line)


def compute_arcs(local_data, to_compute_data, nb_traveler, nb_peak):
    for count, peak in enumerate(local_data["peak"]):
        for i in range(nb_traveler):
            arc = to_compute_data["traveler"][i]["arc"][count]
            dist = arc.set_peakDest(peak["x"], peak["y"]).compute_distance()
            to_compute_data["traveler"][i]["arc"][count] = dist

        for i in range(nb_peak):
            arc = to_compute_data["arc"][i][count]
            dist = arc.set_peakDest(peak["x"], peak["y"]).compute_distance()
            to_compute_data["arc"][i][count] = dist
