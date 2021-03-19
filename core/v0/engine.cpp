#include <iostream>
#include <windows.h>
#include <time.h>
#include <vector>
#include <algorithm>

#include "../json.hpp"

using namespace std;
using json = nlohmann::json;

/**
 * This is the template model : retrieving args and sending reponses is default
 * */
int main(int argc, char *argv[]) {
    if (argc < 4) return -1;

    int id = atoi(argv[1]);
    json inputData = json::parse(argv[2]);
    int batch_size = atoi(argv[3]);

    cout << id << endl;
    srand(time(NULL) % id);

    // start here

    vector<int> peaks;
    for (int i = 0; i < inputData["peak"].size(); ++i) peaks.push_back(i);
    peaks.push_back(peaks[0]);

    random_shuffle(peaks.begin(), peaks.end());
    float total_time = rand()*6;

    // end here

    cout << total_time << ";";
    for (auto elem : peaks) cout << elem << ",";

    return 0;
}