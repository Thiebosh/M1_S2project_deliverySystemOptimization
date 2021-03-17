#include<iostream>
#include<string>
#include<math.h>
#include<vector>
#include<stdlib.h>
#include<time.h>
#include<algorithm>

#include "json.hpp"
#include<algorithm>

using json = nlohmann::json;
using namespace std;  //citynumber
struct city {
	int number;
	int res_link;
	float coordinate[2];
};
struct dist{
	int id;
	float distance;
};


float totaldis(int* path, json input) {
	float total = 0;
	for (int i = 1; i <  input["peak"][0].size(); i++) {
		total += (float)input["arc"][*(path+i-1)][*(path+i)];
	}
	return total;
}

int* findsolution(int id, json input, int nbClosest) {
	static int currsolution[5] = {};

	vector<int> remainingPeaks;
	for(int i=0; i < input["peak"][0].size(); i++){
		remainingPeaks.push_back(i);
	}

	int currentPeak = rand() % remainingPeaks.size();

	currsolution[0] = remainingPeaks[currentPeak];

	remainingPeaks.erase(remainingPeaks.begin() + currentPeak);
	vector<dist> closestPeaks;
	int curRank = 1;

	while(remainingPeaks.size() > 1){
		closestPeaks.clear();
		for(auto i: remainingPeaks){
			dist curPoint;
			curPoint.distance = input["arc"][currentPeak][i];
			curPoint.id = i;
			closestPeaks.push_back(curPoint);
		}
		sort(closestPeaks.begin(), closestPeaks.end(), [](dist a, dist b) {return a.distance < b.distance;});
		
		closestPeaks.erase(closestPeaks.begin());
		if(nbClosest > closestPeaks.size()){
			nbClosest--;
		}
		int pos = (int)(rand() % nbClosest);
		currentPeak =  closestPeaks[pos].id;
		currsolution[curRank++] = currentPeak;
	

		for(int i = 0; i < remainingPeaks.size(); i++){
			if(remainingPeaks[i] == currentPeak){
				remainingPeaks.erase(remainingPeaks.begin()+i);
			}
		}
	}
	
	return currsolution;
}


int main(int argc, char* argv[]) {
    if (argc < 4) return -1;

    int id = atoi(argv[1]);
    json inputData = json::parse(argv[2]);
    int batch_size = atoi(argv[3]);

    cout << id << endl;
    srand(time(NULL) % id);

    // start here

	int* path = findsolution(id, inputData, batch_size);
	

	float a = totaldis(path, inputData);

	cout << a << ";";
	
	for (int i = 0; i <  inputData["peak"][0].size(); i++) {
		cout << *(path+i)<<",";
	}
	
}