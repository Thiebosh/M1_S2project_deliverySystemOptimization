import math


def print_results(local_data, results):
    # greater nbs of digits
    # higher_score = max([exe[1] for exe in results])
    # max_digits_score = 1+int(math.log10(higher_score))

    higher_dist = max([value for sublist in [([travels[0] for travels in exe[-1]]) for exe in results] for value in sublist])
    max_digits_dist = 1+int(math.log10(higher_dist))

    max_digits_name = max([len(x["name"]) for x in local_data["traveler"]])

    print(f"{len(results)} distinc(s) peaks travel(s) order(s) :")

    for seed, score, metrics, travel_list in results:
        print(f"- seed {seed} : score of {score}")
        print(f"\tmetrics : {metrics}")

        for id, (dist, travel) in enumerate(travel_list):
            travel = [local_data["peak"][x]["name"] for x in travel]

            a = local_data['traveler'][id]['name']
            b = f"{dist:{max_digits_dist+3}.2f}"
            c = "with "+" -> ".join(travel) if dist != 0 else ""
            print(f"\t\t{a:{max_digits_name}s} : {b}km {c}")

        print()


def print_fusionned(path):
    pass


def format_csv(local_data, results):
    path_data = [["id",
                  "seed",
                  "score",
                  "variance des variances des distances",
                  "variance des médianes des distances",
                  "variance des distances totales des trajets",
                  "total_distance",  # no return to origin
                  "paths",
                  "img"]]

    for id_travel, (seed, score, metrics, travels) in enumerate(results):

        paths = ""
        for id_path, (_, path) in enumerate(travels):
            name = local_data['traveler'][id_path]['name']
            path = [local_data["peak"][x]["name"] if x != -1 else "none" for x in path]
            paths += f"{name} : {', '.join(path)}\n"

        line = [str(id_travel),
                str(seed),
                str(score).replace(".", ","),
                str(metrics[0]).replace(".", ","),
                str(metrics[1]).replace(".", ","),
                str(metrics[2]).replace(".", ","),
                str(metrics[3]).replace(".", ","),
                '"'+paths[:-1]+'"']

        path_data.append(line)

    cities_data = [["city_name", "lat", "long"]]

    for city in local_data["peak"]:
        cities_data.append([city['name'], str(city['y']), str(city['x'])])

    return path_data, cities_data
