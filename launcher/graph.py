import matplotlib.pyplot as plt
import imageio
import os
import geopandas
import random
from geopip import search
from copy import deepcopy
from threading import Thread
import queue
import time

from defines import MAPS_FOLDER, RESULT_FOLDER
import concurrent.futures
 
def plot_path(countries_map, cities, results, idGraph, local_data, save_gif, path, result_name, files):
    fig = plt.figure()
    axe = fig.gca()
    # extract couple [x, y]
    x, y = zip(*cities)
    # print background map
    for country in countries_map:
            country.plot(ax=axe)

    # print peaks
    axe.scatter(x, y, c="black", s=1)
    for i in range(len(list(dict.fromkeys(results[0][1])))):
        coef = (axe.get_xlim()[1]-axe.get_xlim()[0])/15
        axe.text(x[i]+random.choice([-0.1,0.1])*coef, y[i]+random.choice([-0.1,0.1])*coef, local_data["peak"][i]["name"], fontsize='xx-small')

    axe.title.set_text(f"{str(results[idGraph][0])}km\n{str([x+1 for x in results[idGraph][1]])[1:-1]}")

    # print traveler origin
    travel = local_data["traveler"][0]
    axe.scatter(travel["x"], travel["y"], c="red",s=1)

    # print travel from origin to first peak
    city = [travel["x"], travel["y"]]
    nexCity = cities[results[idGraph][1][0]]

    arr2 = axe.arrow((nexCity[0]-city[0])*0.05+city[0], (nexCity[1]-city[1])*0.05+city[1], 0.9*(nexCity[0]-city[0]), 0.9*(nexCity[1]-city[1]),
                        length_includes_head=True, color="red", width=0.001,head_width=0.5,head_length=0.5, alpha=0.8)
    axe.legend([arr2,], [local_data["traveler"][0]["name"],], bbox_to_anchor=(0.5, -0.1), fontsize='small')

    # gif img
    fileNames = []
    if(save_gif):
        name = f"{idGraph}_init.png"
        fig.savefig(name)
        fileNames.append(name)

    # travel between peaks
    for idCity, city in enumerate(results[idGraph][1][:-1]):
        city = cities[city]
        nexCity = cities[results[idGraph][1][idCity+1]]
        axe.arrow((nexCity[0]-city[0])*0.05+city[0], (nexCity[1]-city[1])*0.05+city[1], 0.9*(nexCity[0]-city[0]), 0.9*(nexCity[1]-city[1]),
                        length_includes_head=True, color="red", width=0.001,head_width=0.5,head_length=0.5, alpha=0.8)

        # gif img
        if(save_gif):
            name = f"{idGraph}_{idCity}.png"
            fig.savefig(name)
            fileNames.append(name)

    # assemble gif
    if(save_gif):
        print(path)
        with imageio.get_writer(f"{path}\\results\\{result_name}_{idGraph}.gif", mode='I') as gifFile:
            for fileName in fileNames:
                image = imageio.imread(fileName)
                gifFile.append_data(image)
        files.append(f"{path}\\results\\{result_name}_{idGraph}.gif")

        for fileName in fileNames:
            os.remove(fileName)

    fig.savefig(f"{path}\\results\\{result_name}_{idGraph}.png", dpi=500)
    files.append(f"{path}\\results\\{result_name}_{idGraph}.png")
    return files



def make_graph(path, local_data, results, result_name, save_gif):
    plt.switch_backend('agg')
    plot_countries = []
    countries_map = []

    cities = [(peak["x"], peak["y"]) for peak in local_data["peak"]]

    # get countries to plot
    for city in cities:
        res = search(city[0], city[1])
        if res and not res["ISO3"] in plot_countries:
            plot_countries.append(res["ISO3"])

    if len(plot_countries) > 5 or len(plot_countries) == 0:
        plot_countries = ["WORLD"]

    for country in plot_countries:
        countries_map.append(geopandas.read_file(path+MAPS_FOLDER+"\\"+country+".shp"))

    # prepare graphs
    nb_graph = min(50, len(results))

    files = []

    que = queue.Queue()
    threads = []

    for idGraph in range(nb_graph):
            t = Thread(target=plot_path, args=(countries_map, cities, results, idGraph, local_data, save_gif, path, result_name, files))
            threads.append(t)
            t.start()
    
    for thread in threads:
        thread.join()

    # while not que.empty():
    #     print("zebi")
    #     print(que.get())
    #     files = files + que.get()

    # print(files)
    return files
