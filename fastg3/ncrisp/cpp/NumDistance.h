#ifndef NUMDISTANCE_H
#define NUMDISTANCE_H

#include <cmath>

template <typename T>
class NumDistance {
    public:
        NumDistance();
        bool equality(T a, T b);
        double absolute(T a, T b);
};

/////////////////////////////////////////////////////// DEFINITION

template <typename T>
NumDistance<T>::NumDistance(){}

template <typename T>
bool NumDistance<T>::equality(T a, T b){
    return a==b;
}

template <typename T>
double NumDistance<T>::absolute(T a, T b){
    return std::abs(a-b);
}

#endif