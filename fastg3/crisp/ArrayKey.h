#include <functional>
#include <iostream>

std::hash<int> int_hasher;

struct ArrayKey {
  const int* value;
  unsigned int size;

  ArrayKey(){}
  ArrayKey(const int* v, unsigned int size) : value(v), size(size){}
};

struct ArrayKey_hash{
  size_t operator()(ArrayKey lak) const {
    size_t seed = 0;
    for(unsigned int i = 0; i < lak.size; i++)
    {
        seed ^= int_hasher(lak.value[i]) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    }
    return seed;
  }
};

bool operator==(const ArrayKey lhs, const ArrayKey rhs){
    for(unsigned int i = 0; i < lhs.size; i++)
    {
        if(lhs.value[i] != rhs.value[i]){
          return false;
        }
    }
    return true;
}
