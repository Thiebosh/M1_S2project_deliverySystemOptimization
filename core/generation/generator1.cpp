#include <iostream>
#include <time.h>
#include <fstream>
#include <vector>
#include <map>
#include "..\json.hpp"
#include "..\heuristic.hpp"
#include "..\kpi.hpp"

//input args
#define ARG_ID 1
#define ARG_RECUR 2
#define ARG_BACK_ORIGIN 3
#define ARG_FILE_PATH 4
#define NB_ARGS 5

using namespace std;
using json = nlohmann::json;

// definitions
vector<int> getRemainingRestaurant(map<int, vector<int>> const &map);

vector<int> getRemainingClient(map<int, vector<int>> const &map);

double computeRecurDistance(int deep, vector<vector<double>> const &distMatrix, vector<int> &left, int curPoint);

map<int, vector<int>> findsolution(json const &input, int deepRecur);

// main function
int main(int argc, char *argv[])
{
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc < NB_ARGS)
        return -1;

    time_t seed = time(NULL) % id;
    // seed = time_t(10);
    srand(seed);
    cout << seed << endl;

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    json inputData = json::parse((istreambuf_iterator<char>(t)), (istreambuf_iterator<char>()));

    // declare result tab
    map<int, vector<int>> res = findsolution(inputData, atoi(argv[ARG_RECUR]));

    // Print results
    vector<float> travelerDist;
    for (int i = 0; i < inputData.at("traveler").size(); i++)
    {
        travelerDist.push_back(travelerDistTotal(res.at(i), inputData, i, atoi(argv[ARG_BACK_ORIGIN]) == 1));
    }

    print_kpis(travelerDist);
    int prevElem = -1;
    for (int i = 0; i < inputData.at("traveler").size(); i++)
    {
        if (travelerDist[i] > 0)
        {
            cout << travelerDist[i] << ";";
            for (int elem : res.at(i))
            {
                if (elem != prevElem)
                {
                    cout << elem << ",";
                }
                prevElem = elem;
            }
        }
        else
            cout << "0;-1,";
        cout << endl;
    }

    return 0;
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

double computeRecurDistance(int deep, vector<vector<double>> const &distMatrix, vector<int> &left, int curPoint)
{
    if (!deep || left.size() <= 1 || curPoint == -1)
        return 0;

    left.erase(find(left.begin(), left.end(), curPoint));

    vector<double> distances;
    for (int tmpPoint : left)
    {
        distances.push_back(distMatrix[curPoint][tmpPoint]);
    }

    int nextPoint = getIdPoint(left, distances);

    return distances[nextPoint] + computeRecurDistance(deep - 1, distMatrix, left, nextPoint);
}

