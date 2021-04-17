import math
import pandas as pd


def print_generated(local_data, results, kpi_names):
    # higher_dist = max([value for sublist in [([travels[0] for travels in exe[-1]]) for exe in results] for value in sublist])

    digit_seed = 1+int(math.log10(max([exe[0] for exe in results])))
    digit_score = 1+int(math.log10(max([exe[1] for exe in results])))
    digit_name = max([len(x["name"]) for x in local_data["traveler"]])
    digit_kpi = max([len(x) for x in kpi_names])

    print(f"{len(results)} distinc(s) peaks travel(s) order(s) :")

    for seed, score, kpi_values, travel_list in results:
        print(f"- seed {seed:{digit_seed}d} : score of {score:{digit_score}f}")
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


def print_optimized(path):
    pass  # print only if better. Else, print "not better"


def print_fusionned(path):
    pass


def origins_to_dests(to_compute, path):
    if path == [-1]:
        return []

    assoc = []
    origins = [(index, id) for index, id in enumerate(path)
               if to_compute["peak"][id]["origin"]]
    for index_origin, id_origin in origins:
        dests = [(index+index_origin+1, id) for index, id in enumerate(path[index_origin+1:])
                 if id in to_compute["peak"][id_origin]["link"]]
        for index_dest, id_dest in dests:
            dist = sum([to_compute["arc"][id1][id2] for id1 in path[index_origin:index_dest] 
                                                    for id2 in path[index_origin+1:index_dest+1]])
            assoc.append((id_origin, id_dest, str(round(dist, 2)).replace(".", ",")))

    return assoc


def format_csv(local_data, to_compute, results_gen, results_opti, result_fusion):
    vertices_df = pd.DataFrame(
        [[id,
          vertice["name"],
          f"{vertice['x']},{vertice['y']}",
          "deposit" if vertice["origin"] else "client"]
         for id, vertice in enumerate(local_data["peak"])],
        columns=["id",
                 "name",
                 "lat_long",
                 "type"]
    )

    deposit_df = vertices_df.loc[vertices_df['type'] == "deposit"] \
                            [["id", "name", "lat_long"]] \
                            .rename(columns={"id": "deposit_id",
                                             "name": "deposit_name",
                                             "lat_long": "deposit_lat_long"})

    client_df = pd.DataFrame(
        [[id,
          vertice["name"],
          to_compute["peak"][id]["link"]]
         for id, vertice in enumerate(local_data["peak"])
         if not vertice["origin"]],
        columns=["client_id",
                 "client_name",
                 "deposit_id"]
    )
    client_df = pd.merge(client_df, vertices_df[["id", "lat_long"]], left_on="client_id", right_on="id")\
                  .rename(columns={"lat_long": "client_lat_long"})

    dep_to_dest_df = pd.merge(client_df, deposit_df, on="deposit_id")

    orders_df = pd.DataFrame(
        [["generated", id_exe, id_client] for id_client in client_df["client_id"] for id_exe in range(len(results_gen))] +
        [["optimized", id_exe, id_client] for id_client in client_df["client_id"] for id_exe, path in enumerate(results_opti) if path != -1],
        columns=["calculation_type", "generation_id", "client_id"]
    )

    orders_df = pd.merge(orders_df, dep_to_dest_df, on="client_id")

    # print(orders_df)

    # generate assoc origin - dest and evaluate dist
    paths_per_exe = [([origins_to_dests(to_compute, travels[1]) for travels in exe[-1]]) for exe in results_gen]
    # generate lines
    paths_per_exe = [[[[["generated", id_exe, id_deposit, id_client, id_trav, distance] 
                       for id_client, id_deposit, distance in trav_data]
                      for id_trav, trav_data in enumerate(paths)]]
                     for id_exe, paths in enumerate(paths_per_exe)]
    # extract lines
    paths_per_exe = [value for sublist in paths_per_exe for value in sublist]
    paths_per_exe = [value for sublist in paths_per_exe for value in sublist]
    paths_per_exe = [value for sublist in paths_per_exe for value in sublist]

    merge_df = pd.DataFrame(
        [line for line in paths_per_exe],
        columns=["calculation_type",
                 "generation_id",
                 "client_id",
                 "deposit_id",
                 "trav_id",
                 "delivery_dist"]
    )

    orders_df = pd.merge(orders_df, merge_df, on=["calculation_type", "generation_id", "client_id", "deposit_id"])

    trav_df = pd.DataFrame(
        [[id,
          trav["name"],
          trav["vehicule"],
          to_compute["traveler"][id]["speed"],
          to_compute["traveler"][id]["qty"]]
         for id, trav in enumerate(local_data["traveler"])],
        columns=["trav_id",
                 "trav_name",
                 "vehicule_name",
                 "vehicule_speed",
                 "vehicule_storage"]
    )

    orders_df = pd.merge(orders_df, trav_df, on=["trav_id"])

    orders_df = orders_df[["calculation_type",
                           "generation_id",
                           "trav_id",
                           "delivery_dist",
                           "deposit_id",
                           "client_id",
                           "client_name",
                           "client_lat_long",
                           "deposit_name",
                           "deposit_lat_long",
                           "trav_name",
                           "vehicule_name",
                           "vehicule_speed",
                           "vehicule_storage"]]

    return vertices_df.to_csv(index=False, sep=";"), \
           orders_df.to_csv(index=False, sep=";")
    # exit()


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
