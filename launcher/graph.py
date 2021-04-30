import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import imageio
import os
import geopandas
from geopip import search
from threading import Thread, Lock, Event
from pygifsicle import optimize
import pickle
import io
import random

from defines import MAPS_FOLDER, RESULT_FOLDER, MAX_COUNTRIES


def plot_path(idThread, interrupt_event, fig, results, cities,
              local_travelers, travel_colors, return_origin,
              path, result_name, save_gif, fps, g_files, g_files_lock):
    try:
        axe = fig.gca()
        axe.title.set_text(f"{results[4]} : {results[2][0]}km")  # :.1f

        img_buffers = []
        if(save_gif):
            b = io.BytesIO()
            fig.savefig(b, format='png')
            b.seek(0)  # crucial
            img_buffers.append(b)

        # travel between peaks
        for idTravel, traveler in enumerate(results[3]):
            # print travel from origin to first peak
            city = [local_travelers[idTravel]["x"], local_travelers[idTravel]["y"]]
            nextCity = cities[traveler[1][0]]

            if city != nextCity:  # if distinct
                deltaX = nextCity[0]-city[0]
                deltaY = nextCity[1]-city[1]

                axe.arrow(deltaX*0.05+city[0], deltaY*0.05+city[1], deltaX*0.9, deltaY*0.9,
                        length_includes_head=True, head_width=0.5, head_length=0.5,
                        width=0.001, color=travel_colors[idTravel % len(travel_colors)], alpha=0.75)

            if(save_gif):
                b = io.BytesIO()
                fig.savefig(b, format='png')
                b.seek(0)  # crucial
                img_buffers.append(b)

            for idCity, city in enumerate(traveler[1][:-1]):
                city = cities[city]
                nextCity = cities[traveler[1][idCity+1]]

                if city == nextCity:
                    continue

                deltaX = nextCity[0]-city[0]
                deltaY = nextCity[1]-city[1]

                axe.arrow(deltaX*0.05+city[0], deltaY*0.05+city[1], deltaX*0.9, deltaY*0.9,
                        length_includes_head=True, head_width=0.5, head_length=0.5,
                        width=0.001, color=travel_colors[idTravel % len(travel_colors)], alpha=0.75)

                # gif img
                if(save_gif):
                    b = io.BytesIO()
                    fig.savefig(b, format='png')
                    b.seek(0)  # crucial
                    img_buffers.append(b)

            if return_origin:
                city = cities[traveler[1][-1]]
                nextCity = [local_travelers[idTravel]["x"], local_travelers[idTravel]["y"]]

                deltaX = nextCity[0]-city[0]
                deltaY = nextCity[1]-city[1]

                axe.arrow(deltaX*0.05+city[0], deltaY*0.05+city[1], deltaX*0.9, deltaY*0.9,
                          length_includes_head=True, head_width=0.5, head_length=0.5,
                          width=0.001, color=travel_colors[idTravel % len(travel_colors)], alpha=0.75)

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
            fig.savefig(filename)

    except KeyboardInterrupt:
        interrupt_event.set()
        return


def make_graph(path, local_data, compute_data, results, results_opti, opti_names, nb_graph, result_name, show_names, link_vertices, background, save_gif, fps, return_origin):
    plt.switch_backend('agg')

    # prepare graphs
    nb_graph = min(nb_graph, len(results))

    cities = [(peak["x"], peak["y"]) for peak in local_data["peak"]]
    x, y = zip(*cities)  # zip because of tuples : extract couples [x, y]

    # take most optimized path for selected graph range
    for name, opti in zip(opti_names, results_opti):
        convertor = {id_exe: counter for counter, (*_, id_exe) in enumerate(opti) if counter < nb_graph}  # id translation
        for id_exe, id_convert in convertor.items():
            if results[id_exe][1] > opti[id_convert][1]:  # lower score = better path
                results[id_exe] = opti[id_convert]
                del results[id_exe][-1]
                results[id_exe].append(name)

    for id, line in enumerate(results):
        if len(line) < 5:
            results[id].append("Generated")

    # plot common part
    fig = plt.figure(figsize=(6, 3))
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
                line, = axe.plot([x1, x2], [y1, y2], zorder=0, linestyle="dashed", c="green", alpha=0.3)
        line.set_label('Refers')

    # step3.1 : display origins and destinations
    cities_origin = [(peak["x"], peak["y"]) for peak in local_data["peak"] if peak["origin"]]
    cities_dest = [(peak["x"], peak["y"]) for peak in local_data["peak"] if not peak["origin"]]

    axe.scatter(*zip(*cities_origin), marker="s", c="red", label="Deposit")
    axe.scatter(*zip(*cities_dest), marker="o", c="green", label="Client")

    # step3.2 : display travelers origins
    nb_trav = len(local_data["traveler"])
    if nb_trav < 10:
        colors = list(mcolors.TABLEAU_COLORS.values())
    else:
        colors = mcolors.CSS4_COLORS  # 148 colors
        colors.pop("lightgray")
        colors.pop("lightgrey")
        colors.pop("gainsboro")
        colors = [color for color in colors.values() if color.count("F") < 4]  # 128 left
    random.shuffle(colors)
    colors = colors[:nb_trav]

    travelers = [(trav["x"], trav["y"], trav["name"]) for trav in local_data["traveler"]]
    x_trav, y_trav, _ = zip(*travelers)
    axe.scatter(x_trav, y_trav, marker="D", c=colors, label="Traveler")

    # step4 : optional display of vertices and travelers names
    if show_names:
        coef = 0.3*(axe.get_xlim()[1]-axe.get_xlim()[0])/15
        for i in range(len(cities)):
            axe.text(x[i]+coef, y[i]+coef, local_data["peak"][i]["name"],
                     fontsize='x-small', c="black")

        for (x, y, name), color in zip(travelers, colors):
            axe.text(x+coef, y+coef, name, fontsize='x-small', c=color)

    # step5 : tweak legend order & position
    if link_vertices:
        handles, labels = axe.get_legend_handles_labels()
        handles = handles[1:3]+[handles[0]]+[handles[3]]
        labels = labels[1:3]+[labels[0]]+[labels[3]]
        axe.legend(handles, labels, ncol=4, loc='lower center', bbox_to_anchor=(0.5, -0.15))
    else:
        axe.legend(ncol=3, loc='lower center', bbox_to_anchor=(0.5, -0.15))

    # step6 : dump base graph and enrich it in each thread
    graph_buffer = io.BytesIO()
    pickle.dump(fig, graph_buffer)

    # step7 : start threads
    g_files = []
    g_files_lock = Lock()
    interrupt_event = Event()
    threads = []
    for idThread in range(nb_graph):
        graph_buffer.seek(0)  # crucial
        newfig = pickle.load(graph_buffer)

        args = (idThread, interrupt_event, newfig, results[idThread], cities,
                local_data["traveler"], colors, return_origin,
                path, result_name, save_gif, fps, g_files, g_files_lock)
        threads.append(Thread(target=plot_path, args=args))
        threads[-1].start()

    for thread in threads:
        thread.join()

    if interrupt_event.is_set():
        print("Close program")
        exit()

    return g_files
