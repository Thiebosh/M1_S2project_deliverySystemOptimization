#include <iostream>
#include <string>
#include <math.h>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <algorithm>
#include <map>
#include <limits>
#include <typeinfo>
#include "D:\S2 project\M1_S2project_deliverySystemOptimization\core\json.hpp"
using namespace std;
using json = nlohmann::json;

typedef struct dist_ {
    int id;
    float distance;
} dist;


vector<int> findsolution(int id, json input, int nbClosest);
float totaldis(vector<int>& path, json input);
vector<int> findnei(vector<int> solution, json input);

int main(int argc, char* argv[]) {
    int id = atoi(argv[1]);
    cout << id << endl;

    if (argc < 4) return -1;

    time_t seed = time(NULL) % id;
    srand(seed);
    cout << seed << endl;

    json inputData = json::parse(argv[2]);
    int batch_size = atoi(argv[3]);

    // declare result tab
    vector<int> currentpath = findsolution(id, inputData, batch_size);

    float totalDistance = totaldis(currentpath, inputData) / (float)inputData["traveler"][0]["speed"];
    cout << totalDistance << ";";
    for (int elem : currentpath) cout << elem << ",";
    cout<<endl;
    for (int i = 0; i < 20; i++) {
       currentpath=findnei(currentpath, inputData);
    }
    totalDistance = totaldis(currentpath, inputData) / (float)inputData["traveler"][0]["speed"];
    cout << totalDistance << ";";
    for (int elem : currentpath) cout << elem << ",";
    return 0;
}

vector<int> getNthClosest(int n, vector<double> arc) {
    vector<int> closest;
    vector<double> sortedArc = arc;
    sort(sortedArc.begin(), sortedArc.end());
    for (auto i = 0; i < min(n, (int)arc.size()); i++) {
        vector<double>::iterator itr = find(arc.begin(), arc.end(), sortedArc[i]);
        closest.push_back(distance(arc.begin(), itr));
    }
    return closest;
}

vector<int> getRemainingRestaurant(map<int, vector<int>> map) {
    vector<int> remainingRestaurant;
    for (auto i : map) {
        remainingRestaurant.push_back(i.first);
    }
    return remainingRestaurant;
}

vector<int> getRemainingClient(map<int, vector<int>> map) {
    vector<int> remainingClients;
    for (auto i : map) {
        for (auto j : i.second) {
            remainingClients.push_back(j);
        }
    }
    return remainingClients;
}

vector<int> getPossibleNextPeak(vector<double> arc, vector<int> possiblePoints, int nbClosest) {
    vector<double> possiblePointsDistanceList;
    vector<double> allDistances = arc;
    vector<int> closestPoints;
    vector<int> points;


    for (auto i : possiblePoints) {
        possiblePointsDistanceList.push_back(allDistances[i]);
    }

    closestPoints = getNthClosest(nbClosest, possiblePointsDistanceList);

    for (auto i : closestPoints) {
        vector<double>::iterator itr = find(allDistances.begin(), allDistances.end(), possiblePointsDistanceList[i]);
        points.push_back(distance(allDistances.begin(), itr));
    }

    return points;
}

