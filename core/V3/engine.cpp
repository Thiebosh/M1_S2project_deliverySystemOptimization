#include <iostream>
#include <string>
#include <math.h>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <algorithm>
#include <map>
#include <mutex>
#include <thread>
#include "../json.hpp"

using namespace std;
using json = nlohmann::json;

typedef struct dist_
{
    int id;
    float distance;
} dist;

void findsolution(json input, int nbClosest, map<int, vector<int>> *restaurantClientLink, vector<vector<int>> *path, mutex *restaurantClientLink_mutex, mutex *path_mutex, int idTraveler);

float totaldis(vector<int> &path, json input);

int main(int argc, char *argv[])
{
    int id = atoi(argv[1]);
    json inputData = json::parse(argv[2]);
    int batch_size = atoi(argv[3]);

    time_t seed = time(NULL) % id;
    srand(seed);

    vector<vector<int>> path(inputData["traveler"].size(), vector<int>());

    mutex path_mutex;
    map<int, vector<int>> restaurantClientLink;
    mutex restaurantClientLink_mutex;

    //initializing restaurantClientLink
    for (int i = 0; i < inputData["peak"].size(); ++i)
    {
        if (inputData["peak"][i]["origin"] == 1)
        {
            vector<int> clients;
            for (int j = 0; j < inputData["peak"][i]["link"].size(); j++)
            {
                clients.push_back(inputData["peak"][i]["link"][j]);
            }
            restaurantClientLink.insert(pair<int, vector<int>>(i, clients));
        }
    }

    cout << id << endl << seed << endl;

    // start here

    // declare result tab
    vector<thread> threads;
    for(int i = 0; i < inputData["traveler"].size(); i++){
        threads.push_back(thread(findsolution, inputData, batch_size, &restaurantClientLink, &path, &restaurantClientLink_mutex, &path_mutex, i));
    }
    // cout << "threads started" << endl;
    for(auto& curThread: threads){
        curThread.join();
    }
    // cout << "threads joined" << endl;

    // end here

    // for(int i = 0; i < inputData["traveler"].size(); i++){
    for(int i = 0; i < 1; i++){
        cout << totaldis(path[i], inputData) << ";";
        for (int elem : path[i])
            cout << elem << ",";
        // cout << endl;
    }
    

    return 0;
}

vector<int> getNthClosest(int n, vector<double> arc)
{
    vector<int> closest;
    vector<double> sortedArc = arc;
    sort(sortedArc.begin(), sortedArc.end());
    for (auto i = 0; i < min(n, (int)arc.size()); i++)
    {
        vector<double>::iterator itr = find(arc.begin(), arc.end(), sortedArc[i]);
        closest.push_back(distance(arc.begin(), itr));
    }
    return closest;
}

vector<int> getRemainingRestaurant(map<int, vector<int>> *map)
{
    vector<int> remainingRestaurant;
    for (auto i : *map)
    {
        remainingRestaurant.push_back(i.first);
    }
    return remainingRestaurant;
}

vector<int> getRemainingClient(map<int, vector<int>> map)
{
    vector<int> remainingClients;
    for (auto i : map)
    {
        for (auto j : i.second)
        {
            remainingClients.push_back(j);
        }
    }
    return remainingClients;
}

vector<int> getPossibleNextPeak(vector<double> arc, vector<int> possiblePoints, int nbClosest)
{
    vector<double> possiblePointsDistanceList;
    vector<double> allDistances = arc;
    vector<int> closestPoints;
    vector<int> points;

    for (auto i : possiblePoints)
    {
        possiblePointsDistanceList.push_back(allDistances[i]);
    }

    closestPoints = getNthClosest(nbClosest, possiblePointsDistanceList);

    for (auto i : closestPoints)
    {
        vector<double>::iterator itr = find(allDistances.begin(), allDistances.end(), possiblePointsDistanceList[i]);
        points.push_back(distance(allDistances.begin(), itr));
    }

    return points;
}

