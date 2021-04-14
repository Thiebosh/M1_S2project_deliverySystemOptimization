import matplotlib.pyplot as plt
import imageio
import os
import geopandas
from geopip import search
from threading import Thread, Lock
from pygifsicle import optimize
import pickle
import io

from defines import MAPS_FOLDER, RESULT_FOLDER, MAX_GRAPH, MAX_COUNTRIES


def plot_path(idThread, fig, results, cities, local_travelers, travel_colors,
              path, result_name, save_gif, fps, g_files, g_files_lock):
    axe = fig.gca()
    axe.title.set_text(f"{results[2][1]}km")  # :.1f

    img_buffers = []
    if(save_gif):
        b = io.BytesIO()
        fig.savefig(b, format='png')
        b.seek(0)  # crucial
        img_buffers.append(b)

    # travel between peaks
    for idTravel, traveler in enumerate(results[-1]):
        # print travel from origin to first peak
        city = [local_travelers[idTravel]["x"], local_travelers[idTravel]["y"]]
        nextCity = cities[traveler[1][0]]

        deltaX = nextCity[0]-city[0]
        deltaY = nextCity[1]-city[1]

        axe.arrow(deltaX*0.05+city[0], deltaY*0.05+city[1], deltaX*0.9, deltaY*0.9,
                  length_includes_head=True, head_width=0.5, head_length=0.5,
                  width=0.001, color=travel_colors, alpha=0.75)

        if(save_gif):
            b = io.BytesIO()
            fig.savefig(b, format='png')
            b.seek(0)  # crucial
            img_buffers.append(b)

        for idCity, city in enumerate(traveler[1][:-1]):
            city = cities[city]
            nextCity = cities[traveler[1][idCity+1]]

            deltaX = nextCity[0]-city[0]
            deltaY = nextCity[1]-city[1]

            axe.arrow(deltaX*0.05+city[0], deltaY*0.05+city[1], deltaX*0.9, deltaY*0.9,
                      length_includes_head=True, head_width=0.5, head_length=0.5,
                      width=0.001, color=travel_colors, alpha=0.75)

            # gif img
            if(save_gif):
                b = io.BytesIO()
                fig.savefig(b, format='png')
                b.seek(0)  # crucial
                img_buffers.append(b)

    # assemble gif
    if(save_gif):
        gifname = path+RESULT_FOLDER+f"\\{result_name}_{idThread}.gif"

        with g_files_lock:
            g_files.append(gifname)

        frames = [imageio.imread(buffer.read()) for buffer in img_buffers]
        frames.append(frames[-1])
        frames.append(frames[-1])

        imageio.mimsave(gifname, frames, fps=fps)
        optimize(gifname)

    else:
        filename = path+RESULT_FOLDER+f"\\{result_name}_{idThread}.png"
        with g_files_lock:
            g_files.append(filename)
        fig.savefig(filename, dpi=500)


def make_graph(path, local_data, compute_data, results, result_name, show_names, link_vertices, background, save_gif, fps):
    plt.switch_backend('agg')

    # prepare graphs
    nb_graph = min(MAX_GRAPH, len(results))

    cities = [(peak["x"], peak["y"]) for peak in local_data["peak"]]
    x, y = zip(*cities)  # extract couples [x, y]

    # plot common part
    fig = plt.figure()
    axe = fig.gca()
    axe.axis('off')

    # step1 : optional background (country maps)
    if background:
        plot_countries = []
        # get countries to plot
        for city in cities:
            res = search(city[0], city[1])
            if res and res["ISO3"] not in plot_countries:
                plot_countries.append(res["ISO3"])

        if len(plot_countries) > MAX_COUNTRIES or len(plot_countries) == 0:
            plot_countries = ["WORLD"]

        for country in plot_countries:  # print background map
            country_map = geopandas.read_file(path+MAPS_FOLDER+"\\"+country+".shp")
            country_map.plot(ax=axe, color="lightgray", zorder=-1)

    # step2 : optional display of link between vertices
    if link_vertices:
        linked = [(id, peak["link"]) for id, peak in enumerate(compute_data["peak"]) if peak["origin"]]
        for origin, dests in linked:
            x1, y1 = cities[origin]
            for dest in dests:
                x2, y2 = cities[dest]
                axe.plot([x1, x2], [y1, y2], zorder=0, linestyle="dashed", c="green", alpha=0.3)

    # step3 : display origins, destinations and travelers origins
    cities_origin = [(peak["x"], peak["y"]) for peak in local_data["peak"] if peak["origin"]]
    cities_dest = [(peak["x"], peak["y"]) for peak in local_data["peak"] if not peak["origin"]]
    x_o, y_o = zip(*cities_origin) # donne direct ?
    x_d, y_d = zip(*cities_dest)

    axe.scatter(x_o, y_o, marker="s", c="red")  # , s=8
    axe.scatter(x_d, y_d, marker="o", c="green")  # , s=12

    travelers = [(trav["x"], trav["y"], trav["name"]) for trav in local_data["traveler"]]
    x_trav, y_trav, _ = zip(*travelers)
    axe.scatter(x_trav, y_trav, marker="D", c="blue")  # color array

    # step4 : optional display of vertices and travelers names
    if show_names:
        coef = 0.3*(axe.get_xlim()[1]-axe.get_xlim()[0])/15
        for i in range(len(cities)):
            axe.text(x[i]+coef, y[i]+coef, local_data["peak"][i]["name"],
                     fontsize='x-small', c="black")

        for x, y, name in travelers:
            axe.text(x+coef, y+coef, name, fontsize='x-small', c="blue")  # color array

    # step5 : dump base graph and enrich it in each thread
    graph_buffer = io.BytesIO()
    pickle.dump(fig, graph_buffer)

    # step6 : start threads
    g_files = []
    g_files_lock = Lock()
    threads = []
    for idThread in range(nb_graph):
        graph_buffer.seek(0)  # crucial
        newfig = pickle.load(graph_buffer)
        args = (idThread, newfig, results[idThread], cities,
                local_data["traveler"], "blue",  # color array
                path, result_name, save_gif, fps, g_files, g_files_lock)
        threads.append(Thread(target=plot_path, args=args))

    for thread in threads:
        thread.start()
        thread.join()

    return g_files
