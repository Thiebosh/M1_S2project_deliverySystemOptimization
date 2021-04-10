#include "pathComparison.h"


float avg(vector<float> &vect){
    float average = 0;
    for(int i = 0; i < vect.size(); i++){
        average+=vect[i];
    }
    return average/vect.size();
}

float var(vector<float> &vect){
    float var = 0;
    float average = avg(vect);
    for(int i = 0; i < vect.size()-1; i++){
        var += pow(vect[i]-average,2);
    }

    return var/vect.size();
}

float travelerDistVar(vector<int> &path, json input, int traveler){
    vector<float> vect;
    if(path.size() > 0){
        vect.push_back((float)input["traveler"][traveler]["arc"][path[0]]);
    }
    for (int i = 1; i < path.size(); i++)
    {
        vect.push_back((float)input["arc"][path[i - 1]][path[i]]);
    }
    return var(vect);
}

float travelerDistTotal(vector<int> &path, json input, int traveler)
{
    float total = 0;
    if(path.size() > 0){
        total += (float)input["traveler"][traveler]["arc"][path[0]];
    }
    for (int i = 1; i < path.size(); i++)
    {
        total += (float)input["arc"][path[i - 1]][path[i]];
    }
    return total;
}

float travelerDistMed(vector<int> &path, json input, int traveler){
    vector<float> vect;
   if(path.size() > 0){
        vect.push_back((float)input["traveler"][traveler]["arc"][path[0]]);
    }
    for (int i = 1; i < path.size(); i++)
    {
        vect.push_back((float)input["arc"][path[i - 1]][path[i]]);
    }
    sort(vect.begin(), vect.end());

    if(vect.size() % 2 == 0){
        return (vect[(int)(vect.size()/2)]+vect[(int)(vect.size()/2-1)])/2;
    }
    
    return vect[(int)(vect.size()/2-0.5)];
}