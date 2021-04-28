#include <vector>
#include <map>
#include "..\json.hpp"
#include "..\heuristic.hpp"
#include "common.hpp"

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
    json inputData;
    int recurs;
    bool back_origin;
    initalize(argc, argv, inputData, recurs, back_origin);

    // declare result tab
    map<int, vector<int>> res = findsolution(inputData, recurs);

    print_results(inputData, res, back_origin);

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
    int nbTravelers = input["traveler"].size();
    //initializing arrays
    for (int i = 0; i < nbTravelers; i++)
    {
        storages.push_back(input["traveler"][i]["qty"]);
        deliveries.insert(make_pair(i, vector<int>()));
        canBeDelivered.insert(make_pair(i, vector<int>()));
        banedDeliveryman.insert(make_pair(i, vector<int>()));
    }

    for (int i = 0; i < input["peak"].size(); ++i)
    {
        deliveredByWhom.insert(make_pair(i, vector<int>()));
        if (input["peak"][i]["origin"] == 1)
        {
            vector<int> clients;
            for (int j = 0; j < input["peak"][i]["link"].size(); j++)
            {
                clients.push_back(input["peak"][i]["link"][j]);
            }
            restaurantClientLink.insert(pair<int, vector<int>>(i, clients));
        }
    }

    //initialize storage's capacity

    // int storage = input->at("traveler")[idTraveler]["qty"];

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
            if (!canBeDelivered[i].empty())
            {
                //case the deliver hasnt moved yet
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canBeDelivered[i].begin(), canBeDelivered[i].end());
            }

            if (deliveries[i].empty())
            {
                vector<double> distances;
                for (auto j : tmpPossiblePoints)
                {
                    double dist = input["traveler"][i]["arc"][j];
                    vector<int> left(tmpPossiblePoints);
                    dist += computeRecurDistance(deepRecur, input["arc"], left, j);
                    distances.push_back(input["traveler"][i]["arc"][j]);
                }
                possiblePoints = getPossibleNextPeak(distances, tmpPossiblePoints);
            }
            else
            {
                int curPoint = deliveries[i][deliveries[i].size() - 1];
                vector<double> distances;
                for (auto j : tmpPossiblePoints)
                {
                    double dist = input["arc"][curPoint][j];
                    vector<int> left(tmpPossiblePoints);
                    dist += computeRecurDistance(deepRecur, input["arc"], left, j);
                    distances.push_back(input["arc"][curPoint][j]);
                }
                possiblePoints = getPossibleNextPeak(distances, tmpPossiblePoints);
            }

            if (possiblePoints.empty())
            {
                continue;
            }

            vector<double> distances;
            if (deliveries[i].empty())
            {
                for (int tmpPoint : possiblePoints)
                {
                    double dist = input["traveler"][i]["arc"][tmpPoint];
                    vector<int> left(possiblePoints);
                    dist += computeRecurDistance(deepRecur, input["arc"], left, tmpPoint);
                    distances.push_back(input["traveler"][i]["arc"][tmpPoint]);
                }
            }
            else
            {
                int curPoint = deliveries[i][deliveries[i].size() - 1];
                for (int tmpPoint : possiblePoints)
                {
                    double dist = input["traveler"][i]["arc"][tmpPoint];
                    vector<int> left(possiblePoints);
                    dist += computeRecurDistance(deepRecur, input["arc"], left, tmpPoint);
                    distances.push_back(input["arc"][curPoint][tmpPoint]);
                }
            }

            point = getIdPoint(possiblePoints, distances);
            if (point >= 0)
            {
                deliveredByWhom[point].push_back(i);
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
                if (deliveries[curDeliver].empty())
                {
                    double dist = input["traveler"][curDeliver]["arc"][it->first];
                    distances.push_back(dist);
                }
                else
                {
                    double dist = input["arc"][deliveries[curDeliver][deliveries[curDeliver].size() - 1]][it->first];
                    distances.push_back(dist);
                }
            }

            possiblePoints = getPossibleNextPeak(distances, it->second);

            if (possiblePoints.empty())
            {
                continue;
            }

            distances.clear();
            for (int curDeliver : possiblePoints)
            {
                if (deliveries[curDeliver].empty())
                {
                    distances.push_back(input["traveler"][curDeliver]["arc"][it->first]);
                }
                else
                {
                    distances.push_back(input["arc"][deliveries[curDeliver][deliveries[curDeliver].size() - 1]][it->first]);
                }
            }

            idTraveler = getIdPoint(possiblePoints, distances);
            idPoint = it->first;
            if (input["peak"][idPoint]["origin"] == 1 && restaurantClientLink.find(idPoint) != restaurantClientLink.end())
            {
                //if point is a restaurant check every clients of this restaurant
                for (int client : restaurantClientLink[idPoint])
                {
                    if (storages[idTraveler] - (int)input["peak"][client]["qty"] >= 0)
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
            if (input["peak"][idPoint]["origin"] == 0)
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
            avg += (double)input["traveler"][i->first]["arc"][i->second[0]];
            for (auto j = 1; j < i->second.size(); j++)
            {
                avg += (double)input["arc"][i->second[j - 1]][i->second[j]];
                nbPoint++;
            }
        }
        for (int i = 0; i < tmpDeliveries.size(); i += 2)
        {
            idTraveler = tmpDeliveries[i];
            idPoint = tmpDeliveries[i + 1];
            if (deliveries[idTraveler].empty())
            {
                avg += (double)input["traveler"][idTraveler]["arc"][idPoint];
                nbPoint++;
            }
            else
            {
                int lastPoint = deliveries[idTraveler][deliveries[idTraveler].size() - 1];
                avg += (double)input["arc"][lastPoint][idPoint];
                nbPoint++;
            }
            if (input["peak"][tmpDeliveries[i + 1]]["origin"] == 1)
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
            idTraveler = tmpDeliveries[i];
            idPoint = tmpDeliveries[i + 1];
            double dist;
            if (deliveries[idTraveler].empty())
            {
                dist = input["traveler"][idTraveler]["arc"][idPoint];
                // dist += computeRecurDistance(deepRecur, input["arc"], possiblePoints, idPoint);
            }
            else
            {
                int lastPoint = deliveries[idTraveler][deliveries[idTraveler].size() - 1];
                dist = input["arc"][lastPoint][idPoint];
            }
            if (dist < avg)
            {
                if (input["peak"][idPoint]["origin"] == 1)
                {
                    int client = tmpDeliveries[i + 2];
                    solutionFound = true;
                    if (storages[idTraveler] - (int)input["peak"][client]["qty"] >= 0)
                    {
                        deliveries[idTraveler].push_back(idPoint);
                        storages[idTraveler] -= (int)input["peak"][client]["qty"];
                        canBeDelivered[idTraveler].push_back(client);
                        vector<int>::iterator it2 = find(restaurantClientLink[idPoint].begin(), restaurantClientLink[idPoint].end(), client);
                        if (it2 != restaurantClientLink[idPoint].end())
                        {
                            restaurantClientLink[idPoint].erase(it2);
                        }

                        if (restaurantClientLink[idPoint].empty())
                        {
                            restaurantClientLink.erase(idPoint);
                        }
                    }
                }
                else if (input["peak"][idPoint]["origin"] == 0)
                {
                    deliveries[idTraveler].push_back(idPoint);
                    solutionFound = true;
                    storages[idTraveler] += (int)input["peak"][idPoint]["qty"];
                    canBeDelivered[idTraveler].erase(find(canBeDelivered[idTraveler].begin(), canBeDelivered[idTraveler].end(), idPoint));
                }
                banedDeliveryman[idTraveler].clear();
            }
            if (!solutionFound)
            {
                pointsNoSolution.push_back(i);
            }

            if (input["peak"][idPoint]["origin"] == 1)
            {
                i += 1;
            }
        }

        if (pointsNoSolution.size() == countPoint && !tmpDeliveries.empty())
        {
            vector<double> dists;
            for (auto i : pointsNoSolution)
            {
                idTraveler = tmpDeliveries[i];
                idPoint = tmpDeliveries[i + 1];
                if (deliveries[idTraveler].empty())
                {
                    dists.push_back(input["traveler"][idTraveler]["arc"][idPoint]);
                }
                else
                {
                    int lastPoint = deliveries[idTraveler][deliveries[idTraveler].size() - 1];
                    dists.push_back(input["arc"][lastPoint][idPoint]);
                }
            }
            int id = pointsNoSolution[min_element(dists.begin(), dists.end()) - dists.begin()];
            idTraveler = tmpDeliveries[id];
            idPoint = tmpDeliveries[id + 1];
            deliveries[idTraveler].push_back(idPoint);
            if (input["peak"][idPoint]["origin"] == 1)
            {
                int client = tmpDeliveries[id + 2];
                storages[idTraveler] -= (int)input["peak"][client]["qty"];
                canBeDelivered[idTraveler].push_back(client);
                vector<int>::iterator it2 = find(restaurantClientLink[idPoint].begin(), restaurantClientLink[idPoint].end(), client);
                if (it2 != restaurantClientLink[idPoint].end())
                {
                    restaurantClientLink[idPoint].erase(it2);
                }

                if (restaurantClientLink[idPoint].empty())
                {
                    restaurantClientLink.erase(idPoint);
                }
            }
            else if (input["peak"][idPoint]["origin"] == 0)
            {
                storages[idTraveler] += (int)input["peak"][idPoint]["qty"];
                canBeDelivered[idTraveler].erase(find(canBeDelivered[idTraveler].begin(), canBeDelivered[idTraveler].end(), idPoint));
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
