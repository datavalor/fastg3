#distutils: language = c++
cimport cython
from .VPEGraph cimport VPEGraph

import logging
logger = logging.getLogger('Yoshida2009')
import time

from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp cimport bool
from libc.stdlib cimport rand, RAND_MAX

ctypedef cpp_vector[size_t] index_vector

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

cdef class SubGIC:
    cdef:
        size_t n_nodes
        VPEGraph G
        index_vector nodes
        int nodes_list
        unordered_map[size_t, bool] cover # -1 being visited, 0 not in cover, 1 in cover
        unordered_map[size_t, bool] discovered
        unordered_map[size_t, index_vector] degree_map

    def __cinit__(self, VPEGraph G):
        self.G = G
        self.nodes = self.G.nodes()
        self.n_nodes = self.nodes.size()
    
    cdef reset(self):
        self.cover.clear()

    def estimate_mvc_size(self, size_t n):
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
        
        cdef size_t v_degree
        for i in range(v_sample.size()):
            print(f'--------------------> {v_sample[i]} - {self.G.neighbors(v_sample[i])} neighbors')
            self.explore_vertex_area(v_sample[i], v_sample[i])
            self.handle_degree(self.G.degree(v_sample[i]))
            if self.cover[v_sample[i]]: mvc_sum += 1

        # print(self.cover)
        # test=0
        cover_list = []
        for k, v in self.cover:
            if v: 
                cover_list.append(k)
        # print(test/len(self.cover))

        print(self.G.neighbors(12))
        print(self.G.neighbors(13))
        
        return cover_list
        # return mvc_sum/n

    cdef void handle_degree(self, size_t degree) nogil:
        # with gil: print("------------>")
        cdef:
            index_vector node_list = self.degree_map[degree]
            size_t i
            size_t j
            size_t k
            size_t tmp
            index_vector neighbors1
        for j in range(node_list.size()):
                # Uniform shuffling
                k = _rand_from_one_to(node_list.size()-j)+j-1
                tmp = node_list[j]
                node_list[j] = node_list[k]
                node_list[k] = tmp
                with gil: print(node_list[j], self.G.degree(node_list[j]), self.G.neighbors(node_list[j]))
                # Adding if possible
                if self.cover.find(node_list[j])==self.cover.end():
                    neighbors1=self.G.neighbors(node_list[j])
                    with gil: print("ADDED", node_list[j], neighbors1)
                    for k in range(neighbors1.size()):
                        self.cover[neighbors1[k]] = True
                    self.cover[node_list[j]] = False
        self.degree_map[degree].clear()

    cdef void explore_vertex_area(self, size_t v, size_t v_obj) nogil:
        self.discovered[v] = True

        cdef: 
            index_vector neighbors = self.G.neighbors(v)
            index_vector current_degree_list
            size_t v_degree = neighbors.size()
            size_t n_degree
            size_t i
            bool to_visit
        self.degree_map[v_degree].push_back(v)
        for i in range(neighbors.size()):
            n_degree = self.G.degree(neighbors[i])
            to_visit=True
            if self.discovered.find(neighbors[i]) != self.discovered.end():# or self.cover.find(neighbors[i]) != self.cover.end():
                to_visit=False
            if to_visit and n_degree<v_degree:
                self.explore_vertex_area(neighbors[i], v_obj)
                self.handle_degree(n_degree)
            elif to_visit and n_degree==v_degree:
                self.explore_vertex_area(neighbors[i], v_obj)