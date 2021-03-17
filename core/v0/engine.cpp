#include<iostream>
#include <windows.h>
#include <time.h>
#include <vector>
#include <algorithm>

using namespace std;

int main(int argc, char *argv[]) {//model
    if (argc < 3) return -1;

    int id = atoi(argv[1]);
    cout << id << endl;

    // start here

    vector<int> peeks = {0, 1, 2, 3, 4, 5};

    // if (id == 2) {
    //     cout << id << " is waiting" << endl;
    //     Sleep(5000);
    // }

    srand(time(NULL) % id);
    random_shuffle(peeks.begin(), peeks.end());

    // end here

    cout << rand()*6 << ";";
    for (auto elem : peeks) cout << elem << ",";

    return 0;
}