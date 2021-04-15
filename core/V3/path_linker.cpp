#include <iostream>
#include <string>
#include <math.h>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <algorithm>
#include <map>
#include <mutex>
#include <thread>
#include <fstream>
#include <streambuf>
#include <numeric>
#include "../json.hpp"
#include "pathComparison.h"

//input args
#define ARG_SEED 1
#define ARG_MATRIX 2
#define NB_ARGS 3

using namespace std;

typedef struct dist_
{
    int id;
    float distance;
} dist;

void findsolution(json* input, vector<int>& currSolution);

int main(int argc, char *argv[])
{
    if (argc < NB_ARGS) return -1;

    srand(time_t(argv[ARG_SEED]));

    json jsonData = json::parse(argv[ARG_MATRIX]);
    json* inputData = &jsonData;

    vector<int> idPath(inputData->at(0).size());

	findsolution(inputData, idPath);

    for(int i = 0; i < idPath.size(); ++i) cout << i << ',';

    return 0;
}


void findsolution(json* input, vector<int>& currSolution) {
	// build list of unselected peaks
	vector<int> remainingPeaks;
	for(int i=0; i < currSolution.size(); ++i) remainingPeaks.push_back(i);

	// select first peak
	int currentPeak = rand() % remainingPeaks.size();
	currSolution[0] = remainingPeaks[currentPeak];
	remainingPeaks.erase(remainingPeaks.begin() + currentPeak);

	// select next peak while some remains unselected
	int currRank = 1;
	vector<dist> closestPeaks;
	while(!remainingPeaks.empty()) {
		closestPeaks.clear();

		// gather remaining peaks and reverse sort them
		for(auto i: remainingPeaks){
			dist curPoint;
			curPoint.distance = input->at(currentPeak).at(i);
			curPoint.id = i;
			closestPeaks.push_back(curPoint);
		}
		sort(closestPeaks.begin(), closestPeaks.end(), [](dist a, dist b) {return a.distance < b.distance;});

		// select one of the closest remaining
		int pos = (int)(rand() % remainingPeaks.size());  // bad random
		currentPeak =  closestPeaks[pos].id;
		currSolution[currRank++] = currentPeak;

		// remove selected from remaining
		for(int i = 0; i < remainingPeaks.size(); i++){
			if(remainingPeaks[i] == currentPeak){
				remainingPeaks.erase(remainingPeaks.begin()+i);
				break;
			}
		}
	}
}
