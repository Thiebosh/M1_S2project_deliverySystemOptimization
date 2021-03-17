#include<iostream>
#include <windows.h>
#include <time.h>
#include <vector>
#include <algorithm>

using namespace std;

int main(int argc, char *argv[]) {//model
    if (argc < 4) return -1;

    int id = atoi(argv[1]);
    //json parser of argv[2]
    int batch_size = atoi(argv[3]);

    cout << id << endl;

    // start here

    vector<int> peeks;
    for (int i = 0; i < 5; ++i) peeks.push_back(i); //replace 5 by peek tab length

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