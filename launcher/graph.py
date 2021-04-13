import matplotlib.pyplot as plt
import imageio
import os
import geopandas
import random
from geopip import search
from threading import Thread, Lock
import time
from pygifsicle import optimize

from defines import MAPS_FOLDER, RESULT_FOLDER, MAX_GRAPH, MAX_COUNTRIES


def plot_path(link_vertices, background, show_names, countries_map, cities, x, y, x_o, y_o, x_d, y_d, results, idGraph, local_data, peaks, save_gif, fps, path, result_name, files, files_lock):
    fig = plt.figure()
    axe = fig.gca()

    axe.title.set_text(f"{results[2][1]:.1f}km")  # \n{str([x+1 for x in results[3][to:do][1]])[1:-1]}
    axe.axis('off')

    if background:
        for country in countries_map:  # print background map
            country.plot(ax=axe)

    if link_vertices:
        linked = [(id, peak["link"]) for id, peak in enumerate(peaks) if peak["origin"]]
        for origin, dests in linked:
            x1, y1 = cities[origin]
            for dest in dests:
                x2, y2 = cities[dest]
                axe.plot([x1, x2], [y1, y2], zorder=1, linestyle="dashed", c="lightgreen", alpha=0.75)

    axe.scatter(x_o, y_o, zorder=2, marker="s", c="red")  # , s=8
    axe.scatter(x_d, y_d, zorder=2, marker="o", c="green")  # , s=12

    if show_names:
        coef = 0.3*(axe.get_xlim()[1]-axe.get_xlim()[0])/15
        for i in range(len(cities)):
            axe.text(x[i]+coef, y[i]+coef, local_data["peak"][i]["name"], fontsize='x-small', c="black")

    # print travelers origins
    for id, traveler in enumerate(results[-1]):
        color = "blue"
        travel = local_data["traveler"][id]
        axe.scatter(travel["x"], travel["y"], marker="D", c=color)  # , s=8
        if show_names:
            axe.text(travel["x"]+coef, travel["y"]+coef, travel["name"], fontsize='x-small', c=color)

    # end init part here

    filenames = []
    if(save_gif):
        name = f"{idGraph}_-1.png"
        fig.savefig(name)
        filenames.append(name)

    # travel between peaks
    for idTravel, traveler in enumerate(results[-1]):
        color = "blue"

        # print travel from origin to first peak
        travel = local_data["traveler"][idTravel]
        city = [travel["x"], travel["y"]]  # update here
        nextCity = cities[traveler[1][0]]

        deltaX = nextCity[0]-city[0]
        deltaY = nextCity[1]-city[1]

        axe.arrow(deltaX*0.05+city[0], deltaY*0.05+city[1], deltaX*0.9, deltaY*0.9,
                  length_includes_head=True, head_width=0.5, head_length=0.5,
                  width=0.001, color=color, alpha=0.75)

        if(save_gif):
            name = f"{idGraph}_{idTravel}.png"
            fig.savefig(name)
            filenames.append(name)

        for idCity, city in enumerate(traveler[1][:-1]):
            city = cities[city]
            nextCity = cities[traveler[1][idCity+1]]

            deltaX = nextCity[0]-city[0]
            deltaY = nextCity[1]-city[1]

            axe.arrow(deltaX*0.05+city[0], deltaY*0.05+city[1], deltaX*0.9, deltaY*0.9,
                      length_includes_head=True, head_width=0.5, head_length=0.5,
                      width=0.001, color=color, alpha=0.75)

            # gif img
            if(save_gif):
                name = f"{idGraph}_{idTravel}_{idCity}.png"
                fig.savefig(name)
                filenames.append(name)

    # assemble gif
    if(save_gif):
        gifname = path+RESULT_FOLDER+f"\\{result_name}_{idGraph}.gif"

        with files_lock:
            files.append(gifname)

        frames = [imageio.imread(img) for img in filenames]
        for filename in filenames:
            os.remove(filename)

        frames.append(frames[-1])
        frames.append(frames[-1])

        imageio.mimsave(gifname, frames, fps=fps)
        optimize(gifname)

    filename = path+RESULT_FOLDER+f"\\{result_name}_{idGraph}.png"
    with files_lock:
        files.append(filename)
    fig.savefig(filename, dpi=500)


def make_graph(path, local_data, compute_data, results, result_name, show_names, link_vertices, background, save_gif, fps):
    plt.switch_backend('agg')
    plot_countries = []
    countries_map = []

    cities_origin = [(peak["x"], peak["y"], peak["name"]) for peak in local_data["peak"] if peak["origin"]]
    cities_dest = [(peak["x"], peak["y"], peak["name"]) for peak in local_data["peak"] if not peak["origin"]]
    cities = [(peak["x"], peak["y"]) for peak in local_data["peak"]]
    x_o, y_o, _ = zip(*cities_origin)
    x_d, y_d, _ = zip(*cities_dest)
    x, y = zip(*cities)  # extract couples [x, y]

    if background:
        # get countries to plot
        for city in cities:
            res = search(city[0], city[1])
            if res and res["ISO3"] not in plot_countries:
                plot_countries.append(res["ISO3"])
        if len(plot_countries) > MAX_COUNTRIES or len(plot_countries) == 0:
            plot_countries = ["WORLD"]

        for country in plot_countries:
            countries_map.append(geopandas.read_file(path+MAPS_FOLDER+"\\"+country+".shp"))

    # prepare graphs
    nb_graph = min(MAX_GRAPH, len(results))

    files = []
    files_lock = Lock()

    threads = []
    for idGraph in range(nb_graph):
        t = Thread(target=plot_path, args=(link_vertices, background, show_names, countries_map, cities, x, y, x_o, y_o, x_d, y_d, results[idGraph], idGraph, local_data, compute_data["peak"], save_gif, fps, path, result_name, files, files_lock))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    return files
