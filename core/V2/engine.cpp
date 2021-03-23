#include <iostream>
#include <string>
#include <math.h>
#include <vector>
#include <stdlib.h>
#include <time.h>
#include <algorithm>

#include "../json.hpp"

using namespace std;
using json = nlohmann::json;


typedef struct dist_{
	int id;
	float distance;
} dist;


void findsolution(int id, json input, int nbClosest, vector<int>& currSolution);

float totaldis(vector<int>& path, json input);


int main(int argc, char* argv[]) {
    if (argc < 4) return -1;

    int id = atoi(argv[1]);
    json inputData = json::parse(argv[2]);
    int batch_size = atoi(argv[3]);

	time_t seed = time(NULL) % id;
    srand(seed);

	cout << id << endl << seed << endl;

    // start here

	// declare result tab
	vector<int> path(inputData["peak"].size(), 0);

	findsolution(id, inputData, batch_size, path);

    // end here

	cout << totaldis(path, inputData) << ";";
    for (int elem : path) cout << elem << ",";

	return 0;
}


void findsolution(int id, json input, int nbClosest, vector<int>& currSolution) {
	// build list of unselected peaks
	vector<int> remainingPeaks;
	for(int i=0; i < input["peak"].size(); ++i){
		if (input["peak"][i]["origin"]==1){
			remainingPeaks.push_back(i);
		}
	}

	// select first peak
	int currentPeak = rand() % remainingPeaks.size();
	currSolution[0] = remainingPeaks[currentPeak];
	remainingPeaks.erase(remainingPeaks.begin() + currentPeak);
	remainingPeaks.push_back(currSolution[0]+1);

	// select next peak while some remains unselected
	int currRank = 1;
	vector<dist> closestPeaks;
	while(!remainingPeaks.empty()) {
		closestPeaks.clear();

		// gather remaining peaks and reverse sort them
		for(auto i: remainingPeaks){
			dist curPoint;
			curPoint.distance = input["arc"][currentPeak][i];
			curPoint.id = i;
			closestPeaks.push_back(curPoint);
		}
		sort(closestPeaks.begin(), closestPeaks.end(), [](dist a, dist b) {return a.distance < b.distance;});

		// select one of the closest remaining
		if(nbClosest > closestPeaks.size()) nbClosest--;
		int pos = (int)(rand() % nbClosest);
		currentPeak =  closestPeaks[pos].id;
		currSolution[currRank++] = currentPeak;

		// remove selected from remaining
		for(int i = 0; i < remainingPeaks.size(); i++){
			if(remainingPeaks[i] == currentPeak){
				remainingPeaks.erase(remainingPeaks.begin()+i);
				break;
			}
		}

		//add the destination associated to the chosed peak (if the chose peak is an origin)
		if (input["peak"][currentPeak]["origin"]==1){
			remainingPeaks.push_back(currentPeak+1);
		}
		

	}
	currSolution[input["peak"].size()] = currSolution[0];
}


float totaldis(vector<int>& path, json input) {
	float total = 0;
	for (int i = 1; i <  path.size(); i++) {
		total += (float)input["arc"][path[i-1]][path[i]];
	}
	return total;
}
