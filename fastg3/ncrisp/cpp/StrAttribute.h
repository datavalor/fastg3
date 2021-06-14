#ifndef STRATTRIBUTE_H
#define STRATTRIBUTE_H

#include <iostream>
#include <string>
#include <exception>
#include <unordered_map>
#include <vector>

#include "StrDistance.h"

std::unordered_map<std::string, int> AUTHORIZED_STR_PREDICATES = {
    {"equality", 0},
    {"edit_distance", 1},
};

using strcol = std::vector<std::string>;

class StrAttribute{
    public:
        StrAttribute(strcol v, size_t n, std::string metric, double threshold): n_rows(n), value(v){
            if(AUTHORIZED_STR_PREDICATES.find(metric)!=AUTHORIZED_STR_PREDICATES.end()){
                this->metric_num = AUTHORIZED_STR_PREDICATES[metric];
                this->threshold = threshold;
            }
        }
        bool is_similar(size_t i, size_t j) const;
        void show_col() const;
        void show_val(size_t i) const;
    
    private:
        double threshold;
        int metric_num;
        size_t n_rows;
        strcol value;
        StrDistance * SD = new StrDistance();
};

/////////////////////////////////////////////////////// DEFINITION

bool StrAttribute::is_similar(size_t i, size_t j) const{
    bool similar = false;
    switch(metric_num){
        case 0: if(SD->equality(value[i],value[j])) similar=true;
                break;
        case 1: if(SD->edit_distance(value[i],value[j], value[i].length(), value[j].length()) <= threshold) similar=true;
                break;
    }
    return similar;
}

void StrAttribute::show_col() const{
    for(size_t i=0; i<n_rows; i++){
        std::cout << value[i] << std::endl;
    }
}

void StrAttribute::show_val(size_t i) const{
    std::cout << value[i];

}

#endif