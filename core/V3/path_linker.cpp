#include <iostream>
#include <stdlib.h>
#include "../json.hpp"
#include "common.hpp"

//input args
#define ARG_SEED 1
#define ARG_MATRIX 2
#define NB_ARGS 3

using namespace std;
using json = nlohmann::json;

int main(int argc, char *argv[])
{
	if (argc < NB_ARGS)
		return -1;

    srand(atoi(argv[ARG_SEED]));  // reuse same seed

	json input = json::parse(argv[ARG_MATRIX]);

	for (int pathId : findsolution(input)) {
		cout << pathId << ',';
	}

	return 0;
}
