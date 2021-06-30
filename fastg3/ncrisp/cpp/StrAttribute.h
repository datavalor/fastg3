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
        StrAttribute(strcol v, size_t n, std::string predicate, std::vector<double> params): n_rows(n), value(v){
            if(AUTHORIZED_STR_PREDICATES.find(predicate)!=AUTHORIZED_STR_PREDICATES.end()){
                this->predicate_num = AUTHORIZED_STR_PREDICATES[predicate];
                this->params = params;
            }
        }
        bool is_similar(size_t i, size_t j) const;
        void show_col() const;
        void show_val(size_t i) const;
    
    private:
        std::vector<double> params;
        int predicate_num;
        size_t n_rows;
        strcol value;
        StrDistance * SD = new StrDistance();
};

/////////////////////////////////////////////////////// DEFINITION

bool StrAttribute::is_similar(size_t i, size_t j) const{
    bool is_similar = false;
    switch(predicate_num){
        case 0: if(value[i]==value[j]) 
                    is_similar=true;
                break;
        case 1: if(SD->edit_distance(value[i], value[j], value[i].length(), value[j].length()) <= params[0])
                    is_similar=true;
                break;
    }
    return is_similar;
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