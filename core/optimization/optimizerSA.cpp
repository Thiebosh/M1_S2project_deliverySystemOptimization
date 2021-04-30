#include <math.h>
#include <vector>
#include <algorithm>
#include "..\json.hpp"
#include "common.hpp"

using namespace std;
using json = nlohmann::json;


void findnei(vector<int> &bestsolution,vector<int> &solution, json const &input, int const path_id, int t, bool back_origin, int trav_id);


int main(int argc, char* argv[]) {
    json inputData, path_list;
    int nb_tries;
    bool back_origin;
    initalize(argc, argv, inputData, path_list, nb_tries, back_origin);

    json best_path_list = path_list;

    // search for each traveler path
    for (int path_id = 0; path_id < path_list.size(); path_id++) {
        if (path_list[path_id].size() <= 2) continue; //not enough vertices

        vector<int> currentpath = path_list[path_id];
        vector<int> bestpath = currentpath;

        double q = 0.99;
        double t_end = 1e-8;
        int t1 = 1000;

        while (t1 > t_end) {
            for (int i = 0; i < nb_tries; i++) {
                findnei(bestpath, currentpath, inputData, path_id, t1, back_origin, path_id);
            }
            t1 *= q;
        }

        best_path_list[path_id] = bestpath;
    }

    print_results(inputData, path_list, best_path_list, back_origin);
    
    return 0;
}


void findnei(vector<int> &bestsolution, vector<int> &solution, json const &input, int const path_id, int t, bool back_origin, int trav_id) {
    vector<int> nei = solution;
    swap(nei[rand() % solution.size()], nei[rand() % solution.size()]);

    if (checknei(nei, input, trav_id)) {
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
