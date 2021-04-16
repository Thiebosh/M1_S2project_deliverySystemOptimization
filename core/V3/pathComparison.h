#include <vector>
#include <algorithm>
#include <limits>
#include "../json.hpp"

using namespace std;

float avg(vector<float> const &vect);

float var(vector<float> const &vect);

float travelerDistVar(vector<int> const &path, json const &input, int traveler);

float travelerDistTotal(vector<int> const &path, json const &input, int traveler);

float travelerDistMed(vector<int> const &path, json const &input, int traveler);
