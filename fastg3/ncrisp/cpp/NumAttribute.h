#ifndef NUMATTRIBUTE_H
#define NUMATTRIBUTE_H

#include <iostream>
#include <string>
#include <exception>
#include <unordered_map>
#include <algorithm>
#include <cmath>

#include "NumDistance.h"

std::unordered_map<std::string, int> AUTHORIZED_NUM_PREDICATES = {
    {"equality", 0},
    {"absolute_distance", 1},
    {"abs_rel_uncertainties", 2},
};

template <typename T>
class NumAttribute{
    public:
        NumAttribute(T* v, size_t n, std::string predicate, std::vector<double> params): n_rows(n){
            value = std::vector<T>(v, v+n);
            if(AUTHORIZED_NUM_PREDICATES.find(predicate)!=AUTHORIZED_NUM_PREDICATES.end()){
                this->predicate_num = AUTHORIZED_NUM_PREDICATES[predicate];
                this->params = params;
            }
        }
        bool is_similar(size_t i, size_t j) const;
        void show_col() const;
        void show_val(size_t i) const;
    
    private:
        std::vector<T> value;
        std::vector<double> params;
        int predicate_num;
        size_t n_rows;
        NumDistance<T> * ND = new NumDistance<T>();
};

/////////////////////////////////////////////////////// DEFINITION

template <typename T>
bool NumAttribute<T>::is_similar(size_t i, size_t j) const{
    switch(predicate_num){
        case 0: if(value[i]==value[j]) 
                    return true;
        case 1: if(std::abs(value[i]-value[j]) <= params[0]) 
                    return true;
        case 2: if(std::abs(value[i]-value[j]) <= (params[0]+params[1]*std::max(value[i],value[j]))) 
                    return true;
    }
    return false;
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