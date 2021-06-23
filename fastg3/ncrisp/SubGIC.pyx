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
ctypedef unordered_map[size_t, double] ranking_map
ctypedef pair[size_t, size_t] vwd #(vertex, degree)

cdef extern from "pair_hash.h":
    cdef cppclass pair_hash:
        pass

cdef extern from "math.h":
    double log(double x) nogil
    double exp(double x) nogil
    double ceil(double x) nogil
    double floor(double x) nogil

cdef inline size_t _rand_from_one_to(size_t b) nogil:
    return <size_t> rand() % b + 1;


cdef int comp_vertex_with_degree(const void * a, const void * b) nogil:
    cdef:
        vwd a_e = (<vwd*> a)[0]
        vwd b_e = (<vwd*> b)[0]
    if a_e.second<b_e.second: return -1
    else: return 1

cdef class SubGIC:
    cdef:
        size_t n_nodes
        VPEGraph G
        index_vector nodes
        int nodes_list
        unordered_map[size_t, bool] cover
        unordered_map[size_t, bool] discovered
        ranking_map vertex_ranking

    def __cinit__(self, VPEGraph G):
        self.G = G
        self.nodes = self.G.nodes()
        self.n_nodes = self.nodes.size()
    
    cdef reset(self):
        self.cover.clear()

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
            size_t j
            int mvc_sum = 0
            double W
        with nogil:
            # Reservoir sampling
            for i in range(n):
                v_sample.push_back(self.nodes[i])
            W=exp(log(rand()/RAND_MAX)/n)
            i=n+1
            while i < self.n_nodes:
                i+=<unsigned long>floor(log(rand()/RAND_MAX)/log(1-W))+1
                if i < self.n_nodes:
                    v_sample[_rand_from_one_to(n)-1] = self.nodes[i]
                    W*=exp(log(rand()/RAND_MAX)/n)
        
        for i in range(v_sample.size()):
            # print(f'--------------------> {v_sample[i]} - {self.G.neighbors(v_sample[i])} neighbors')
            self.discovered.clear()
            if self.vertex_oracle(v_sample[i]):
                mvc_sum+=1

        return mvc_sum/n

    cdef double get_vertex_rank(self, size_t v) nogil:
        if self.vertex_ranking.find(v)==self.vertex_ranking.end():
            self.vertex_ranking[v] = rand()/RAND_MAX
            return self.vertex_ranking[v]
        else:
            return self.vertex_ranking[v]

    cdef bool vertex_oracle(self, size_t v) nogil:
        self.discovered[v] = True
        if self.cover.find(v) != self.cover.end(): 
            return self.cover[v]

        cdef: 
            index_vector neighbors = self.G.neighbors(v)
            cpp_vector[vwd] neighbors_wd
            size_t v_degree = neighbors.size()
            size_t i
            size_t n_index
            size_t n_degree
            bool to_visit
            double v_ranking
        for i in range(v_degree):
            neighbors_wd.push_back(vwd(neighbors[i], self.G.degree(neighbors[i])))
        qsort(&neighbors_wd[0], neighbors_wd.size(), sizeof(neighbors_wd[0]), comp_vertex_with_degree)
        i = 0
        while(i<v_degree and neighbors_wd[i].second <= v_degree):
            n_index = neighbors_wd[i].first
            n_degree = neighbors_wd[i].second
            to_visit=True
            if self.discovered.find(n_index) != self.discovered.end() or self.cover.find(n_index) != self.cover.end():
                to_visit=False
            if to_visit and (n_degree<v_degree or (n_degree==v_degree and self.get_vertex_rank(n_index)<self.get_vertex_rank(v))):
                self.vertex_oracle(n_index)
                if self.cover.find(v) != self.cover.end():
                    return self.cover[v]
            i+=1

        for i in range(neighbors.size()): self.cover[neighbors[i]] = True
        self.cover[v] = False
        return False