#ifndef NUMATTRIBUTE_H
#define NUMATTRIBUTE_H

#include <iostream>
#include <string>
#include <exception>
#include <unordered_map>

#include "NumDistance.h"

std::unordered_map<std::string, int> AUTHORIZED_NUM_PREDICATES = {
    {"equality", 0},
    {"absolute", 1},
};

template <typename T>
class NumAttribute{
    public:
        NumAttribute(T* v, size_t n, std::string metric, double threshold): n_rows(n){
            value = std::vector<T>(v, v+n);
            if(AUTHORIZED_NUM_PREDICATES.find(metric)!=AUTHORIZED_NUM_PREDICATES.end()){
                this->metric_num = AUTHORIZED_NUM_PREDICATES[metric];
                this->threshold = threshold;
            }
        }
        bool is_similar(size_t i, size_t j) const;
        void show_col() const;
        void show_val(size_t i) const;
    
    private:
        std::vector<T> value;
        double threshold;
        int metric_num;
        size_t n_rows;
        NumDistance<T> * ND = new NumDistance<T>();
};

/////////////////////////////////////////////////////// DEFINITION

template <typename T>
bool NumAttribute<T>::is_similar(size_t i, size_t j) const{
    bool similar = false;
    switch(metric_num){
        case 0: if(ND->equality(value[i],value[j])) similar=true;
                break;
        case 1: if(ND->absolute(value[i],value[j]) <= threshold) similar=true;
                break;
    }
    return similar;
}

template <typename T>
void NumAttribute<T>::show_col() const{
    for(size_t i=0; i<n_rows; i++){
        std::cout << value[i] << std::endl;
    }
}

template <typename T>
void NumAttribute<T>::show_val(size_t i) const{
    std::cout << value[i];

}

#endif