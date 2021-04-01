import matplotlib.pyplot as plt
import imageio
import os
import geopandas
import random
from geopip import search


def make_graph(path, local_data, results, result_name, save_gif):
    fig2, axe2 = plt.subplots()
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
        countries_map.append(geopandas.read_file(path+"\\country_maps\\"+country+".shp"))

    # extract couple [x, y]
    x, y = zip(*cities)

    # prepare graphs
    nb_graph = min(3, len(results))

    files = []
    for idGraph in range(nb_graph):
        axe2.clear()
        for country in countries_map:
            country.plot(ax=axe2)
        axe2.title.set_text(f"{str(results[idGraph][0])}km\n{str([x+1 for x in results[idGraph][1]])[1:-1]}")

        # print peaks
        axe2.scatter(x, y, c="black", s=1)
        for i in range(len(list(dict.fromkeys(results[0][1])))):
            coef = (axe2.get_xlim()[1]-axe2.get_xlim()[0])/15
            axe2.text(x[i]+random.choice([-0.1,0.1])*coef, y[i]+random.choice([-0.1,0.1])*coef, local_data["peak"][i]["name"], fontsize='xx-small')

        # print traveler origin
        travel = local_data["traveler"][0]
        axe2.scatter(travel["x"], travel["y"], c="red",s=1)

        # print travel from origin to first peak
        city = [travel["x"], travel["y"]]
        nexCity = cities[results[idGraph][1][0]]

        arr2 = axe2.arrow((nexCity[0]-city[0])*0.05+city[0], (nexCity[1]-city[1])*0.05+city[1], 0.9*(nexCity[0]-city[0]), 0.9*(nexCity[1]-city[1]),
                           length_includes_head=True, color="red", width=0.001,head_width=0.5,head_length=0.5, alpha=0.8)
        axe2.legend([arr2,], [local_data["traveler"][0]["name"],], bbox_to_anchor=(0.5, -0.1), fontsize='small')

        # gif img
        fileNames = []
        if(save_gif):
            name = f"{idGraph}_init.png"
            fig2.savefig(name)
            fileNames.append(name)

        # travel between peaks
        for idCity, city in enumerate(results[idGraph][1][:-1]):
            city = cities[city]
            nexCity = cities[results[idGraph][1][idCity+1]]
            axe2.arrow((nexCity[0]-city[0])*0.05+city[0], (nexCity[1]-city[1])*0.05+city[1], 0.9*(nexCity[0]-city[0]), 0.9*(nexCity[1]-city[1]),
                           length_includes_head=True, color="red", width=0.001,head_width=0.5,head_length=0.5, alpha=0.8)

            # gif img
            if(save_gif):
                name = f"{idGraph}_{idCity}.png"
                fig2.savefig(name)
                fileNames.append(name)

        # assemble gif
        if(save_gif):
            with imageio.get_writer(f"{path}\\results\\{result_name}_{idGraph}.gif", mode='I') as gifFile:
                for fileName in fileNames:
                    image = imageio.imread(fileName)
                    gifFile.append_data(image)
            files.append(f"{path}\\results\\{result_name}_{idGraph}.gif")

            for fileName in fileNames:
                os.remove(fileName)

        fig2.savefig(f"{path}\\results\\{result_name}_{idGraph}.png", dpi=500)
        files.append(f"{path}\\results\\{result_name}_{idGraph}.png")

    plt.close(fig2)
    return files
