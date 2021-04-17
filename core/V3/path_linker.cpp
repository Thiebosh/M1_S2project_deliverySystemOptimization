#include <iostream>
#include <stdlib.h>
#include <vector>
#include "../json.hpp"

//input args
#define ARG_SEED 1
#define ARG_MATRIX 2
#define NB_ARGS 3

using namespace std;
using json = nlohmann::json;

vector<int> findsolution(json const &input);

int main(int argc, char *argv[])
{
	if (argc < NB_ARGS)
		return -1;

    srand(atoi(argv[ARG_SEED]));  // reuse same seed

	json input = json::parse(argv[ARG_MATRIX]);

	for (int pathId : findsolution(input)) {
		cout << pathId << ',';
	}

	return 0;
}

int getIdPoint(vector<int> const &allPoints, vector<double> const &distances)
{
	vector<double> weights;
	vector<double> normalized_weights;
	double min_val;
	double max_val;

	for (double i = 0; i < allPoints.size(); i++)
	{
		weights.push_back(1 / distances[i]);
	}
	//normalizing weights
	min_val = *min_element(weights.begin(), weights.end());
	max_val = *max_element(weights.begin(), weights.end());
	for (int i = 0; i < weights.size(); ++i)
	{
		if (max_val != min_val)
		{
			normalized_weights.push_back((double)(weights[i] - min_val) / (double)(max_val - min_val));
		}
		else
		{
			normalized_weights.push_back(0);
		}
	}

	double randomValue = (double)rand() / (RAND_MAX);
	for (int i = 0, j = normalized_weights.size()-1; i < normalized_weights.size(); i++, j--)
	{
		if (randomValue > normalized_weights[j])  // j replace reverse()
		{
			return allPoints[i];
		}
	}
	return -1;
}

vector<int> getNthClosest(int n, vector<double> &arc)
{
	vector<int> closest;
	vector<double> sortedArc = arc;
	sort(sortedArc.begin(), sortedArc.end());

	for (auto i = 0; i < min(n, (int)arc.size()); i++)
	{
		vector<double>::iterator itr = find(arc.begin(), arc.end(), sortedArc[i]);
		closest.push_back(distance(arc.begin(), itr));
	}
	return closest;
}

vector<int> getPossibleNextPeak(vector<double> const &arc, vector<int> const &possiblePoints, int nbClosest)
{
	vector<double> possiblePointsDistanceList;
	vector<double> allDistances = arc;
	vector<int> closestPoints;
	vector<int> points;

	for (auto i : possiblePoints)
	{
		possiblePointsDistanceList.push_back(allDistances[i]);
	}

	for (auto i : getNthClosest(nbClosest, possiblePointsDistanceList))
	{
		if (possiblePointsDistanceList[i] != 0)
		{
			vector<double>::iterator itr = find(allDistances.begin(), allDistances.end(), possiblePointsDistanceList[i]);
			points.push_back(distance(allDistances.begin(), itr));
		}
	}

	return points;
}

vector<int> findsolution(json const &input)
{
    vector<int> currSolution(input.at(0).size(), -1);

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
		closestPeaks = getPossibleNextPeak(input.at(currentPeak), remainingPeaks, remainingPeaks.size());

		for (int i : closestPeaks)
		{
			distances.push_back(input.at(currentPeak).at(i));
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
