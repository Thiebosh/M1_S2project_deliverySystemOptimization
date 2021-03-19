import pathlib
import asyncio
from parse import user_args
from common import load_data, execute_heuristic

def remove_duplicates_from_results(res):
    returnedArray = list()
    for data in res:
        path = data[1]
        path.pop()
        pathExists = False
        for i in range(len(path)-1):
            path.insert(0,path.pop())
            for existingData in returnedArray:
                if existingData[1] == path:
                    pathExists = True
        for i in range(len(path)-1):
            path.append(path[0])
            path.pop(0)
            for existingData in returnedArray:
                if existingData[1][:-1] == path:
                    pathExists = True
        if not pathExists:
            path.append(path[0])
            returnedArray.append(data)
    return returnedArray

if __name__ == "__main__":
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    file_name, file_path, heuristic_inputs = user_args(path)
    cities = []
    for i in range(len(results[0][1])-1):
        x = 10*math.cos(2*math.pi/(len(results[0][1])-1)*i)
        y = 10*math.sin(2*math.pi/(len(results[0][1])-1)*i)
        cities.append([x,y])

    local_data, to_compute = load_data(file_name, file_path)

    results = asyncio.run(execute_heuristic(to_compute, *heuristic_inputs))

    print(f"We get {len(results)} distinc(s) peaks travel(s) order(s) :")
    for distance, travel in results:
        print(f"- {str(travel)[1:-1]} take {distance}km")


    fig, axes = plt.subplots(figsize=(10,10), ncols=min(8,len(results)), sharey=True)
    for idGraph, axe in enumerate(axes):
        axe.set_box_aspect(1)
        axe.set_xlim(-10,10)
        axe.set_ylim(-10,10)
        for i in range(len(results[0][1])-1):
            x = 9*math.cos(2*math.pi/(len(results[0][1])-1)*i)
            y = 9*math.sin(2*math.pi/(len(results[0][1])-1)*i)
            axe.scatter(x,y, c="black")
            axe.text(x,y+0.5,"city" +str(i))
        for idCity, city in enumerate(results[idGraph][1]):
            nexCity = None
            if idCity == len(results[idGraph][1])-1:
                nexCity = results[idGraph][1][0]
            else:
                nexCity = results[idGraph][1][idCity+1]
            arrow = axe.arrow(cities[city][0],cities[city][1], cities[nexCity][0]-cities[city][0], cities[nexCity][1]-cities[city][1])
            arrow.set_color("red")

    for id, task in enumerate(results):
        print(f"peaks travel in '{task[1]}' order take {task[0]}km")
    
    plt.show()
    fig.savefig("savedFile.png")