map<int, vector<int>> findsolution(json const &input, int deepRecur)
{
    // build list of unselected peaks
    map<int, vector<int>> restaurantClientLink;
    map<int, vector<int>> deliveries;
    map<int, vector<int>> deliveredByWhom;
    map<int, vector<int>> banedDeliveryman;
    map<int, vector<int>> canBeDelivered;
    vector<double> storages;
    vector<int> tmpDeliveries;
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

            if (deliveries.at(i).empty())
            {
                vector<double> distances;
                for (auto j : tmpPossiblePoints)
                {

                    double dist = input.at("traveler").at(i).at("arc").at(j);
                    // dist += computeRecurDistance(deepRecur, input.at("arc"), possiblePoints, j);
                    distances.push_back(dist);
                }
                possiblePoints = getPossibleNextPeak(distances, tmpPossiblePoints, tmpPossiblePoints.size());
            }
            else
            {
                int curPoint = deliveries.at(i).at(deliveries.at(i).size() - 1);
                vector<double> distances;
                for (auto j : tmpPossiblePoints)
                {
                    double dist = input.at("arc").at(curPoint).at(j);
                    // dist += computeRecurDistance(deepRecur, input.at("arc"), possiblePoints, j);
                    distances.push_back(dist);
                }
                possiblePoints = getPossibleNextPeak(distances, tmpPossiblePoints, tmpPossiblePoints.size());
            }

            if (possiblePoints.empty())
            {
                continue;
            }

            vector<double> distances;
            if (deliveries.at(i).empty())
            {
                for (int tmpPoint : possiblePoints)
                {
                    double dist = input.at("traveler").at(i).at("arc").at(tmpPoint);
                    // dist += computeRecurDistance(deepRecur, input.at("arc"), possiblePoints, tmpPoint);
                    distances.push_back(dist);
                }
            }
            else
            {
                int curPoint = deliveries.at(i).at(deliveries.at(i).size() - 1);
                for (int tmpPoint : possiblePoints)
                {
                    double dist = input.at("arc").at(curPoint).at(tmpPoint);
                    // dist += computeRecurDistance(deepRecur, input.at("arc"), possiblePoints, tmpPoint);
                    distances.push_back(dist);
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
            if (it->second.empty())
            {
                continue;
            }
            vector<double> distances;
            for (int curDeliver : it->second)
            {
                if (deliveries.at(curDeliver).empty())
                {
                    double dist = input.at("traveler").at(curDeliver).at("arc").at(it->first);
                    distances.push_back(dist);
                }
                else
                {
                    double dist = input.at("arc").at(deliveries.at(curDeliver).at(deliveries.at(curDeliver).size() - 1)).at(it->first);
                    distances.push_back(dist);
                }
            }

            possiblePoints = getPossibleNextPeak(distances, it->second, it->second.size());

            if (possiblePoints.empty())
            {
                continue;
            }

            distances.clear();
            for (int curDeliver : possiblePoints)
            {
                if (deliveries.at(curDeliver).empty())
                {
                    distances.push_back(input.at("traveler").at(curDeliver).at("arc").at(it->first));
                }
                else
                {
                    distances.push_back(input.at("arc").at(deliveries.at(curDeliver).at(deliveries.at(curDeliver).size() - 1)).at(it->first));
                }
            }

            idTraveler = getIdPoint(possiblePoints, distances);
            idPoint = it->first;
            if (input.at("peak").at(idPoint).at("origin") == 1 && restaurantClientLink.find(idPoint) != restaurantClientLink.end())
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
                        tmpDeliveries.push_back(idTraveler);
                        tmpDeliveries.push_back(idPoint);
                        tmpDeliveries.push_back(client);
                    }
                }
            }
            if (input.at("peak").at(idPoint).at("origin") == 0)
            {
                /*
                point is a client ready to be delivered, we remove it from the client ready to be delivered and
                we increase the storage space of the deliveryman
                */
                tmpDeliveries.push_back(idTraveler);
                tmpDeliveries.push_back(idPoint);
            }
        }

        //check avg;
        double avg = 0;
        int nbPoint = 0;

        for (map<int, vector<int>>::iterator i = deliveries.begin(); i != deliveries.end(); i++)
        {
            if (i->second.empty())
                continue;
            avg += (double)input.at("traveler").at(i->first).at("arc").at(i->second.at(0));
            for (auto j = 1; j < i->second.size(); j++)
            {
                avg += (double)input.at("arc").at(i->second.at(j - 1)).at(i->second.at(j));
                nbPoint++;
            }
        }
        for (int i = 0; i < tmpDeliveries.size(); i += 2)
        {
            idTraveler = tmpDeliveries.at(i);
            idPoint = tmpDeliveries.at(i + 1);
            if (deliveries.at(idTraveler).empty())
            {
                avg += (double)input.at("traveler").at(idTraveler).at("arc").at(idPoint);
                nbPoint++;
            }
            else
            {
                int lastPoint = deliveries.at(idTraveler).at(deliveries.at(idTraveler).size() - 1);
                avg += (double)input.at("arc").at(lastPoint).at(idPoint);
                nbPoint++;
            }
            if (input.at("peak").at(tmpDeliveries.at(i + 1)).at("origin") == 1)
            {
                i += 1;
            }
        }
        avg = avg / nbPoint;

        vector<int> pointsNoSolution;
        int countPoint = 0;
        for (int i = 0; i < tmpDeliveries.size(); i += 2)
        {
            countPoint++;
            solutionFound = false;
            idTraveler = tmpDeliveries.at(i);
            idPoint = tmpDeliveries.at(i + 1);
            double dist;
            if (deliveries.at(idTraveler).empty())
            {
                dist = input.at("traveler").at(idTraveler).at("arc").at(idPoint);
                // dist += computeRecurDistance(deepRecur, input.at("arc"), possiblePoints, idPoint);
            }
            else
            {
                int lastPoint = deliveries.at(idTraveler).at(deliveries.at(idTraveler).size() - 1);
                dist = input.at("arc").at(lastPoint).at(idPoint);
            }
            if (dist < avg)
            {
                if (input.at("peak").at(idPoint).at("origin") == 1)
                {
                    int client = tmpDeliveries.at(i + 2);
                    solutionFound = true;
                    if (storages[idTraveler] - (int)input.at("peak").at(client).at("qty") >= 0)
                    {
                        deliveries.at(idTraveler).push_back(idPoint);
                        storages[idTraveler] -= (int)input.at("peak").at(client).at("qty");
                        canBeDelivered.at(idTraveler).push_back(client);
                        vector<int>::iterator it2 = find(restaurantClientLink.at(idPoint).begin(), restaurantClientLink.at(idPoint).end(), client);
                        if (it2 != restaurantClientLink.at(idPoint).end())
                        {
                            restaurantClientLink.at(idPoint).erase(it2);
                        }

                        if (restaurantClientLink.at(idPoint).empty())
                        {
                            restaurantClientLink.erase(idPoint);
                        }
                    }
                }
                else if (input.at("peak").at(idPoint).at("origin") == 0)
                {
                    deliveries.at(idTraveler).push_back(idPoint);
                    solutionFound = true;
                    storages[idTraveler] += (int)input.at("peak").at(idPoint).at("qty");
                    canBeDelivered.at(idTraveler).erase(find(canBeDelivered.at(idTraveler).begin(), canBeDelivered.at(idTraveler).end(), idPoint));
                }
                banedDeliveryman.at(idTraveler).clear();
            }
            if (!solutionFound)
            {
                pointsNoSolution.push_back(i);
            }

            if (input.at("peak").at(idPoint).at("origin") == 1)
            {
                i += 1;
            }
        }

        if (pointsNoSolution.size() == countPoint && !tmpDeliveries.empty())
        {
            vector<double> dists;
            for (auto i : pointsNoSolution)
            {
                idTraveler = tmpDeliveries.at(i);
                idPoint = tmpDeliveries.at(i + 1);
                if (deliveries.at(idTraveler).empty())
                {
                    dists.push_back(input.at("traveler").at(idTraveler).at("arc").at(idPoint));
                }
                else
                {
                    int lastPoint = deliveries.at(idTraveler).at(deliveries.at(idTraveler).size() - 1);
                    dists.push_back(input.at("arc").at(lastPoint).at(idPoint));
                }
            }
            int id = pointsNoSolution.at(min_element(dists.begin(), dists.end()) - dists.begin());
            idTraveler = tmpDeliveries.at(id);
            idPoint = tmpDeliveries.at(id + 1);
            deliveries.at(idTraveler).push_back(idPoint);
            if (input.at("peak").at(idPoint).at("origin") == 1)
            {
                int client = tmpDeliveries.at(id + 2);
                storages[idTraveler] -= (int)input.at("peak").at(client).at("qty");
                canBeDelivered.at(idTraveler).push_back(client);
                vector<int>::iterator it2 = find(restaurantClientLink.at(idPoint).begin(), restaurantClientLink.at(idPoint).end(), client);
                if (it2 != restaurantClientLink.at(idPoint).end())
                {
                    restaurantClientLink.at(idPoint).erase(it2);
                }

                if (restaurantClientLink.at(idPoint).empty())
                {
                    restaurantClientLink.erase(idPoint);
                }
            }
            else if (input.at("peak").at(idPoint).at("origin") == 0)
            {
                storages[idTraveler] += (int)input.at("peak").at(idPoint).at("qty");
                canBeDelivered.at(idTraveler).erase(find(canBeDelivered.at(idTraveler).begin(), canBeDelivered.at(idTraveler).end(), idPoint));
            }
        }
        tmpDeliveries.clear();
        pointsNoSolution.clear();

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
