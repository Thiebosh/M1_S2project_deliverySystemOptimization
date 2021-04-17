#include <vector>
#include <algorithm>
#include "../json.hpp"

using namespace std;
using json = nlohmann::json;

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
