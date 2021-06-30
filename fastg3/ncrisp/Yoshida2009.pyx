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
ctypedef cpp_vector[edge_type] edge_list
ctypedef unordered_map[edge_type, double, pair_hash] ranking_type
ctypedef unordered_map[edge_type, double, pair_hash].iterator ranking_type_iterator
ctypedef unordered_map[edge_type, bool, pair_hash] mo_cache_type
ctypedef pair[edge_type, double] edge_ranking_pair

cdef extern from "pair_hash.h":
    cdef cppclass pair_hash:
        pass

cdef extern from "math.h":
    double log(double x) nogil
    double exp(double x) nogil
    double ceil(double x) nogil
    double floor(double x) nogil

cdef int compare_edge_ranking_pair(const void * a, const void * b) nogil:
    cdef:
        edge_ranking_pair a_e = (<edge_ranking_pair*> a)[0]
        edge_ranking_pair b_e = (<edge_ranking_pair*> b)[0]
    if a_e.second<b_e.second: return -1
    else: return 1

cdef inline size_t _rand_from_one_to(size_t b) nogil:
    return <size_t> rand() % b + 1;

cdef class Yoshida2009:
    cdef:
        size_t n_nodes
        VPEGraph G
        index_vector nodes
        int nodes_list
        ranking_type ranking
        mo_cache_type matching_oracle_cache
        unordered_map[size_t, index_vector] neighbors_memoize

        double pfg_counter

    def __cinit__(self, VPEGraph G):
        self.G = G
        self.nodes = self.G.nodes()
        self.n_nodes = self.nodes.size()
    
    cdef reset(self):
        self.ranking = ranking_type()
        self.matching_oracle_cache = mo_cache_type()

    cdef edge_type format_edge(self, edge_type e) nogil:
        if e.first<e.second: return e
        else: return edge_type(e.second, e.first)

    cdef double get_edge_ranking(self, edge_type e) nogil:
        e=self.format_edge(e)
        cdef: 
            ranking_type_iterator rti = self.ranking.find(e)
            double rand_n
        if rti==self.ranking.end(): 
            rand_n = rand()/RAND_MAX
            self.ranking[e]=rand_n
            return rand_n
        else:
            return dereference(rti).second

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
            if self.vertex_oracle(v_sample[i]): mvc_sum+=1
        
        # print("------->", self.pfg_counter)
        return mvc_sum/n

    cdef bool vertex_oracle(self, size_t v) nogil:
        cdef: 
            edge_list neighboring_edges = self.G.node_iedges(v)
            cpp_vector[edge_ranking_pair] nedges
            size_t i
        for i in range(neighboring_edges.size()):
            nedges.push_back(edge_ranking_pair(neighboring_edges[i], self.get_edge_ranking(neighboring_edges[i])))
        qsort(&nedges[0], nedges.size(), sizeof(nedges[0]), compare_edge_ranking_pair)
        for i in range(nedges.size()):
            if self.matching_oracle(nedges[i].first):
                return True
        return False
    
    cdef bool matching_oracle(self, edge_type e) nogil:
        e = self.format_edge(e)
        if self.matching_oracle_cache.find(e)!=self.matching_oracle_cache.end():
            return self.matching_oracle_cache[e]

        cdef: 
            double rank = self.get_edge_ranking(e)
            edge_list neighboring_edges = self.G.edge_iedges(e)
            cpp_vector[edge_ranking_pair] nedges
            size_t i

            cpp_vector[double] r_number

        for i in range(neighboring_edges.size()):
            nedges.push_back(edge_ranking_pair(neighboring_edges[i], self.get_edge_ranking(neighboring_edges[i])))
        # with gil: start = time.time()
        qsort(&nedges[0], nedges.size(), sizeof(nedges[0]), compare_edge_ranking_pair)
        # with gil: self.pfg_counter+=time.time()-start
            
        i=0
        while i<nedges.size() and nedges[i].second<rank:
            if self.matching_oracle(nedges[i].first): 
                self.matching_oracle_cache[e] = False
                return False
            i+=1

        cdef size_t j
        for j in range(i,nedges.size()): self.matching_oracle_cache[self.format_edge(nedges[i].first)] = False
        self.matching_oracle_cache[e] = True
        return True