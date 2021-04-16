#include "pathComparison.h"


float avg(vector<float> const &vect){
    float average = 0;
    for(int i = 0; i < vect.size(); i++){
        average+=vect[i];
    }
    return average/vect.size();
}

float var(vector<float> const &vect){
    if(vect.size() > 0){
        float var = 0;
        float average = avg(vect);
        for(int i = 0; i < vect.size()-1; i++){
            var += pow(vect[i]-average,2);
        }
        return var/vect.size();
    }
    return numeric_limits<float>::max();
    
}

float travelerDistVar(vector<int> const &path, json const &input, int traveler){
    vector<float> vect;
    if(path.size() > 0){
        vect.push_back((float)input.at("traveler").at(traveler).at("arc").at(path[0]));
    }
    for (int i = 1; i < path.size(); i++)
    {
        vect.push_back((float)input.at("arc").at(path[i - 1]).at(path[i]));
    }
    return var(vect);
}

float travelerDistTotal(vector<int> const &path, json const &input, int traveler)
{
    float total = 0;
    if(path.size() > 0){
        total += (float)input.at("traveler").at(traveler).at("arc").at(path[0]);
    }
    for (int i = 1; i < path.size(); i++)
    {
        total += (float)input.at("arc").at(path[i - 1]).at(path[i]);
    }
    return total;
}

float travelerDistMed(vector<int> const &path, json const &input, int traveler){
    vector<float> vect;
   if(path.size() > 0){
        vect.push_back((float)input.at("traveler").at(traveler).at("arc").at(path[0]));
    }else{
        return numeric_limits<float>::max();
    }
    for (int i = 1; i < path.size(); i++)
    {
        vect.push_back((float)input.at("arc").at(path[i - 1]).at(path[i]));
    }
    sort(vect.begin(), vect.end());

    if(vect.size() % 2 == 0){
        return (vect[(int)(vect.size()/2)]+vect[(int)(vect.size()/2-1)])/2;
    }
    
    return vect[(int)(vect.size()/2-0.5)];
}