vector<int> findsolution(int id, json input, int nbClosest) {
    // build list of unselected peaks
    map<int, vector<int>> restaurantClientLink;
    //vector<int> remainingClients;
    vector<int> canDeliverClients; //clients
    vector<int> currSolution;
    //initializing arrays
    for (int i = 0; i < input["peak"].size(); ++i) {
        if (input["peak"][i]["origin"] == 1) {
            vector<int> clients;
            for (int j = 0; j < input["peak"][i]["link"].size(); j++) {
                clients.push_back(input["peak"][i]["link"][j]);
            }
            restaurantClientLink.insert(pair<int, vector<int>>(i, clients));
        }
        else if (input["peak"][i]["origin"] == 0) {
            //remainingClients.push_back(i);
        }

    }

    //initialize storage's capacity
    int storage = input["traveler"][0]["qty"];


    vector<int> possiblePoints;
    int solutionId = 0;
    bool solutionFound = false;
    int idPoint = -1;
    // select first restaurant
    possiblePoints = getPossibleNextPeak(input["traveler"][0]["arc"], getRemainingRestaurant(restaurantClientLink), nbClosest);
    int nbClosestCopy = nbClosest;
    do {
        if (!solutionFound) {
            //if no path had been found, remove last tried id and try again
            auto it = find(possiblePoints.begin(), possiblePoints.end(), idPoint);
            if (it != possiblePoints.end()) {
                possiblePoints.erase(it);
            }
        }
        else {
            //if a path had been found, reinitialize possible destinations
            solutionFound = false;
            possiblePoints.clear();
            nbClosestCopy = nbClosest;
            vector<int> tmpPossiblePoints = getRemainingRestaurant(restaurantClientLink);
            if (!canDeliverClients.empty()) {
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canDeliverClients.begin(), canDeliverClients.end());
            }
            possiblePoints = getPossibleNextPeak(input["arc"][idPoint], tmpPossiblePoints, nbClosestCopy);

        }
        if (possiblePoints.size() == 0) {
            //if there no way to deliver everyone only by going to the n closest places, we increase this number.
            nbClosestCopy += 1;
            vector<int> tmpPossiblePoints = getRemainingRestaurant(restaurantClientLink);
            if (!canDeliverClients.empty()) {
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canDeliverClients.begin(), canDeliverClients.end());
            }
            possiblePoints = getPossibleNextPeak(input["arc"][idPoint], tmpPossiblePoints, nbClosestCopy);
        }

        idPoint = possiblePoints[rand() % possiblePoints.size()];
        if (input["peak"][idPoint]["origin"] == 1) {
            //if point is a restaurant check every clients of this restaurant
            for (int client : restaurantClientLink[idPoint]) {
                if (storage - (int)input["peak"][client]["qty"] >= 0) {
                    /*
                        if deliveryman can store the order, we add this restaurant to the path and this client to
                        the client that can be delivered and we reduce the storage space.
                    */
                    solutionFound = true;
                    storage -= (int)input["peak"][client]["qty"];
                    currSolution.push_back(idPoint);
                    canDeliverClients.push_back(client);
                    restaurantClientLink[idPoint].erase(find(restaurantClientLink[idPoint].begin(), restaurantClientLink[idPoint].end(), client));
                    if (restaurantClientLink[idPoint].empty()) {
                        restaurantClientLink.erase(idPoint);
                    }
                    break;
                }
            }
        }
        else if (input["peak"][idPoint]["origin"] == 0) {
            /*
                point is a client ready to be delivered, we remove it from the client ready to be delivered and
                we increase the storage space of the deliveryman
            */
            solutionFound = true;
            storage += (int)input["peak"][idPoint]["qty"];
            currSolution.push_back(idPoint);
            canDeliverClients.erase(find(canDeliverClients.begin(), canDeliverClients.end(), idPoint));
        }
    } while (!restaurantClientLink.empty() || !canDeliverClients.empty());

    return currSolution;

}
bool checknei(vector<int> solution,json input) {
    vector<int> ableclient;
    int storage = input["traveler"][0]["qty"];
    int des=0;
    for (int i = 0; i < solution.size(); i++) {
        if (input["peak"][solution[i]]["origin"] == 1) {
            if (storage == 0) { des++ ; break; }
            storage--;
            for (int j = 0; j < input["peak"][solution[i]]["link"].size();j++) {
                ableclient.push_back(input["peak"][solution[i]]["link"][j]);
            }
        }
        if (input["peak"][solution[i]]["origin"] == 0) {
            storage++;
            int judge = 0;
            for (int j = 0; j < ableclient.size(); j++) {
                if (solution[i] == ableclient[j]) { 
                    judge++;
                }
            }
            if (judge == 0) { des++ ; break; }
        }
    }
    if(des!=0){return 0;}
    else{return 1;}
}
vector<int> findnei(vector<int> solution, json input) {
    vector<int> nei = solution;
    int a = rand() % input["peak"].size() + 1;
    for (int i=0; i < nei.size()&&i!=a; i++) {
        int nuclear = nei[a];
        nei[a] = nei[i];
        nei[i] = nuclear;
        if (checknei(nei,input)==1) {
            float dis = totaldis(nei, input);
            if (dis < totaldis(solution, input)) { solution = nei; }
        }
    }
    return solution;
}
float totaldis(vector<int>& path, json input) {
    float total = 0;
    for (int i = 1; i < path.size(); i++) {
        total += (float)input["arc"][path[i - 1]][path[i]];
    }
    return total;
}