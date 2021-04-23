#include <iostream>
#include <fstream>
#include <time.h>
#include <vector>
#include <map>
#include "..\json.hpp"
#include "..\kpi.hpp"

//input args
#define ARG_ID 1
#define ARG_RECUR 2
#define ARG_BACK_ORIGIN 3
#define ARG_FILE_PATH 4
#define NB_ARGS 5

using namespace std;
using json = nlohmann::json;


json initalize(int argc, char *argv[]) {
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc < NB_ARGS)
        exit(-1);

    time_t seed = time(NULL) % id;
    srand(seed);
    cout << seed << endl;

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    return json::parse((istreambuf_iterator<char>(t)), (istreambuf_iterator<char>()));
}

void print_results(json const &inputData, map<int, vector<int>> const &res, bool back_origin) {
    vector<float> travelerDist;
    for (int i = 0; i < inputData.at("traveler").size(); i++)
    {
        travelerDist.push_back(travelerDistTotal(res.at(i), inputData, i, back_origin));
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
                if (elem == prevElem)
                    continue;
                cout << elem << ",";
                prevElem = elem;
            }
        }
        else
            cout << "0;-1,";
        cout << endl;
    }
}