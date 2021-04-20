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


void findnei(vector<int> &bestsolution,vector<int> &solution, json const &input, int const path_id, int t, bool back_origin);


int main(int argc, char* argv[]) {
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc != NB_ARGS) return -1;

    srand(atoi(argv[ARG_SEED])); // reuse seed

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    json inputData = json::parse((std::istreambuf_iterator<char>(t)), (std::istreambuf_iterator<char>()));

    json path_list = json::parse(argv[ARG_PATH]);
    json best_path_list = path_list;

    bool back_origin = atoi(argv[ARG_BACK_ORIGIN]) == 1;

    // search for each traveler path
    for (int path_id = 0; path_id < path_list.size(); path_id++) {
        if (path_list.at(path_id).size() <= 2) continue; //not enough vertices

        vector<int> currentpath = path_list.at(path_id);
        vector<int> bestpath = currentpath;

        double q = 0.99;
        double t_end = 1e-8;
        int t1 = 1000;

        while (t1 > t_end) {
            for (int i = 0; i < atoi(argv[ARG_TRIES]); i++) {
                findnei(bestpath, currentpath, inputData, path_id, t1, back_origin);
            }
            t1 *= q;
        }

        best_path_list[path_id] = bestpath;
    }

    print_results(inputData, path_list, best_path_list, back_origin);
    
    return 0;
}


void findnei(vector<int> &bestsolution, vector<int> &solution, json const &input, int const path_id, int t, bool back_origin) {
    vector<int> nei = solution;
    swap(nei[rand() % solution.size()], nei[rand() % solution.size()]);

    if (checknei(nei, input)) {
        float dis = travelerDistTotal(nei, input, path_id, back_origin);
        float dis_solu = travelerDistTotal(solution, input, path_id, back_origin);

        if (dis < travelerDistTotal(solution, input, path_id, back_origin)) {
            solution = nei;
            bestsolution = nei;
        }
        else if (exp(-(dis - dis_solu) / t) <= (rand() % 100 + 1) / 100) {
            bestsolution = solution;
            solution = nei;
        }
    }
}
