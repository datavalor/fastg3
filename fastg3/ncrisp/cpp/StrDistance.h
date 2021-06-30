#ifndef STRDISTANCE_H
#define STRDISTANCE_H

#include <cmath>
#include <string>

size_t min3(size_t x, size_t y, size_t z) { return std::min(std::min(x, y), z); }

class StrDistance {
    public:
        StrDistance();
        bool equality(std::string a, std::string b);
        size_t edit_distance(std::string a, std::string b, size_t al, size_t bl);
};

/////////////////////////////////////////////////////// DEFINITION

StrDistance::StrDistance(){}

bool StrDistance::equality(std::string a, std::string b){
    return a==b;
}

size_t StrDistance::edit_distance(std::string a, std::string b, size_t al, size_t bl){
    if(al == 0) 
        return bl;
    else if(bl == 0) 
        return al;
    else if(a[al] == b[bl]) 
        return edit_distance(a, b, al-1, bl-1);
    else
        return 1 + min3(edit_distance(a, b, al-1, bl), // Insert
                        edit_distance(a, b, al, bl-1), // Remove
                        edit_distance(a, b, al-1, bl-1) // Replace
                    );
}

#endif