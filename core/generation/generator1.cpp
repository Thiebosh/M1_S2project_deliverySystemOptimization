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

    left.erase(remove(left.begin(), left.end(), curPoint), left.end());

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
        // cout << "START WHILE" << endl;
        //clear deliverByWhom
        for (map<int, vector<int>>::iterator it = deliveredByWhom.begin(); it != deliveredByWhom.end(); it++)
        {
            it->second.clear();
        }

        for (int i = 0; i < nbTravelers; i++)
        {
            // cout << "ppppp" << endl;
            possiblePoints.clear();
            tmpPossiblePoints = getRemainingRestaurant(restaurantClientLink);
            if (!canBeDelivered.at(i).empty())
            {
                //case the deliver hasnt moved yet
                tmpPossiblePoints.insert(tmpPossiblePoints.end(), canBeDelivered.at(i).begin(), canBeDelivered.at(i).end());
            }
            // cout << "qqqqq" << endl;

            // for (auto tmpPoint : banedDeliveryman.at(i))
            // {
            //     if (find(tmpPossiblePoints.begin(), tmpPossiblePoints.end(), tmpPoint) != tmpPossiblePoints.end())
            //     {
            //         tmpPossiblePoints.erase(find(tmpPossiblePoints.begin(), tmpPossiblePoints.end(), tmpPoint));
            //     }
            // }

            if (deliveries.at(i).empty())
            {
                vector<double> distances;
                for (auto j : tmpPossiblePoints)
                {
                    distances.push_back(input.at("traveler").at(i).at("arc").at(j));
                }
                possiblePoints = getPossibleNextPeak(distances, tmpPossiblePoints, tmpPossiblePoints.size());
                // cout << "possiblePoints" << endl;
                // for(auto i: possiblePoints){
                //     cout << i << ", ";
                // }
                // cout << endl; 
            }
            else
            {
                int curPoint = deliveries.at(i).at(deliveries.at(i).size() - 1);
                vector<double> distances;
                for (auto j : tmpPossiblePoints)
                {
                    distances.push_back(input.at("arc").at(curPoint).at(j));
                }
                possiblePoints = getPossibleNextPeak(distances, tmpPossiblePoints, tmpPossiblePoints.size());
            }

            // cout << "rrrrrr" << endl;

            if (possiblePoints.empty())
            {
                continue;
            }
            // cout << "99999999" << endl;

            vector<double> distances;
            if (deliveries.at(i).empty())
            {
                // cout << "8888888" << endl;
                for (int tmpPoint : possiblePoints)
                {
                    double dist = input.at("traveler").at(i).at("arc").at(tmpPoint);
                    // vector<int> left(possiblePoints);
                    // cout << "aaa" << endl;
                    // dist += computeRecurDistance(deepRecur, input.at("arc"), left, tmpPoint);
                    // cout << "bbb" << endl;
                    distances.push_back(dist);
                }
            }
            else
            {
                // cout << "777777777" << endl;
                int curPoint = deliveries.at(i).at(deliveries.at(i).size() - 1);
                for (int tmpPoint : possiblePoints)
                {
                    double dist = input.at("arc").at(curPoint).at(tmpPoint);
                    // vector<int> left(possiblePoints);
                    // dist += computeRecurDistance(deepRecur, input.at("arc"), left, tmpPoint);
                    distances.push_back(dist);
                }
            }
            // cout << "sssssss" << endl;

            point = getIdPoint(possiblePoints, distances);
            if (point >= 0)
            {
                deliveredByWhom.at(point).push_back(i);
            }
        }
        // cout << "DELIVERD BY WHOM" << endl;
        // for(auto k: deliveredByWhom){
        //     cout << k.first<<": ";
        //     for(auto r: k.second){
        //         cout << r <<", ";
        //     }
        //     cout << endl;
        // }

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
                    distances.push_back(input.at("traveler").at(curDeliver).at("arc").at(it->first));
                }
                else
                {
                    distances.push_back(input.at("arc").at(deliveries.at(curDeliver).at(deliveries.at(curDeliver).size() - 1)).at(it->first));
                }
            }

            possiblePoints = getPossibleNextPeak(distances, it->second, it->second.size());

            if (possiblePoints.empty())
            {
                continue;
            }

            idTraveler = getIdPoint(possiblePoints, distances);
            idPoint = it->first;
            // cout << "aaaa" << endl;
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
                        // cout <<"CLIENT " << client << endl;
                        tmpDeliveries.push_back(idTraveler);
                        tmpDeliveries.push_back(idPoint);
                        tmpDeliveries.push_back(client);
                        break;
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
        // cout << "test" << endl;
        double avg = 0;
        int nbPoint = 0;
        // cout << "TMP DELIVERIES" << endl;
        // for(auto i: tmpDeliveries){
        //     cout << i <<", ";
        // }
        // cout << endl;
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
        // cout << "le gang" << endl;
        for (int i = 0; i < tmpDeliveries.size(); i += 2)
        {
            idTraveler = tmpDeliveries.at(i);
            idPoint = tmpDeliveries.at(i+1);
            if (deliveries.at(idTraveler).empty())
            {
                avg += (double)input.at("traveler").at(idTraveler).at("arc").at(idPoint);
                nbPoint++;
            }
            else
            {
                int lastPoint = deliveries.at(idTraveler).at(deliveries.at(idTraveler).size()-1);
                avg += (double)input.at("arc").at(lastPoint).at(idPoint);
                nbPoint++;
            }
            if (input.at("peak").at(tmpDeliveries.at(i + 1)).at("origin") == 1)
            {
                i += 1;
            }
        }
        avg = avg / nbPoint;
        // cout << "avg: " << avg << endl;



        // cout << "DELIVERIES" << endl;
        // for (auto i : deliveries)
        // {
        //     cout << "Traveler" << i.first << ": ";
        //     for (auto j : i.second)
        //     {
        //         cout << j << ", ";
        //     }
        //     cout << endl;
        // }

        vector<int> pointsNoSolution;
        int countPoint = 0;
        for (int i = 0; i < tmpDeliveries.size(); i += 2)
        {
            countPoint++;
            solutionFound = false;
            idTraveler = tmpDeliveries.at(i);
            idPoint = tmpDeliveries.at(i + 1);
            // cout << "aaa" << idTraveler << "  " << idPoint << endl;
            double dist;
            if (deliveries.at(idTraveler).empty())
            {
                dist = input.at("traveler").at(idTraveler).at("arc").at(idPoint);
            }
            else
            {
                int lastPoint = deliveries.at(idTraveler).at(deliveries.at(idTraveler).size()-1);
                dist = input.at("arc").at(lastPoint).at(idPoint);
            }
            if (dist < avg)
            {
                deliveries.at(idTraveler).push_back(idPoint);
                solutionFound = true;
                if (input.at("peak").at(idPoint).at("origin") == 1)
                {
                    // cout << "case resto" << endl;
                    int client = tmpDeliveries.at(i + 2);
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
                    // cout << "case client" << endl;
                    storages[idTraveler] += (int)input.at("peak").at(idPoint).at("qty");
                    canBeDelivered.at(idTraveler).erase(find(canBeDelivered.at(idTraveler).begin(), canBeDelivered.at(idTraveler).end(), idPoint));
                }
                banedDeliveryman.at(idTraveler).clear();
            }
            // cout << "dddd" << endl;
            if (!solutionFound)
            {
                pointsNoSolution.push_back(i);
            }

            // cout << "ffff" << endl;
            if (input.at("peak").at(idPoint).at("origin") == 1)
            {
                i += 1;
            }
            // cout << "ggggg" << endl;
        }

        if (pointsNoSolution.size() == countPoint && !tmpDeliveries.empty())
        {
            // cout << "NO SOL FOUND" << endl;
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
                    int lastPoint = deliveries.at(idTraveler).at(deliveries.at(idTraveler).size()-1);
                    dists.push_back(input.at("arc").at(lastPoint).at(idPoint));
                }
            }
            // cout << "1111111" << endl;
            int id = pointsNoSolution.at(min_element(dists.begin(), dists.end()) - dists.begin());
            // cout << "aaaa" << endl;
            idTraveler = tmpDeliveries.at(id);
            idPoint = tmpDeliveries.at(id + 1);
            // cout << "bbbbb" << endl;
            deliveries.at(idTraveler).push_back(idPoint);
            // cout << "ccccc" << endl;
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
                // cout << "case client" << endl;
                storages[idTraveler] += (int)input.at("peak").at(idPoint).at("qty");
                canBeDelivered.at(idTraveler).erase(find(canBeDelivered.at(idTraveler).begin(), canBeDelivered.at(idTraveler).end(), idPoint));
            }
            // banedDeliveryman.at(idTraveler).clear();
            // cout << "NO SOL FOUND END" << endl;
        }
        tmpDeliveries.clear();
        pointsNoSolution.clear();
        // cout << "BANNED DELIVERY MAN" << endl;
        // for(auto k: banedDeliveryman){
        //     cout << k.first<<": ";
        //     for(auto r: k.second){
        //         cout << r << ", ";
        //     }
        //     cout << endl;
        // }
        allEmpty = true;
        for (auto k : canBeDelivered)
        {

            if (!k.second.empty())
            {
                allEmpty = false;
                break;
            }
        }

        // cout << "END WHILE " << endl;
    } while (!(restaurantClientLink.empty()) || !allEmpty);
    return deliveries;
}
