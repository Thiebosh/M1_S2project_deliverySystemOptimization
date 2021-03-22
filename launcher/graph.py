import matplotlib.pyplot as plt
import imageio
import os

def make_graph(local_data, results, result_name, save_gif):
    cities = []
    for i in range(len(results[0][1])-1):
        x = local_data[i]["x"]
        y = local_data[i]["y"]
        cities.append([x, y])

    minX = min([coord[0] for coord in cities])
    maxX = max([coord[0] for coord in cities])
    minY = min([coord[1] for coord in cities])
    maxY = max([coord[1] for coord in cities])

    nb_graph = min(3, len(results))
    
    fig, axes = plt.subplots(figsize=(10, 10), ncols=nb_graph, sharey=True)
    fig2, axes2 = plt.subplots()
    
    for idGraph in range(nb_graph):
        axes2.clear()
        axe1 = axes[idGraph]
        axe1.set_box_aspect(1)
        axe1.title.set_text(f"{str(results[idGraph][0])}km\n{str([x+1 for x in results[idGraph][1]])[1:-1]}")
        axe1.set_xlim(minX-1, maxX+1)
        axe1.set_ylim(minY-1, maxY+1)

        axes2.set_box_aspect(1)
        axes2.title.set_text(f"{str(results[idGraph][0])}km\n{str([x+1 for x in results[idGraph][1]])[1:-1]}")
        axes2.set_xlim(minX-1, maxX+1)
        axes2.set_ylim(minY-1, maxY+1)
    
        for i in range(len(results[0][1])-1):
            x = local_data[i]["x"]
            y = local_data[i]["y"]
            axe1.scatter(x, y, c="black")
            axes2.scatter(x, y, c="black")
            axe1.text(x, y+0.5, local_data[i]["name"])
            axes2.text(x, y+0.5, local_data[i]["name"])

        origin = local_data[results[idGraph][1][0]]
        axe1.scatter(origin["x"], origin["y"], c="blue")
        axes2.scatter(origin["x"], origin["y"], c="blue")
        fileNames = []
        if save_gif:
            fig2.savefig(str(idGraph)+"_init"+".png")
            fileNames.append(str(idGraph)+"_init"+".png")

        for idCity, city in enumerate(results[idGraph][1]):
            index = (0 if idCity == len(results[idGraph][1])-1 else idCity+1)
            nexCity = cities[results[idGraph][1][index]]
            city = cities[city]
            
            axe1.arrow(city[0], city[1], nexCity[0]-city[0], nexCity[1]-city[1],
                      head_width=0.15*nb_graph, head_length=0.35*nb_graph,
                      length_includes_head=True, color="red")
            axes2.arrow(city[0], city[1], nexCity[0]-city[0], nexCity[1]-city[1],
                      head_width=0.15*nb_graph, head_length=0.35*nb_graph,
                      length_includes_head=True, color="red")
            if(save_gif):
                fig2.savefig(str(idGraph)+"_"+str(idCity)+".png")
                fileNames.append(str(idGraph)+"_"+str(idCity)+".png")
        if(save_gif):
            with imageio.get_writer("graph_"+str(idGraph)+".gif", mode='I') as gifFile:
                for fileName in fileNames:
                    image = imageio.imread(fileName)
                    gifFile.append_data(image)
            for fileName in fileNames:
                    os.remove(fileName)
    fig.savefig(result_name)
    plt.close(fig2)
    plt.show()