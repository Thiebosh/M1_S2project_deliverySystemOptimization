#include <iostream>
#include <stdlib.h>
#include <math.h>
#include <vector>
#include <map>
#include <time.h>
#include <algorithm>
#include <fstream>
#include <streambuf>
#include "..\json.hpp"
#include "..\kpi.hpp"

//input args
#define ARG_ID 1
#define ARG_SEED 2
#define ARG_FILE_PATH 3
#define ARG_PATH 4
#define ARG_TRIES 5
#define NB_ARGS 6

using namespace std;
using json = nlohmann::json;


void findnei(vector<int> &solution, json const &input, int const path_id);


int main(int argc, char* argv[]) {
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc < NB_ARGS) return -1;

    srand(atoi(argv[ARG_SEED])); // reuse seed

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    json inputData = json::parse((std::istreambuf_iterator<char>(t)), (std::istreambuf_iterator<char>()));

    json path_list = json::parse(argv[ARG_PATH]);

    double scoreBefore = 0;

    // search for each traveler path
    for (int path_id = 0; path_id < path_list.size(); path_id++) {
        if (path_list.at(path_id).size() <= 2) continue; //not enough vertices

        vector<int> currentpath = path_list.at(path_id);

        cout << endl << path_id << endl;
        cout << "before : " << travelerDistTotal(currentpath, inputData, path_id) << ";";
        for (int elem : currentpath) cout << elem << ",";
        cout << endl;

        for (int i = 0; i < atoi(argv[ARG_TRIES]); i++) {
            findnei(currentpath, inputData, path_id);
        }

        cout << "after  : " << travelerDistTotal(currentpath, inputData, path_id) << ";";
        for (int elem : currentpath) cout << elem << ",";
        cout << endl;
    }

    return 0;
}


bool checknei(vector<int> const &solution, json const &input) {
    vector<int> ableclient(input["peak"].size(), 0);
    int storage = input["traveler"][0]["qty"];
    int des = 0;

    for (int i = 0; i < solution.size(); i++) {
        if (input["peak"][solution[i]]["origin"] == 1) {
            if (!storage) {
                des++;
                break;
            }
            int j = 0;
            while(j++ < input["peak"][solution[i]]["link"].size() && storage-- > 0) {
                ableclient[solution[i]]++;
            }
        }

        if (input["peak"][solution[i]]["origin"] == 0) {
            storage++;
            int position = input["peak"][solution[i]]["link"];
            if(ableclient[position] > 0) ableclient[position]--;
            else {
                des++;
                break;
            }
        }        
    }

    return !des;
}


void findnei(vector<int> &solution, json const &input, int const path_id) {
    vector<int> bestnei = solution;

    for(int a = 0; a < solution.size(); a++){    
        for (int i = 0; i < solution.size() && i != a; i++) {
            vector<int> nei = solution;
            swap(nei[a], nei[i]);

            double before = travelerDistTotal(solution, input, path_id);
            double after = travelerDistTotal(nei, input, path_id);

            if (checknei(nei, input) && before > after) bestnei = nei;
        }
    }

    solution = bestnei;
}
