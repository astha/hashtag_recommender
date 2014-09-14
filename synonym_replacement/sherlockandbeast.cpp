#include <cmath>
#include <cstdio>
#include <vector>
#include <iostream>
#include <algorithm>
using namespace std;

bool largest(int n){
    if(n < 0){
        return false;
    }else if(n == 0){
        return true;
    }else{
        if(largest(n-3)){
            cout << "555";
            return true;
        }else if(largest(n-5)){
            cout << "33333";
            return true;
        }else{
            return false;
        }
    }
    return false;
}

int main() {
    /* Enter your code here. Read input from STDIN. Print output to STDOUT */  
    int T; 
    cin >> T;
    int N;
    for(int count = 0; count < N; count++){
        cin >> N;
        if(!largest(N))
            cout << -1 << endl;
        else
            cout << endl;
    }
    return 0;
}
