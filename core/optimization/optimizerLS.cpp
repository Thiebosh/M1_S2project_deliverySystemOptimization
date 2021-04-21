#include <iostream>
#include <stdlib.h>
#include <math.h>
#include <vector>
#include <map>
#include <algorithm>
#include <fstream>
#include <streambuf>
#include "..\json.hpp"
#include "..\kpi.hpp"
#include "common.hpp"

using namespace std;
using json = nlohmann::json;


void findnei(vector<int> &solution, json const &input, int const path_id, bool back_origin, int trav_id);


int main(int argc, char* argv[]) {
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc < NB_ARGS) return -1;

    srand(atoi(argv[ARG_SEED])); // reuse seed

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    json inputData = json::parse((std::istreambuf_iterator<char>(t)), (std::istreambuf_iterator<char>()));

    json path_list = json::parse(argv[ARG_PATH]);
    json best_path_list = path_list;

    bool back_origin = atoi(argv[ARG_BACK_ORIGIN]) == 1;
    int nb_tries = atoi(argv[ARG_TRIES]);

    // search for each traveler path
    for (int path_id = 0; path_id < best_path_list.size(); path_id++) {
        if (best_path_list.at(path_id).size() <= 2) continue; //not enough vertices

        vector<int> currentpath = best_path_list.at(path_id);

        for (int i = 0; i < nb_tries; i++) {
            findnei(currentpath, inputData, path_id, back_origin, path_id);
        }

        best_path_list.at(path_id) = currentpath;
    }

    print_results(inputData, path_list, best_path_list, back_origin);

    return 0;
}


void findnei(vector<int> &solution, json const &input, int const path_id, bool back_origin, int trav_id) {
    vector<int> bestnei = solution;

    for(int a = 0; a < solution.size(); a++){    
        for (int i = 0; i < solution.size() && i != a; i++) {
            vector<int> nei = bestnei;
            swap(nei[a], nei[i]);

            double before = travelerDistTotal(bestnei, input, path_id, back_origin);
            double after = travelerDistTotal(nei, input, path_id, back_origin);

            if (checknei(nei, input, trav_id) && before > after) bestnei = nei;
        }
    }

    solution = bestnei;
}
