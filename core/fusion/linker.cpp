#include <iostream>
#include <vector>
#include <map>
#include "..\json.hpp"
#include "..\heuristic.hpp"

//input args
#define ARG_SEED 1
#define ARG_MATRIX 2
#define NB_ARGS 3

using namespace std;
using json = nlohmann::json;


// definitions
vector<int> findsolution(json const &input);


// main function
int main(int argc, char *argv[])
{
	if (argc < NB_ARGS)
		return -1;

    srand(atoi(argv[ARG_SEED])); // reuse seed

	json input = json::parse(argv[ARG_MATRIX]);

	for (int pathId : findsolution(input)) {
		cout << pathId << ',';
	}

	return 0;
}

vector<int> findsolution(json const &input)
{
    vector<int> currSolution(input[0].size(), -1);

	// build list of unselected peaks
	vector<int> remainingPeaks;
	for (int i = 0; i < currSolution.size(); ++i)
		remainingPeaks.push_back(i);

	// select first peak
	int currentPeak = (int)(rand() % remainingPeaks.size());
	currSolution[0] = currentPeak;
	remainingPeaks.erase(remainingPeaks.begin() + currentPeak);

	// select next peak while some remains unselected
	int currRank = 1;
	vector<int> closestPeaks;
	vector<double> distances;


	while (!remainingPeaks.empty())
	{
		distances.clear();
		vector<double> arc_distances = input[currentPeak];
		closestPeaks = getPossibleNextPeak(arc_distances, remainingPeaks);

		for (int i : closestPeaks)
		{
			distances.push_back(input[currentPeak].at(i));
		}

		// select one of the closest remaining
		currentPeak = getIdPoint(closestPeaks, distances);
		if (currentPeak < 0)
		{
			break;
		}
		currSolution[currRank++] = currentPeak;
		// remove selected from remaining

		if (find(remainingPeaks.begin(), remainingPeaks.end(), currentPeak) != remainingPeaks.end())
		{
			remainingPeaks.erase(find(remainingPeaks.begin(), remainingPeaks.end(), currentPeak));
		}
	}

	return currSolution;
}
