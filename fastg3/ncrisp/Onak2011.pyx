#distutils: language = c++
cimport cython
from .VPEGraph cimport VPEGraph

import logging
logger = logging.getLogger('Yoshida2009')
import time

from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp.pair cimport pair
from libcpp cimport bool
from libc.stdlib cimport rand, RAND_MAX, qsort
from cython.operator import dereference, postincrement

ctypedef cpp_vector[size_t] index_vector
ctypedef pair[size_t, size_t] edge_type
ctypedef unordered_map[edge_type, bool, pair_hash] mo_cache_type
ctypedef pair[size_t, double] neighbors_rank 
ctypedef cpp_vector[neighbors_rank] neighbors_rank_vector

cdef struct NeighborsInfos:
    double lb # random number lower bound
    double next_lb # next random number lower bound
    unordered_map[size_t, double] assigned_number # ranking assigned to each known neighbor
    cpp_vector[neighbors_rank] sorted_list # sorted list of neighbors with ranking
    index_vector neighbors # list of direct neighbors

ctypedef unordered_map[size_t, NeighborsInfos] neighbors_map
ctypedef unordered_map[size_t, NeighborsInfos].iterator neighbors_map_iterator

cdef extern from "math.h":
    double log(double x) nogil
    double exp(double x) nogil
    double ceil(double x) nogil
    double floor(double x) nogil
    double pow(double base, double exponent);

cdef extern from "pair_hash.h":
    cdef cppclass pair_hash:
        pass

cdef int compare_edge_ranking_pair(const void * a, const void * b) nogil:
    cdef:
        neighbors_rank a_e = (<neighbors_rank*> a)[0]
        neighbors_rank b_e = (<neighbors_rank*> b)[0]
    if a_e.second<b_e.second: return -1
    else: return 1

cdef inline size_t _rand_from_one_to(size_t b) nogil:
    return <size_t> rand() % b + 1;

