#include <iostream>
#include <fstream>
#include <time.h>
#include <vector>
#include <map>
#include "..\json.hpp"
#include "..\kpi.hpp"

//input args
#define ARG_ID 1
#define ARG_SEED 2
#define ARG_FILE_PATH 3
#define ARG_PATH 4
#define ARG_TRIES 5
#define ARG_BACK_ORIGIN 6
#define NB_ARGS 7

using namespace std;
using json = nlohmann::json;


void initalize(int argc, char *argv[], json &inputData, json &path_list, int &nb_tries, bool &back_origin) {
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc < NB_ARGS)
        exit(-1);

    srand(atoi(argv[ARG_SEED])); // reuse seed

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    inputData = json::parse((istreambuf_iterator<char>(t)), (istreambuf_iterator<char>()));

    path_list = json::parse(argv[ARG_PATH]);
    // json best_path_list = path_list;

    nb_tries = atoi(argv[ARG_TRIES]);
    back_origin = atoi(argv[ARG_BACK_ORIGIN]) == 1;
}

bool checknei(vector<int> const &solution, json const &input, int trav_id) {
    vector<int> ableclient(input["peak"].size(), 0);
    int storage = input["traveler"][trav_id]["qty"];

    for (int i = 0; i < solution.size(); i++) {
        if (input["peak"][solution[i]]["origin"] == 1) {
            if (!storage) return false;
            int j = 0;
            // reduce here by quantity ordered by client ?
            while(j++ < input["peak"][solution[i]]["link"].size() && storage-- > 0) {
                ableclient[solution[i]]++;
            }
        }

        if (input["peak"][solution[i]]["origin"] == 0) {
            storage++; // input["peak"][solution[i]]["qty"]
            int position = input["peak"][solution[i]]["link"];
            if(ableclient[position] > 0) ableclient[position]--;
            else return false;
        }
    }

    return true;
}


void print_results(json const &inputData, json const &path_list, json const &best_path_list, bool back_origin) {
    vector<float> travelerDist;
    for (int i = 0; i < path_list.size(); i++)
    {
        if (path_list[i][0] == -1) continue;
        travelerDist.push_back(travelerDistTotal(path_list[i], inputData, i, back_origin));
    }
    double scoreBefore = accumulate(travelerDist.begin(), travelerDist.end(), 0.0);

    travelerDist.clear();
    for (int i = 0; i < path_list.size(); i++)
    {
        if (best_path_list[i][0] == -1) travelerDist.push_back(0);
        else travelerDist.push_back(travelerDistTotal(best_path_list[i], inputData, i, back_origin));
    }
    double scoreAfter = accumulate(travelerDist.begin(), travelerDist.end(), 0.0);

    if (scoreBefore < scoreAfter) {
        cout << false << endl;
        return;
    }

    cout << true << endl;
    print_kpis(travelerDist);
    for (int i = 0; i < best_path_list.size(); i++)
    {
        if (travelerDist[i] > 0)
        {
            cout << travelerDist[i] << ";";
            for (int elem : best_path_list[i])
            {
                cout << elem << ",";
            }
        }
        else
            cout << "0;-1,";
        cout << endl;
    }
}
