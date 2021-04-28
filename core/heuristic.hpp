#include <vector>
#include <algorithm>
#include <random>
#include <iostream>
#include "json.hpp"

using namespace std;
using json = nlohmann::json;

int getIdPoint(vector<int> const &allPoints, vector<double> const &distances)
{
	vector<double> weights;
	vector<double> normalized_weights;
	double sum = 0;
	for (int i = allPoints.size() - 1; i >= 0; i--)
	{
		// cout << "dist: " << distances[i] << endl;
		sum += 1 / distances[i];
		// cout << "sum: " << sum << endl;
		weights.push_back(sum);
	}
	// cout << "end" << endl;

	double max_val_coeff = 100 / (*max_element(weights.begin(), weights.end()));
	for (auto w : weights)
	{
		normalized_weights.push_back(w * max_val_coeff);
	}

	double randomValue = rand() % 100;
	for (int i = 0; i < normalized_weights.size(); i++)
	{
		if (randomValue <= normalized_weights[i])
		{
			return allPoints[normalized_weights.size()-1-i];
		}
	}
	return -1;
}

vector<int> getNthClosest(int n, vector<double> &arc)
{
	vector<int> closest;
	vector<double> sortedArc = arc;
	sort(sortedArc.begin(), sortedArc.end());
	int limit = min(n, (int)arc.size());

	for (auto i = 0; i < limit; i++)
	{
		vector<double>::iterator itr = find(arc.begin(), arc.end(), sortedArc[i]);
		closest.push_back(distance(arc.begin(), itr));
	}

	return closest;
}

vector<int> getPossibleNextPeak(vector<double> &allDistances, vector<int> const &possiblePoints)
{
	vector<int> points;

	for (int i : getNthClosest(possiblePoints.size(), allDistances))
	{
		if (allDistances[i] == 0)
			continue;

		vector<double>::iterator itr = find(allDistances.begin(), allDistances.end(), allDistances[i]);
		points.push_back(possiblePoints[(int)distance(allDistances.begin(), itr)]);
	}

	return points;
}
