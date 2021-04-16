#include <iostream>
#include <time.h>
#include <fstream>
#include <vector>
#include <map>
#include "../json.hpp"
#include "pathComparison.h"

//input args
#define ARG_FILE_PATH 2
#define ARG_ID 1
#define NB_ARGS 3

using namespace std;
using json = nlohmann::json;


// definitions
vector<int> getNthClosest(int n, vector<double> &arc);

vector<int> getRemainingRestaurant(map<int, vector<int>> const &map);

vector<int> getRemainingClient(map<int, vector<int>> const &map);

vector<int> getPossibleNextPeak(vector<double> const &arc, vector<int> const &possiblePoints, int nbClosest);

int getIdPoint(vector<int> const &allPoints, vector<double> const &distances);

map<int, vector<int>> findsolution(json const &input);


// main function
int main(int argc, char *argv[]) {
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc < NB_ARGS)
        return -1;

    time_t seed = time(NULL) % id;
    srand(seed);
    cout << seed << endl;

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    json inputData = json::parse((istreambuf_iterator<char>(t)), (istreambuf_iterator<char>()));

    // declare result tab
    map<int, vector<int>> res = findsolution(inputData);

    // Print results
    vector<float> travelersVar;
    vector<float> travelersMed;
    vector<float> travelerDist;
    for (int i = 0; i < inputData.at("traveler").size(); i++)
    {
        travelersVar.push_back(travelerDistVar(res.at(i), inputData, i));
        travelersMed.push_back(travelerDistMed(res.at(i), inputData, i));
        travelerDist.push_back(travelerDistTotal(res.at(i), inputData, i));
    }
    cout << var(travelersVar) << endl;
    cout << var(travelersMed) << endl;
    cout << var(travelerDist) << endl;
    cout << accumulate(travelerDist.begin(), travelerDist.end(), 0.0) << endl;

    for (int i = 0; i < inputData.at("traveler").size(); i++)
    {
        if (travelerDist[i] > 0)
        {
            cout << travelerDist[i] << ";";
            for (int elem : res.at(i))
            {
                cout << elem << ",";
            }
        }
        else
            cout << "0;-1,";
        cout << endl;
    }

    return 0;
}

vector<int> getNthClosest(int n, vector<double> &arc)
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

vector<int> getRemainingRestaurant(map<int, vector<int>> const &map)
{
    vector<int> remainingRestaurant;
    for (auto i : map)
    {
        remainingRestaurant.push_back(i.first);
    }
    return remainingRestaurant;
}

vector<int> getRemainingClient(map<int, vector<int>> const &map)
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

vector<int> getPossibleNextPeak(vector<double> const &arc, vector<int> const &possiblePoints, int nbClosest)
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

int getIdPoint(vector<int> const &allPoints, vector<double> const &distances)
{
    vector<double> weights;
    vector<double> normalized_weights;
    double min_val;
    double max_val;

    for (double i = 0; i < allPoints.size(); i++)
    {
        weights.push_back(distances[i]);
    }
    //normalizing weights
    min_val = *min_element(weights.begin(), weights.end());
    max_val = *max_element(weights.begin(), weights.end());
    for (int i = 0; i < weights.size(); ++i)
    {
        if (max_val != min_val)
        {
            normalized_weights.push_back((double)(weights[i] - min_val) / (double)(max_val - min_val));
        }
        else
        {
            normalized_weights.push_back(weights[i]);
        }
    }
    reverse(normalized_weights.begin(), normalized_weights.end());
    double randomValue = (double)rand() / (RAND_MAX);
    for (int i = 0, j = normalized_weights.size()-1; i < normalized_weights.size(); i++, j--)
    {
        if (randomValue <= normalized_weights[i])
        {
            return allPoints[j];  // j replace reverse()
        }
    }
    return -1;
}

