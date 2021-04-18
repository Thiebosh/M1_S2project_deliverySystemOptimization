#include <vector>
#include <algorithm>
#include <random>
#include "../json.hpp"

using namespace std;
using json = nlohmann::json;

int getIdPoint(vector<int> const &allPoints, vector<double> const &distances)
{
	vector<double> weights;
	vector<double> normalized_weights;
	double min_val;
	double max_val;
	for (int i = allPoints.size()-1; i >= 0; i--)
	{
		weights.push_back(1/distances[i]);
	}

	max_val = *max_element(weights.begin(), weights.end());
	min_val = *min_element(weights.begin(), weights.end());
	for(auto i: weights){
		normalized_weights.push_back(i*100/max_val);
	}
	double randomValue =  rand()%100;
	for (int j = 0; j < normalized_weights.size(); j++)
	{
		if (randomValue <= normalized_weights[j])  // j replace reverse()
		{
			return allPoints[j];
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
