#include<iostream>
#include<string>
#include<math.h>
#include<vector>
#include< stdlib.h>
using namespace std;
int n = 5;    //citynumber
struct city {
	int number;
	int res_link;
	float coordinate[2];
};
float citydistance[5][5] = { 0.0 , 3.0  ,4.0 , 2.0  ,7.0,
3.0,  0.0,  4.0 , 6.0  ,3.0,
4.0,  4.0,  0.0 , 5.0 , 8.0,
2.0 , 6.0 , 5.0 , 0.0 , 6.0,
7.0 , 3.0,  8.0 , 6.0 , 0.0
};
int currsolution[5] = {};
float totaldis(int solution[5]) {
	float total = 0;
	for (int i = 0; i < 4; i++) {
		total = total + citydistance[solution[i]-1][solution[i+1]-1];
	}
	total=total+ citydistance[solution[0] - 1][solution[4] - 1];
	return total;
}
void findsolution() {
	srand(time(NULL));
	int b = rand() % 5 + 1;
	vector<int> a = { 1,2,3,4,5 };
	currsolution[0] = a[b];
	std::vector<int>::iterator i = a.begin() + b;
	a.erase(i);
	for (int i = 0; i < 4; i++) {
		int pos = 0;
		float dis = 100;
		for (int j = 0; j < a.size(); j++) {
			if (citydistance[currsolution[i]-1][a[j] - 1] < dis) {
				pos = j;
				dis = citydistance[currsolution[i] -1][a[j] - 1];
			}
		}
		currsolution[i + 1] = a[pos];
		std::vector<int>::iterator it = a.begin() + pos;
		a.erase(it);
	}
}
int main() {
	findsolution();
	float a = totaldis(currsolution);
	cout << "distance:" << a << endl;
	for (int i = 0; i < 5; i++) {
		cout << currsolution[i] << " ";
	}
	cout << currsolution[0];
}