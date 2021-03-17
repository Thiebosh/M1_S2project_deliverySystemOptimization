#include<iostream>
#include<string>
#include<math.h>
#include<vector>
#include<stdlib.h>
#include<time.h>
#include<algorithm>

#include "json.hpp"
using json = nlohmann::json;

using namespace std;

int n = 5;    //citynumber
struct city {
	int number;
	int res_link;
	float coordinate[2];
};
struct dist{
	int id;
	float distance;
};

float citydistance[5][5] = { 0.0 , 3.0  ,4.0 , 2.0  ,7.0,
3.0,  0.0,  4.0 , 6.0  ,3.0,
4.0,  4.0,  0.0 , 5.0 , 8.0,
2.0 , 6.0 , 5.0 , 0.0 , 6.0,
7.0 , 3.0,  8.0 , 6.0 , 0.0
};
int currsolution[5] = {};
float totaldis(int solution[5]) {
	float total = 0;
	for (int i = 0; i < 4; i++) {
		total = total + citydistance[solution[i]-1][solution[i+1]-1];
	}
	total=total+ citydistance[solution[0] - 1][solution[4] - 1];
	return total;
}
void findsolution(int id, json input, int nbClosest) {
	vector<int> remainingPeaks;
	cout << input["peak"][0].size() << endl;
	for(int i=0; i < input["peak"][0].size(); i++){
		remainingPeaks.push_back(i);
	}

	int currentPeak = rand() % remainingPeaks.size();

	currsolution[0] = remainingPeaks[currentPeak];

	remainingPeaks.erase(remainingPeaks.begin() + currentPeak);
	vector<dist> closestPeaks;
	int curRank = 1;
	cout << currentPeak << endl;
		for(auto elem: currsolution){
			cout << elem << " "; 
		}
		cout << endl;
	while(!remainingPeaks.empty()){
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
		currsolution[curRank++] =	currentPeak;
		cout << currentPeak << endl;
		// for(auto elem: currsolution){
		// 	cout << elem << " "; 
		// }
		// cout << endl;
		for(auto elem: remainingPeaks){
			cout << elem << " ";
		}
		cout <<endl;
		remainingPeaks.erase(remainingPeaks.begin() + pos);
		for(auto elem: remainingPeaks){
			cout << elem << " ";
		}
		cout <<endl<<endl<<endl;

	}
}

int main(int argc, char* argv[]) {
    if (argc < 4) return -1;

    int id = atoi(argv[1]);
    json inputData = json::parse(argv[2]);
    int batch_size = atoi(argv[3]);

    cout << id << endl;
    srand(time(NULL) % id);

    // start here

	findsolution(id, inputData, batch_size);
	
    // end here

    cout << totaldis(currsolution) << ";";
    for (auto elem : currsolution) cout << elem << ",";

    return 0;
}
