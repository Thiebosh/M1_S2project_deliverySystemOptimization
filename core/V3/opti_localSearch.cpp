#include <iostream>
#include <string>
#include <math.h>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <algorithm>
#include <map>
#include <limits>
#include <typeinfo>
#include <fstream>
#include <streambuf>
#include "../json.hpp"

//input args
#define ARG_ID 1
#define ARG_SEED 2
#define ARG_FILE_PATH 3
#define ARG_PATH 4
#define ARG_TRIES 5
#define NB_ARGS 6

using namespace std;
using json = nlohmann::json;


float totaldis(vector<int> const &path, json const &input);
void findnei(vector<int> &solution, json const &input);

// .\opti_localSearch.exe 0 125 data.tmp "[[0, 2, 3, 1], [4, 6, 7, 5], [-1]]" 1
int main(int argc, char* argv[]) {
    int id = atoi(argv[ARG_ID]);
    cout << id << endl;

    if (argc < NB_ARGS) return -1;

    // srand(atoi(argv[ARG_SEED])); // reuse seed
    srand(time_t(argv[ARG_SEED])); // debug : works for nearly all seed but sometimes, error. some others, invalid path

    ifstream t(argv[ARG_FILE_PATH], ios::in);
    t.seekg(0);
    json inputData = json::parse((std::istreambuf_iterator<char>(t)), (std::istreambuf_iterator<char>()));

    json path_list = json::parse(argv[ARG_PATH]);

    // declare result tab
    for (int path_id = 0; path_id < path_list.size(); path_id++) {
        if (path_list.at(path_id).size() <= 2) continue; //not enough vertices

        vector<int> currentpath = path_list.at(path_id);

        // float totalDistance = totaldis(currentpath, inputData) / (float)inputData["traveler"][0]["speed"]; //not implemented yet
        cout << endl << path_id << endl;
        cout << "before : " << totaldis(currentpath, inputData) << ";";
        for (int elem : currentpath) cout << elem << ",";
        cout << endl;

        for (int i = 0; i < atoi(argv[ARG_TRIES]); i++) findnei(currentpath, inputData);

        // totalDistance = totaldis(currentpath, inputData) / (float)inputData["traveler"][0]["speed"]; //not implemented yet
        cout << "after  : " << totaldis(currentpath, inputData) << ";";
        for (int elem : currentpath) cout << elem << ",";
        cout << endl;
    }

    return 0;
}

bool checknei(vector<int> const &solution, json const &input) {
    vector<int> ableclient;
    int storage = input["traveler"][0]["qty"];
    int des = 0;

    for (int i = 0; i < solution.size(); i++) {
        if (input["peak"][solution[i]]["origin"] == 1) {
            if (!storage) {
                des++;
                break;
            }
            storage--;
            for (int j = 0; j < input["peak"][solution[i]]["link"].size(); j++) {
                ableclient.push_back(input["peak"][solution[i]]["link"][j]);
            }
        }

        if (input["peak"][solution[i]]["origin"] == 0) {
            storage++;
            int judge = 0;
            for (int j = 0; j < ableclient.size(); j++) {
                if (solution[i] == ableclient[j]) {
                    judge++;
                }
            }
            if (judge == 0) {
                des++;
                break;
            }
        }
    }

    return !des;
}

void findnei(vector<int> &solution, json const &input) {
    vector<int> nei = solution;
    int a = rand() % input["peak"].size() + 1;

    for (int i = 0; i < nei.size() && i != a; i++) {
        int nuclear = nei[a];
        nei[a] = nei[i];
        nei[i] = nuclear;

        if (checknei(nei,input) && totaldis(nei, input) < totaldis(solution, input)) {
            solution = nei;
        }
    }
}

float totaldis(vector<int> const &path, json const &input) {
    float total = 0;
    for (int i = 1; i < path.size(); i++) {
        total += (float)input["arc"][path[i - 1]][path[i]];
    }
    return total;
}