map<int, vector<int>> findsolution(json const &input) {
    // build list of unselected peaks
    map<int, vector<int>> restaurantClientLink;
    map<int, vector<int>> deliveries;
    map<int, vector<int>> deliveredByWhom;
    map<int, vector<int>> banedDeliveryman;
    map<int, vector<int>> canBeDelivered;
    vector<double> storages;
    int nbTravelers = input.at("traveler").size();
    //initializing arrays
    for (int i = 0; i < nbTravelers; i++)
    {
        storages.push_back(input.at("traveler").at(i).at("qty"));
        deliveries.insert(make_pair(i, vector<int>()));
        canBeDelivered.insert(make_pair(i, vector<int>()));
        banedDeliveryman.insert(make_pair(i, vector<int>()));
    }

    for (int i = 0; i < input.at("peak").size(); ++i)
    {
        deliveredByWhom.insert(make_pair(i, vector<int>()));
        if (input.at("peak").at(i).at("origin") == 1)
        {
            vector<int> clients;
            for (int j = 0; j < input.at("peak").at(i).at("link").size(); j++)
            {
                clients.push_back(input.at("peak").at(i).at("link").at(j));
            }
            restaurantClientLink.insert(pair<int, vector<int>>(i, clients));
        }
    }

    //initialize storage's capacity

    // int storage = input->at("traveler").at(idTraveler).at("qty");

    // int solutionId = 0;
    bool solutionFound = false;
    // int idPoint = -1;
    vector<int> possiblePoints;
    vector<int> tmpPossiblePoints;
    int point;
    int idPoint = -1;
    int idTraveler;
    bool allEmpty = true;
    // select first restaurant
    do
    {
        //clear deliverByWhom
        for (map<int, vector<int>>::iterator it = deliveredByWhom.begin(); it != deliveredByWhom.end(); it++)
        {
            it->second.clear();
        }
        for (int i = 0; i < nbTravelers; i++)
        {
            possiblePoints.clear();
            tmpPossiblePoints = getRemainingRestaurant(restaurantClientLink);
            if (!canBeDelivered.at(i).empty())
            {
                //case the deliver hasnt moved yet
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canBeDelivered.at(i).begin(), canBeDelivered.at(i).end());
            }

            for(auto tmpPoint: banedDeliveryman.at(i)){
                if(find(tmpPossiblePoints.begin(), tmpPossiblePoints.end(), tmpPoint) != tmpPossiblePoints.end()){
                    tmpPossiblePoints.erase(find(tmpPossiblePoints.begin(), tmpPossiblePoints.end(), tmpPoint));
                }
            }
            if(deliveries.at(i).empty()){
                possiblePoints = getPossibleNextPeak(input.at("traveler").at(i).at("arc"), tmpPossiblePoints, tmpPossiblePoints.size());
            }else{
                int curPoint = deliveries.at(i).at(deliveries.at(i).size()-1);
                possiblePoints = getPossibleNextPeak(input.at("arc").at(curPoint), tmpPossiblePoints, tmpPossiblePoints.size());
            }
            
            if (possiblePoints.empty())
            {
                continue;
            }
            vector<double> distances;
            if(deliveries.at(i).empty()){
                for(int tmpPoint: possiblePoints){
                    distances.push_back(input.at("traveler").at(i).at("arc").at(tmpPoint));
                }
            }else{
                int curPoint = deliveries.at(i).at(deliveries.at(i).size()-1);
                for(int tmpPoint: possiblePoints){
                    distances.push_back(input.at("arc").at(curPoint).at(tmpPoint));
                }
            }
            point = getIdPoint(possiblePoints, distances);
            if (point >= 0)
            {
                deliveredByWhom.at(point).push_back(i);
            }
        }
        for (map<int, vector<int>>::iterator it = deliveredByWhom.begin(); it != deliveredByWhom.end(); it++)
        {
            solutionFound = false;
            if (it->second.empty())
            {
                continue;
            }
            vector<double> distances;
            for (int curDeliver : it->second)
            {
                if (deliveries.at(curDeliver).empty())
                {
                    distances.push_back(input.at("traveler").at(curDeliver).at("arc").at(it->first));
                }
                else
                {
                    distances.push_back(input.at("arc").at(deliveries.at(curDeliver)[deliveries.at(curDeliver).size() - 1]).at(it->first));
                }
            }
            
            possiblePoints = getPossibleNextPeak(distances, it->second, it->second.size());
            if (possiblePoints.empty())
            {
                continue;
            }

            idTraveler = getIdPoint(possiblePoints, distances);
            idPoint = it->first;

            if (input.at("peak").at(point).at("origin") == 1 && restaurantClientLink.find(idPoint) != restaurantClientLink.end())
            {
                //if point is a restaurant check every clients of this restaurant
                for (int client : restaurantClientLink.at(idPoint))
                {
                    if (storages[idTraveler] - (int)input.at("peak").at(client).at("qty") >= 0)
                    {
                        /*
                        if deliveryman can store the order, we add this restaurant to the path and this client to 
                        the client that can be delivered and we reduce the storage space.
                    */
                        solutionFound = true;
                        storages[idTraveler] -= (int)input.at("peak").at(client).at("qty");
                        deliveries.at(idTraveler).push_back(idPoint);
                        canBeDelivered.at(idTraveler).push_back(client);
                        vector<int>::iterator it = find(restaurantClientLink.at(idPoint).begin(), restaurantClientLink.at(idPoint).end(), client);
                        if (it != restaurantClientLink.at(idPoint).end())
                        {
                            restaurantClientLink.at(idPoint).erase(it);
                        }

                        if (restaurantClientLink.at(idPoint).empty())
                        {
                            restaurantClientLink.erase(idPoint);
                        }
                        break;
                    }
                }
            }
            if (input.at("peak").at(idPoint).at("origin") == 0 && find(canBeDelivered.at(idTraveler).begin(), canBeDelivered.at(idTraveler).end(), idPoint) != canBeDelivered.at(idTraveler).end())
            {
                /*
                point is a client ready to be delivered, we remove it from the client ready to be delivered and
                we increase the storage space of the deliveryman
                */
                solutionFound = true;
                storages[idTraveler] += (int)input.at("peak").at(idPoint).at("qty");
                deliveries.at(idTraveler).push_back(idPoint);
                canBeDelivered.at(idTraveler).erase(find(canBeDelivered.at(idTraveler).begin(), canBeDelivered.at(idTraveler).end(), idPoint));
            }

            if(!solutionFound){
                banedDeliveryman.at(idTraveler).push_back(idPoint);
            }else{
                banedDeliveryman.at(idTraveler).clear();
            }
        }

        allEmpty = true;
        for (auto k : canBeDelivered)
        {
            if (!k.second.empty())
            {
                allEmpty = false;
                break;
            }
        }
    } while (!(restaurantClientLink.empty()) || !allEmpty);
    return deliveries;
}
