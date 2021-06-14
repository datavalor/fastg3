#distutils: language = c++
from .VPE cimport VPE

from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp.pair cimport pair
from libcpp cimport bool

ctypedef cpp_vector[size_t] index_vector
ctypedef cpp_vector[size_t].iterator index_vector_iterator
ctypedef pair[size_t, size_t] edge_type
ctypedef cpp_vector[edge_type] edge_list

ctypedef unordered_map[size_t, index_vector] neighbors_memoize_type
ctypedef unordered_map[size_t, cpp_vector[size_t]].iterator neighbors_memoize_iterator

cdef class VPEGraph:
    cdef:
        VPE vpe
        index_vector nodes_list
        size_t n_nodes
        size_t max_id
        neighbors_memoize_type neighbors_memoize

    cdef index_vector nodes(self) nogil
    cdef edge_list node_iedges(self, size_t p) nogil
    cdef edge_list edge_iedges(self, edge_type p) nogil
    cdef index_vector neighbors(self, size_t p) nogil
    cdef size_t degree(self, size_t p) nogil
    cdef size_t number_of_nodes(self) nogil