#include <vector>
#include <algorithm>
#include <limits>
#include "../json.hpp"

using namespace std;
using json = nlohmann::json;

float avg(vector<float> &vect);

float var(vector<float> &vect);

float travelerDistVar(vector<int> &path, json input, int traveler);

float travelerDistTotal(vector<int> &path, json input, int traveler);

float travelerDistMed(vector<int> &path, json input, int traveler);