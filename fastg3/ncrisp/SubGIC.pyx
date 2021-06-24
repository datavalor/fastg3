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

ctypedef cpp_vector[size_t] index_vector
ctypedef unordered_map[size_t, double] ranking_map
ctypedef pair[size_t, size_t] vwd #(vertex, degree)
ctypedef pair[size_t, double] vwr #(vertex, ranking)

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

cdef int comp_vertex_with_ranking(const void * a, const void * b) nogil:
    cdef:
        vwr a_e = (<vwr*> a)[0]
        vwr b_e = (<vwr*> b)[0]
    if a_e.second<b_e.second: return -1
    else: return 1

cdef class SubGIC:
    cdef:
        size_t n_nodes
        VPEGraph G
        index_vector nodes
        int nodes_list
        unordered_map[size_t, bool] cover # -1 being visited, 0 not in cover, 1 in cover
        unordered_map[size_t, bool] discovered
        ranking_map vertex_ranking
        unordered_map[size_t, cpp_vector[vwr]] ranked_degree_map

    def __cinit__(self, VPEGraph G):
        self.G = G
        self.nodes = self.G.nodes()
        self.n_nodes = self.nodes.size()
    
    cdef reset(self):
        self.cover.clear()

    def estimate_mvc_size(self, size_t n):
        # Initialisation
        try:
            assert n<=self.nodes.size()
        except AssertionError: 
            logger.error(f"Error: Sample size must be lower than the number of nodes in graph ({self.G.number_of_nodes()})")
            raise
        self.reset()

        # Reservoir sampling
        cdef: 
            index_vector v_sample
            size_t i
            size_t j
            
            double W
        with nogil:
            for i in range(n):
                v_sample.push_back(self.nodes[i])
            W=exp(log(rand()/RAND_MAX)/n)
            i=n+1
            while i < self.n_nodes:
                i+=<unsigned long>floor(log(rand()/RAND_MAX)/log(1-W))+1
                if i < self.n_nodes:
                    v_sample[_rand_from_one_to(n)-1] = self.nodes[i]
                    W*=exp(log(rand()/RAND_MAX)/n)
        
        # Exploring sampled vertices
        cdef:
            size_t v_index
            size_t v_degree
            int mvc_sum = 0
        with nogil:
            for i in range(v_sample.size()):
                v_index = v_sample[i]
                v_degree = self.G.degree(v_sample[i])
                # print(f'##############> {v_sample[i]} - {self.G.neighbors(v_sample[i])} neighbors')
                self.ranked_degree_map.clear()
                self.discovered.clear()
                if self.cover.find(v_index) == self.cover.end() and not self.dfs(v_index, v_index):
                    self.add_ranked_degree(self.G.degree(v_index), v_index)
                if self.cover[v_index]: mvc_sum += 1

        # print(len(self.cover), "vertices explored total!")

        return mvc_sum/n

    cdef void add_ranked_degree(self, size_t degree, size_t v_obj) nogil:
        # Getting node list and sorting by rank
        cdef cpp_vector[vwr] node_list = self.ranked_degree_map[degree]
        qsort(&node_list[0], node_list.size(), sizeof(node_list[0]), comp_vertex_with_ranking)

        # Handling sorted nodes one by one
        cdef:
            size_t v_index
            size_t n_index
            size_t i
            size_t j
            index_vector neighbors
        for i in range(node_list.size()):
                v_index = node_list[i].first
                # Updating cover if needed
                if self.cover.find(v_index)==self.cover.end():
                    neighbors=self.G.neighbors(v_index)
                    for j in range(neighbors.size()): self.cover[neighbors[j]] = True
                    self.cover[v_index] = False
                # Early stopping if possible
                if self.cover.find(v_obj) != self.cover.end(): 
                    self.ranked_degree_map[degree].clear()
                    return
        self.ranked_degree_map[degree].clear()

    cdef double get_vertex_rank(self, size_t v_index) nogil:
        if self.vertex_ranking.find(v_index)==self.vertex_ranking.end():
            self.vertex_ranking[v_index] = rand()/RAND_MAX
            return self.vertex_ranking[v_index]
        else:
            return self.vertex_ranking[v_index]

    cdef bool dfs(self, size_t v_index, size_t v_obj) nogil:
        self.discovered[v_index] = True
        # Getting vertex infos
        cdef: 
            index_vector v_neighbors = self.G.neighbors(v_index)
            size_t v_degree = v_neighbors.size()
            double v_ranking = self.get_vertex_rank(v_index)
            vwr v_vwr = vwr(v_index, v_ranking)
        self.ranked_degree_map[v_degree].push_back(v_vwr)

        # Exploring
        cdef:
            size_t n_index
            size_t n_degree
            size_t i
            bool to_visit
        for i in range(v_degree):
            n_index = v_neighbors[i]
            n_degree = self.G.degree(n_index)
            
            if self.discovered.find(n_index) != self.discovered.end() or self.cover.find(n_index) != self.cover.end(): to_visit=False
            else: to_visit=True

            if to_visit and n_degree<v_degree:
                if self.dfs(n_index, v_obj): return True
                self.add_ranked_degree(n_degree, v_obj) 
                if self.cover.find(v_obj)!=self.cover.end(): return True
            elif to_visit and n_degree==v_degree:
                if self.dfs(n_index, v_obj): return True
        
        return False