#ifndef NEIGBORSINFOS_H
#define NEIGBORSINFOS_H


class NeighborsInfos{
public:
        double lb //random number lower bound
        double next_lb //next random number lower bound
        unordered_map[size_t, double] //assigned_number # ranking assigned to each known neighbor
        cpp_vector[neighbors_rank] sorted_list # sorted list of neighbors with ranking
};

#endif