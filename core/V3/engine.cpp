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
#include <fstream>
#include <streambuf>
#include <numeric>
#include "../json.hpp"
#include "pathComparison.h"

//input args
#define ARG_ID 1
#define ARG_FILE_PATH 2
#define NB_ARGS 3

using namespace std;

typedef struct dist_
{
    int id;
    float distance;
} dist;

void findsolution(json *input, map<int, vector<int>> *restaurantClientLink, vector<vector<int>> *path, mutex *restaurantClientLink_mutex, mutex *path_mutex, int idTraveler);

int main(int argc, char *argv[])
{
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;
    
    if (argc < NB_ARGS) return -1;

    time_t seed = time(NULL) % id;
    srand(seed);
    cout << seed << endl;

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    string str( (std::istreambuf_iterator<char>(t) ),
                       (std::istreambuf_iterator<char>()) );

    json jsonData = json::parse(str);
    json* inputData = &jsonData;

    vector<vector<int>> path(inputData->at("traveler").size(), vector<int>());

    mutex path_mutex;
    map<int, vector<int>> restaurantClientLink;
    mutex restaurantClientLink_mutex;

    //initializing restaurantClientLink
    for (int i = 0; i < inputData->at("peak").size(); ++i)
    {
        if (inputData->at("peak").at(i).at("origin") == 1)
        {
            vector<int> clients;
            for (int j = 0; j < inputData->at("peak").at(i).at("link").size(); j++)
            {
                clients.push_back(inputData->at("peak").at(i).at("link").at(j));
            }
            restaurantClientLink.insert(pair<int, vector<int>>(i, clients));
        }
    }

    // start threads
    // declare result tab
    vector<thread> threads;
    for(int i = 0; i < inputData->at("traveler").size(); i++){
        threads.push_back(thread(findsolution, inputData,   &restaurantClientLink, &path, &restaurantClientLink_mutex, &path_mutex, i));
    }
    for(auto& curThread: threads){
        curThread.join();
    }

    // Print results
    vector<float> travelersVar;
    vector<float> travelersMed;
    vector<float> travelerDist;
    for(int i = 0; i < inputData->at("traveler").size(); i++){
        travelersVar.push_back(travelerDistVar(path[i], inputData, i));
        travelersMed.push_back(travelerDistMed(path[i], inputData, i));
        travelerDist.push_back(travelerDistTotal(path[i], inputData, i));
    }
    cout << var(travelersVar) << endl;
    cout << var(travelersMed) << endl;
    cout << var(travelerDist) << endl;
    cout << accumulate(travelerDist.begin(), travelerDist.end(), 0.0) << endl;

    for(int i = 0; i < inputData->at("traveler").size(); i++){
        if(travelerDist[i] > 0){
            cout << travelerDist[i] << ";";
            for (int elem : path[i]){
                cout << elem << ",";
            }
        }
        else cout << "0;-1,";
        cout << endl;
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


int getIdPoint(vector<int> allPoints){
    reverse(allPoints.begin(), allPoints.end());
    vector<double> weights;
    vector<double> normalized_weights;
    double min_val;
    double max_val;

    for(double i = 0; i < allPoints.size(); i++){
        weights.push_back(1.0/(i+0.001));
    }
    //normalizing weights 
    min_val = *min_element(weights.begin(), weights.end());
    max_val = *max_element(weights.begin(), weights.end());
    for(int i = 0; i < weights.size(); ++i){
        normalized_weights.push_back((double)(weights[i]-min_val)/(double)(max_val-min_val));     
    }
    reverse(normalized_weights.begin(), normalized_weights.end());
    double randomValue = (double) rand() / (RAND_MAX);
    for(int i = 0; i < normalized_weights.size(); i++){
        if(randomValue < normalized_weights[i]){
            return allPoints[i];
        }
    }
    return -1;
}

void findsolution(json *input, map<int, vector<int>> *restaurantClientLink, vector<vector<int>>* path, mutex *restaurantClientLink_mutex, mutex *path_mutex, int idTraveler)
{
    // build list of unselected peaks
    vector<int> canDeliverClients;                          //clients
    vector<int>::iterator cand = canDeliverClients.begin(); //the iterator i used
    //initializing arrays

    //initialize storage's capacity
    
    int storage = input->at("traveler").at(idTraveler).at("qty");

    vector<int> possiblePoints;
    int solutionId = 0;
    bool solutionFound = true;
    int idPoint = -1;

    // select first restaurant
    do
    {
        restaurantClientLink_mutex->lock();
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
            vector<int> tmpPossiblePoints = getRemainingRestaurant(restaurantClientLink);
            if (!canDeliverClients.empty())
            {
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canDeliverClients.begin(), canDeliverClients.end());
            }
            if(idPoint > 0){
                possiblePoints = getPossibleNextPeak(input->at("arc").at(idPoint), tmpPossiblePoints, tmpPossiblePoints.size());
            }else{
                possiblePoints = getPossibleNextPeak(input->at("traveler").at(idTraveler).at("arc"), tmpPossiblePoints, tmpPossiblePoints.size());
            }
        }
        if(possiblePoints.size() == 0){
            restaurantClientLink_mutex->unlock();
            return;
        }
        double val = getIdPoint(possiblePoints);
        if(val >= 0){
            idPoint = val;
        }else{
            restaurantClientLink_mutex->unlock();
            return;
        }   

        if (input->at("peak").at(idPoint).at("origin") == 1 && restaurantClientLink->find(idPoint) != restaurantClientLink->end())
        {
            //if point is a restaurant check every clients of this restaurant
            for (int client : restaurantClientLink->at(idPoint))
            {
                if (storage - (int)input->at("peak").at(client).at("qty") >= 0)
                {
                    /*
                        if deliveryman can store the order, we add this restaurant to the path and this client to 
                        the client that can be delivered and we reduce the storage space.
                    */
                    solutionFound = true;
                    storage -= (int)input->at("peak").at(client).at("qty");
                    path->at(idTraveler).push_back(idPoint);
                    canDeliverClients.push_back(client);
                    vector<int>::iterator it = find(restaurantClientLink->at(idPoint).begin(), restaurantClientLink->at(idPoint).end(), client);
                    if(it != restaurantClientLink->at(idPoint).end()){
                         restaurantClientLink->at(idPoint).erase(it);
                    }

                    if (restaurantClientLink->at(idPoint).empty())
                    {
                        restaurantClientLink->erase(idPoint);
                    }
                    break;
                }
            }
        }
        if (input->at("peak").at(idPoint).at("origin") == 0 && find(canDeliverClients.begin(), canDeliverClients.end(), idPoint) != canDeliverClients.end())
        {
            /*
                point is a client ready to be delivered, we remove it from the client ready to be delivered and
                we increase the storage space of the deliveryman
            */
            solutionFound = true;
            storage += (int)input->at("peak").at(idPoint).at("qty");
            path->at(idTraveler).push_back(idPoint);
            canDeliverClients.erase(find(canDeliverClients.begin(), canDeliverClients.end(), idPoint));
        }
        restaurantClientLink_mutex->unlock();
    } while (!(restaurantClientLink->empty()) || !canDeliverClients.empty());
}
