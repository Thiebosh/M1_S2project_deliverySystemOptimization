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
#define ARG_SEED 1
#define ARG_MATRIX 2
#define NB_ARGS 3

using namespace std;

typedef struct dist_
{
    int id;
    float distance;
} dist;


int main(int argc, char *argv[])
{
    if (argc < NB_ARGS) return -1;

    srand(time_t(argv[ARG_SEED]));

    json jsonData = json::parse(argv[ARG_MATRIX]);
    json* inputData = &jsonData;

    vector<int> idPath(inputData->at(0).size());

    for(int i = 0; i < inputData->at(0).size(); ++i) cout << i << ',';

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
