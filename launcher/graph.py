import matplotlib.pyplot as plt
import imageio
import os


def make_graph(local_data, results, result_name, save_gif):
    # extract couple [x, y]
    cities = [[local_data["peak"][i]["x"], local_data["peak"][i]["y"]]
              for i in range(len(local_data["peak"]))]

    # get graph limits
    minX = min([coord[0] for coord in cities])
    maxX = max([coord[0] for coord in cities])
    minY = min([coord[1] for coord in cities])
    maxY = max([coord[1] for coord in cities])

    # prepare graphs
    nb_graph = min(3, len(results))
    fig, axes = plt.subplots(figsize=(10, 10), ncols=nb_graph, sharey=True)
    fig2, axe2 = plt.subplots()

    if nb_graph == 1:
        axes = [axes]

    for idGraph in range(nb_graph):
        axe2.clear()
        axe1 = axes[idGraph]
        axe1.set_box_aspect(1)
        axe1.title.set_text(f"{str(results[idGraph][0])}km\n{str([x+1 for x in results[idGraph][1]])[1:-1]}")
        axe1.set_xlim(minX-1, maxX+1)
        axe1.set_ylim(minY-1, maxY+1)

        axe2.set_box_aspect(1)
        axe2.title.set_text(f"{str(results[idGraph][0])}km\n{str([x+1 for x in results[idGraph][1]])[1:-1]}")
        axe2.set_xlim(minX-1, maxX+1)
        axe2.set_ylim(minY-1, maxY+1)

        # print peaks
        for i in range(len(results[0][1])):
            x = local_data["peak"][i]["x"]
            y = local_data["peak"][i]["y"]
            axe1.scatter(x, y, c="black")
            axe2.scatter(x, y, c="black")
            axe1.text(x, y+0.5, local_data["peak"][i]["name"])
            axe2.text(x, y+0.5, local_data["peak"][i]["name"])

        # print traveler origin
        travel = local_data["traveler"][0]
        axe1.scatter(travel["x"], travel["y"], c="red")
        axe2.scatter(travel["x"], travel["y"], c="red")

        # print final peak
        # dest = local_data["peak"][results[idGraph][1][-1]]
        # axe1.scatter(dest["x"], dest["y"], c="green")
        # axe2.scatter(dest["x"], dest["y"], c="green")

        # gif img
        fileNames = []
        if save_gif:
            name = f"{idGraph}_peaks.png"
            fig2.savefig(name)
            fileNames.append(name)

        # print travel from origin to first peak
        city = [travel["x"], travel["y"]]
        nexCity = cities[results[idGraph][1][0]]

        arr1 = axe1.arrow(city[0], city[1], nexCity[0]-city[0], nexCity[1]-city[1],
                          head_width=0.15*nb_graph, head_length=0.35*nb_graph,
                          length_includes_head=True, color="red")
        arr2 = axe2.arrow(city[0], city[1], nexCity[0]-city[0], nexCity[1]-city[1],
                           head_width=0.15*nb_graph, head_length=0.35*nb_graph,
                           length_includes_head=True, color="red")
        axe1.legend([arr1,], [local_data["traveler"][0]["name"],], bbox_to_anchor=(0.5, -0.1), fontsize='small') # https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
        axe2.legend([arr2,], [local_data["traveler"][0]["name"],], bbox_to_anchor=(0.5, -0.1), fontsize='small')

        # gif img
        if(save_gif):
            name = f"{idGraph}_init.png"
            fig2.savefig(name)
            fileNames.append(name)

        # travel between peaks
        for idCity, city in enumerate(results[idGraph][1][:-1]):
            city = cities[city]
            nexCity = cities[results[idGraph][1][idCity+1]]

            axe1.arrow(city[0], city[1], nexCity[0]-city[0], nexCity[1]-city[1],
                      head_width=0.15*nb_graph, head_length=0.35*nb_graph,
                      length_includes_head=True, color="red")
            axe2.arrow(city[0], city[1], nexCity[0]-city[0], nexCity[1]-city[1],
                      head_width=0.15*nb_graph, head_length=0.35*nb_graph,
                      length_includes_head=True, color="red")

            # gif img
            if(save_gif):
                name = f"{idGraph}_{idCity}.png"
                fig2.savefig(name)
                fileNames.append(name)

        # assemble gif
        if(save_gif):
            with imageio.get_writer(f"graph_{idGraph}.gif", mode='I') as gifFile:
                for fileName in fileNames:
                    image = imageio.imread(fileName)
                    gifFile.append_data(image)

            for fileName in fileNames:
                os.remove(fileName)

    fig.savefig(result_name)
    plt.close(fig2)
    plt.show()
