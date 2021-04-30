#include <vector>
#include <algorithm>
#include <limits>
#include "json.hpp"

using namespace std;
using json = nlohmann::json;


float travelerDistTotal(vector<int> const &path, json const &input, int traveler, bool back_origin)
{
    float total = 0;
    if (path.size() > 0) {
        total += (float)input["traveler"][traveler]["arc"][path[0]];
        if (back_origin) {
            total += (float)input["traveler"][traveler]["arc"][path[path.size()-1]];
        }
    }
    for (int i = 1; i < path.size(); i++)
    {
        total += (float)input["arc"][path[i - 1]][path[i]];
    }
    return total;
}

vector<float> non_zero(vector<float> const &vect)
{
    vector<float> non_zero(vect.size());
    auto it = copy_if(vect.begin(), vect.end(), non_zero.begin(), [](int i){return i > 0;} );
    non_zero.resize(distance(non_zero.begin(), it));
    return non_zero;
}

// total, % trav, min, max, écart (max-min), moyenne, médiane

float kpi0(vector<float> const &distances) //total
{
    return accumulate(distances.begin(), distances.end(), 0.0);
}

float kpi1(vector<float> const &distances) // % trav used
{
    return (float)non_zero(distances).size() / (float)distances.size();
}

float kpi2(vector<float> const &distances) // min
{
    auto tmp = non_zero(distances);
    return *min_element(tmp.begin(), tmp.end());
}

float kpi3(vector<float> const &distances) //max
{
    return *max_element(distances.begin(), distances.end());
}

float kpi4(vector<float> const &distances) //interval
{
    auto tmp = non_zero(distances);
    float min = *min_element(tmp.begin(), tmp.end());
    float max = *max_element(tmp.begin(), tmp.end());
    return max - min;
}

float kpi5(vector<float> const &distances) //mean
{
    auto tmp = non_zero(distances);
    return accumulate(tmp.begin(), tmp.end(), 0.0) / tmp.size();
}

float kpi6(vector<float> const &distances) //median
{
    auto tmp = non_zero(distances);
    size_t n = tmp.size() / 2;
    nth_element(tmp.begin(), tmp.begin()+n, tmp.end());
    return tmp[n];
}

void print_kpis(vector<float> const &distances) {
    cout << kpi0(distances) << ","
         << kpi1(distances) << ","
         << kpi2(distances) << ","
         << kpi3(distances) << ","
         << kpi4(distances) << ","
         << kpi5(distances) << ","
         << kpi6(distances) << endl;
}
