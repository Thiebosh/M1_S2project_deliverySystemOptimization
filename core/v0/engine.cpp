#include<iostream>
#include <time.h>
#include <vector>
#include <algorithm>

using namespace std;

int main(int argc, char *argv[]) {
    vector<int> peeks = {0, 1, 2, 3, 4, 5};

    srand(time(NULL) % *argv[2]);
    random_shuffle(peeks.begin(), peeks.end());

    cout << rand()*6 << ";";
    for (auto elem : peeks) cout << elem << ",";

    return 0;
}