cdef class Onak2011:
    cdef:
        size_t n_nodes
        VPEGraph G
        index_vector nodes
        mo_cache_type matching_oracle_cache
        neighbors_map neighbors
        double dstar
        double init_next_lb

    def __cinit__(self, VPEGraph G):
        self.G = G
        self.nodes = self.G.nodes()
        self.n_nodes = self.nodes.size()
        self.dstar = self.n_nodes
        self.init_next_lb = pow(2,-log(self.dstar))
    
    cdef reset(self):
        self.matching_oracle_cache = mo_cache_type()
        self.neighbors.clear()

    cpdef double estimate_mvc_size(self, size_t n):
        try:
            assert n<=self.nodes.size()
        except AssertionError: 
            logger.error(f"Error: Sample size must be lower than the number of nodes in graph ({self.G.number_of_nodes()})")
            raise

        self.reset()
        cdef: 
            index_vector v_sample
            size_t i
            int mvc_sum = 0
            double W
        with nogil:
            # Reservoir sampling
            for i in range(n):
                v_sample.push_back(self.nodes[i])
            W=exp(log(rand()/RAND_MAX)/n)
            i=n
            while i < self.n_nodes:
                i+=<unsigned long>floor(log(rand()/RAND_MAX)/log(1-W))+1
                if i < self.n_nodes:
                    v_sample[_rand_from_one_to(n)-1] = self.nodes[i]
                    W*=exp(log(rand()/RAND_MAX)/n)
        
        for i in range(v_sample.size()):
            if self.vertex_oracle(v_sample[i]): mvc_sum+=1
        return mvc_sum/n

    cdef bool vertex_oracle(self, size_t v) nogil:
        cdef:
            size_t k
            neighbors_rank kth_neighbor
        k=0
        kth_neighbor = self.get_k_lowest_neighbors(v, k)
        while kth_neighbor.second!=RAND_MAX:
            if self.matching_oracle(edge_type(v, kth_neighbor.first)):
                return True
            k+=1
            kth_neighbor = self.get_k_lowest_neighbors(v, k)
        return False 

    cdef edge_type format_edge(self, edge_type e) nogil:
        if e.first<e.second: return e
        else: return edge_type(e.second, e.first)

    cdef NeighborsInfos get_n(self, size_t v) nogil:
        cdef: 
            neighbors_map_iterator nmi = self.neighbors.find(v)
            NeighborsInfos ni
        if nmi==self.neighbors.end():
            ni.lb=0
            ni.next_lb=self.init_next_lb
            ni.neighbors=self.G.neighbors(v)
            self.neighbors[v] = ni
            return ni
        else:
            return self.neighbors[v]

    cdef neighbors_rank get_k_lowest_neighbors(self, size_t v, size_t k) nogil:
        cdef: 
            NeighborsInfos ni = self.get_n(v) # getting vertex infos
            unordered_map[size_t, double].iterator an_iterator
            double p
            neighbors_rank_vector S
            size_t tmp
            cpp_vector[size_t] T # randomly selected vertices
            # Other considered vertex
            size_t w # considered neighbor
            double r # w rank
            NeighborsInfos niw 
            size_t i
            size_t j
        while ni.sorted_list.size()<k+1 and ni.lb<1:
            S.clear()
            an_iterator = ni.assigned_number.begin()
            while(an_iterator!=ni.assigned_number.end()):
                w = dereference(an_iterator).first
                r = ni.assigned_number[w]
                if ni.lb<=r and r<ni.next_lb:
                    S.push_back(neighbors_rank(w, r))
                postincrement(an_iterator)

            p = (ni.next_lb-ni.lb)/(1-ni.lb)
            T.clear()
            for i in range(ni.neighbors.size()):
                if rand()/RAND_MAX<=p:
                    T.push_back(i)

            for i in range(T.size()):
                w = ni.neighbors[T[i]]
                r = (ni.next_lb-ni.lb)*(rand()/RAND_MAX)+ni.lb
                niw = self.get_n(w)

                if niw.lb<=ni.lb:
                    tmp = RAND_MAX
                    for j in range(S.size()):
                        if w==S[j].first and r<S[j].second:
                            tmp = j

                    if tmp!=RAND_MAX:
                        ni.assigned_number[w]=r
                        niw.assigned_number[v]=r
                        S[tmp]=neighbors_rank(w, r)
                    
                    if ni.assigned_number.find(w)==ni.assigned_number.end():
                        ni.assigned_number[w]=r
                        niw.assigned_number[v]=r
                        S.push_back(neighbors_rank(w, r))
                    self.neighbors[w] = niw
            
            qsort(&S[0], S.size(), sizeof(S[0]), compare_edge_ranking_pair)
            for i in range(S.size()): ni.sorted_list.push_back(S[i])
            ni.lb = ni.next_lb
            ni.next_lb = 2*ni.next_lb

        self.neighbors[v] = ni
        if ni.sorted_list.size()<k+1: return neighbors_rank(v, RAND_MAX)
        else: return ni.sorted_list[k]
    
    cdef bool matching_oracle(self, edge_type e) nogil:
        e = self.format_edge(e)
        if self.matching_oracle_cache.find(e)!=self.matching_oracle_cache.end():
            return self.matching_oracle_cache[e]

        cdef: 
            size_t u = e.first
            size_t v = e.second
            size_t k1 = 0
            size_t k2 = 0
            neighbors_rank n1 = self.get_k_lowest_neighbors(u, k1)
            neighbors_rank n2 = self.get_k_lowest_neighbors(v, k2)

        while n1.first!=v or n2.first!=u:
            if n1.second < n2.second:
                if self.matching_oracle(edge_type(u, n1.first)): 
                    self.matching_oracle_cache[e] = False
                    return False
                k1+=1
                n1 = self.get_k_lowest_neighbors(u, k1)
            else:
                if self.matching_oracle(edge_type(v, n2.first)): 
                    self.matching_oracle_cache[e] = False
                    return False
                k2+=1
                n2 = self.get_k_lowest_neighbors(v, k2)

        self.matching_oracle_cache[e] = True
        return True