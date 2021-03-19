import pathlib
import asyncio
from parse import user_args
from common import load_data, execute_heuristic
import math
import matplotlib.pyplot as plt
import types
import numpy as np

if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    file_name, file_path, heuristic_inputs = user_args(path)
    
    local_data, to_compute = load_data(file_name, file_path)
    print(local_data)
    results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))
    
    cities = []
    for i in range(len(results[0][1])-1):
        x = local_data[i]["x"]
        y = local_data[i]["y"]
        cities.append([x,y])

    minX = min([coord[0] for coord in cities])
    maxX = max([coord[0] for coord in cities])
    minY = min([coord[1] for coord in cities])
    maxY = max([coord[1] for coord in cities])

    print(f"We get {len(results)} distinc(s) peaks travel(s) order(s) :")
    for distance, travel in results:
        print(f"- {str(travel)[1:-1]} take {distance}km")


    fig, axes = plt.subplots(figsize=(10,10), ncols=min(5,len(results)), sharey=True)
    if type(axes) is not np.ndarray:
        axes = [axes]

    for idGraph, axe in enumerate(axes):
        axe.set_box_aspect(1)
        axe.title.set_text("Distance: "+str(results[idGraph][0])+"km")
        axe.set_xlim(minX-1, maxX+1)
        axe.set_ylim(minY-1,maxY+1)
        for i in range(len(results[0][1])-1):
            x = local_data[i]["x"]
            y = local_data[i]["y"]
            axe.scatter(x,y, c="black")
            # axe.text(x,y+0.5,"city" +str(i))
            axe.text(x,y+0.5, local_data[i]["name"])
        for idCity, city in enumerate(results[idGraph][1]):
            nexCity = None
            if idCity == len(results[idGraph][1])-1:
                nexCity = results[idGraph][1][0]
            else:
                nexCity = results[idGraph][1][idCity+1]
            arrow = axe.arrow(cities[city][0],cities[city][1], cities[nexCity][0]-cities[city][0], cities[nexCity][1]-cities[city][1])
            arrow.set_color("red")
    
    plt.show()
    fig.savefig("savedFile.png")