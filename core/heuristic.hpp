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

	double max_val = *max_element(weights.begin(), weights.end());
	for (auto w : weights)
	{
		normalized_weights.push_back(w * 100 / max_val);
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

	for (auto i = 0; i < min(n, (int)arc.size()); i++)
	{
		vector<double>::iterator itr = find(arc.begin(), arc.end(), sortedArc[i]);
		closest.push_back(distance(arc.begin(), itr));
	}
	return closest;
}

vector<int> getPossibleNextPeak(vector<double> const &arc, vector<int> const &possiblePoints, int nbClosest)
{
	vector<double> allDistances = arc;
	vector<int> closestPoints;
	vector<int> points;

	for (auto i : getNthClosest(nbClosest, allDistances))
	{
		if (allDistances[i] != 0)
		{
			vector<double>::iterator itr = find(allDistances.begin(), allDistances.end(), allDistances[i]);
			// cout << "size1: " << possiblePoints.size() << endl;
			// cout << "dist: " << (int)distance(allDistances.begin(), itr) << endl;
			points.push_back(possiblePoints.at((int)distance(allDistances.begin(), itr)));
		}
	}
	// cout << ":!\\" << endl;
	// cout << "size:" << points.size() << endl;
	return points;
}