void findsolution(json input, int nbClosest, map<int, vector<int>> *restaurantClientLink, vector<vector<int>>* path, mutex *restaurantClientLink_mutex, mutex *path_mutex, int idTraveler)
{
    // build list of unselected peaks
    vector<int> canDeliverClients;                          //clients
    vector<int>::iterator cand = canDeliverClients.begin(); //the iterator i used
    //initializing arrays

    //initialize storage's capacity
    int storage = input["traveler"][idTraveler]["qty"];

    vector<int> possiblePoints;
    int solutionId = 0;
    bool solutionFound = false;
    int idPoint = -1;

    // select first restaurant
    restaurantClientLink_mutex->lock();
    possiblePoints = getPossibleNextPeak(input["traveler"][idTraveler]["arc"], getRemainingRestaurant(restaurantClientLink), nbClosest);
    restaurantClientLink_mutex->unlock();
    int nbClosestCopy = nbClosest;
    do
    {  
        if (!solutionFound)
        {
            //if no path had been found, remove last tried id and try again
            auto it = find(possiblePoints.begin(), possiblePoints.end(), idPoint);
            if (it != possiblePoints.end())
            {
                possiblePoints.erase(it);
            }
        }
        else
        {
            //if a path had been found, reinitialize possible destinations
            solutionFound = false;
            possiblePoints.clear();
            nbClosestCopy = nbClosest;
            restaurantClientLink_mutex->lock();
            vector<int> tmpPossiblePoints = getRemainingRestaurant(restaurantClientLink);
            restaurantClientLink_mutex->unlock();
            if (!canDeliverClients.empty())
            {
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canDeliverClients.begin(), canDeliverClients.end());
            }
            // cout << "line 188" << endl;
            possiblePoints = getPossibleNextPeak(input["arc"][idPoint], tmpPossiblePoints, nbClosestCopy);
            // cout << "line 190" << endl;
        }
        if (possiblePoints.size() == 0 && idPoint > 0)
        {
            //if there no way to deliver everyone only by going to the n closest places, we increase this number.
            nbClosestCopy += 1;
            restaurantClientLink_mutex->lock();
            vector<int> tmpPossiblePoints = getRemainingRestaurant(restaurantClientLink);
            restaurantClientLink_mutex->unlock();
            if (!canDeliverClients.empty())
            {
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canDeliverClients.begin(), canDeliverClients.end());
            }
            possiblePoints = getPossibleNextPeak(input["arc"][idPoint], tmpPossiblePoints, nbClosestCopy);

            if(possiblePoints.size() == 0){
                restaurantClientLink_mutex->unlock();
                return;
            }
        }else if(possiblePoints.size() == 0){
            return;
        }
        idPoint = possiblePoints[rand() % possiblePoints.size()];

        restaurantClientLink_mutex->lock();
        // cout << "line 216" << endl;
        if (input["peak"][idPoint]["origin"] == 1 && restaurantClientLink->find(idPoint) != restaurantClientLink->end())
        {
            // cout << "line 218" << endl;
            //if point is a restaurant check every clients of this restaurant
            for (int client : restaurantClientLink->at(idPoint))
            {
                // cout << "line 223" << endl;
                if (storage - (int)input["peak"][client]["qty"] >= 0)
                {
                    // cout << "line 225" << endl;
                    /*
                        if deliveryman can store the order, we add this restaurant to the path and this client to 
                        the client that can be delivered and we reduce the storage space.
                    */
                    solutionFound = true;
                    // cout << "line 233" << endl;
                    storage -= (int)input["peak"][client]["qty"];
                    // cout << "line 235" << endl;
                    path_mutex->lock();
                    path->at(idTraveler).push_back(idPoint);
                    path_mutex->unlock();
                    canDeliverClients.push_back(client);
                    restaurantClientLink->at(idPoint).erase(find(restaurantClientLink->at(idPoint).begin(), restaurantClientLink->at(idPoint).begin(), client));
                    if (restaurantClientLink->at(idPoint).empty())
                    {
                        restaurantClientLink->erase(idPoint);
                    }
                    break;
                }
            }
        }
        restaurantClientLink_mutex->unlock();
        // cout << "line 250" << endl;
        if (input["peak"][idPoint]["origin"] == 0)
        {
            // cout << "line 252" << endl;
            /*
                point is a client ready to be delivered, we remove it from the client ready to be delivered and
                we increase the storage space of the deliveryman
            */
            solutionFound = true;
            // cout << "line 258" << endl;
            storage += (int)input["peak"][idPoint]["qty"];
            // cout << "line 260" << endl;
            path_mutex->lock();
            path->at(idTraveler).push_back(idPoint);
            path_mutex->unlock();
            canDeliverClients.erase(find(canDeliverClients.begin(), canDeliverClients.end(), idPoint));
        }
    } while (!(restaurantClientLink->empty()) || !canDeliverClients.empty());
}


float totaldis(vector<int> &path, json input)
{
    float total = 0;
    for (int i = 1; i < path.size(); i++)
    {
        total += (float)input["arc"][path[i - 1]][path[i]];
    }
    return total;
}
