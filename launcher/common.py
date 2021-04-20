import pandas as pd
pd.set_option('display.max_rows', None)

def origins_to_dests(to_compute, path, algo, id_exe=""):
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
            assoc.append((algo, id_origin, id_dest, str(round(dist, 2)).replace(".", ","), id_exe))

    return assoc


def format_csv(local_data, to_compute, results_gen, results_opti):
    algos = ["LocalSearch", "SimulatedAnnealing"]

    vertices_df = pd.DataFrame(
        [[id,
          vertice["name"],
          f"{vertice['y']},{vertice['x']}",
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

    optimized = [[[name, path[-1], id_client] 
                 for id_client in client_df["client_id"] 
                 for path in opti]
                 for name, opti in zip(algos, results_opti)]
    optimized = [value for sublist in optimized for value in sublist]  # unpack

    orders_df = pd.DataFrame(
        [["Generated", id_exe, id_client] for id_client in client_df["client_id"] for id_exe in range(len(results_gen))] + optimized,
        columns=["calculation_type", "generation_id", "client_id"]
    )

    orders_df = pd.merge(orders_df, dep_to_dest_df, on="client_id")

    # generate assoc origin - dest and evaluate dist
    paths_per_exe = [([origins_to_dests(to_compute, travels[1], "Generated", id_exe)
                      for travels in exe[-1]])
                     for id_exe, exe in enumerate(results_gen)]
    paths_per_opti = [[([origins_to_dests(to_compute, travels[1], name, exe[-1])
                        for travels in exe[-2]])
                       for exe in opti]
                      for name, opti in zip(algos, results_opti)]
    paths_per_exe += [value for sublist in paths_per_opti for value in sublist]  # unpack

    # generate lines
    paths_per_exe = [[[[[algo, id_exe, id_deposit, id_client, id_trav, distance] 
                       for algo, id_client, id_deposit, distance, id_exe in trav_data]
                      for id_trav, trav_data in enumerate(paths)]]
                     for paths in paths_per_exe]
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

    ref = merge_df[["calculation_type", "generation_id", "trav_id"]].drop_duplicates().to_numpy()
    execution_tab = [(gen,
                      id_exe,
                      id_trav,
                      " -> ".join([local_data["peak"][x]["name"] if x != -1 else "none" for x in results_gen[id_exe][-1][id_trav][1]]),
                      str(round(results_gen[id_exe][-1][id_trav][0], 2)).replace(".", ","),
                      str(round(results_gen[id_exe][2][0], 2)).replace(".", ","),
                      str(round(results_gen[id_exe][1], 2)).replace(".", ","),
                      results_gen[id_exe][0])
                     for gen, id_exe, id_trav
                     in ref
                     if gen == "Generated"]

    tmp = merge_df[["calculation_type", "generation_id"]].drop_duplicates().to_numpy()
    for name, opti in zip(algos, results_opti):
        convertor = {id_exe: id for id, id_exe in enumerate([line[1] for line in tmp if line[0] == name])}

        execution_tab += [(gen,
                           id_exe,
                           id_trav,
                           " -> ".join([local_data["peak"][x]["name"] if x != -1 else "none" for x in opti[convertor[id_exe]][3][id_trav][1]]),
                           str(round(opti[convertor[id_exe]][3][id_trav][0], 2)).replace(".", ","),
                           str(round(opti[convertor[id_exe]][2][0], 2)).replace(".", ","),
                           str(round(opti[convertor[id_exe]][1], 2)).replace(".", ","),
                           opti[convertor[id_exe]][0])
                          for gen, id_exe, id_trav
                          in ref
                          if gen == name]

    execution_df = pd.DataFrame(
        [[*data, "NULL"] for data in execution_tab],
        columns=["calculation_type",
                 "generation_id",
                 "traveler_id",
                 "trav_path",
                 "trav_distance",
                 "total_distance",
                 "total_score",
                 "seed",
                 "gif"]
    )

    vertices_df = vertices_df.to_csv(index=False, sep=";")
    vertices_df = [line.split(";") for line in vertices_df.split("\r\n")]

    orders_df["generation_id"] += 1
    orders_df = orders_df.to_csv(index=False, sep=";")
    orders_df = [line.split(";") for line in orders_df.split("\r\n")]

    execution_df["generation_id"] += 1
    execution_df = execution_df.to_csv(index=False, sep=";")
    execution_df = [line.split(";") for line in execution_df.split("\r\n")]

    return vertices_df, orders_df, execution_df
