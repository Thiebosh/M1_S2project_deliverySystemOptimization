#include<iostream>
#include "Windows.h"
#include <time.h>

using namespace std;

int main(int argc, char *argv[]){
    cout << "start " << *argv[2] << endl;
    srand(time(NULL));
    Sleep((int)(rand()%5000));
    cout<<"TEST: " << *argv[2] <<endl;
    return 0;
}