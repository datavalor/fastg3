#distutils: language = c++
cimport cython
from .VPE cimport VPE

import logging
logger = logging.getLogger('VPEGraph')

from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp.pair cimport pair
from libcpp cimport bool
from cython.operator import dereference, postincrement

cdef class VPEGraph:
    def __cinit__(self, VPE v):
        self.vpe = v
        self.nodes_list = self.vpe.list_all_ids()
        self.n_nodes = self.nodes_list.size()
        self.max_id = 0
        for i in range(self.nodes_list.size()): 
            if self.nodes_list[i]>self.max_id:
                self.max_id=self.nodes_list[i]

    cdef index_vector nodes(self) nogil:
        return self.nodes_list

    cdef edge_list edge_iedges(self, edge_type e) nogil:
        # Return all the violating pairs where p[0] or p[1] is involved if p is a tuple of ids
        cdef:
            edge_list el
            size_t i
            size_t node_id
            bool edge_in_graph = False
            index_vector ns
            index_vector_iterator ivi
        
        ns = self.neighbors(e.first)
        with nogil:
            for i in range(ns.size()):
                if ns[i]==e.second:
                    edge_in_graph=True
                else:
                    el.push_back(edge_type(e.first, ns[i]))
        if not edge_in_graph:
            # logger.warning(f"Edge {e} not in graph.")
            return edge_list()
        ns = self.neighbors(e.second)
        with nogil:
            for i in range(ns.size()):
                if ns[i]!=e.first:
                    el.push_back(edge_type(e.second, ns[i]))
        return el

    cdef edge_list node_iedges(self, size_t p) nogil:
        # Return all the violating pairs where p is involved if p is an id
        cdef: 
            edge_list el
            size_t i
            index_vector ns
        ns = self.neighbors(p)
        for i in range(ns.size()):
            el.push_back(edge_type(p, ns[i]))
        return el

    cdef index_vector neighbors(self, size_t p) nogil:
        cdef neighbors_memoize_iterator nmi = self.neighbors_memoize.find(p)
        if nmi != self.neighbors_memoize.end(): 
            return dereference(nmi).second
        # Returns all the tuples in violation with p
        cdef index_vector ns 
        ns = self.vpe.enum_neighboring_vps(p)
        self.neighbors_memoize[p] = ns
        return ns

    cdef size_t degree(self, size_t p) nogil:
        # Returns the number of tuples in violation with p
        return self.neighbors(p).size()

    cdef size_t number_of_nodes(self) nogil:
        # Returns the number of tuples in memory
        return self.n_nodes