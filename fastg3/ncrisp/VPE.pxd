#distutils: language = c++
from .c_Dataframe cimport Dataframe

from cython.operator cimport dereference, postincrement
from libcpp.string cimport string
from libcpp.pair cimport pair
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp cimport bool

ctypedef pair[size_t, size_t] vp_type
ctypedef cpp_vector[vp_type] vp_list
ctypedef cpp_vector[string] attr_list
ctypedef unordered_map[size_t, cpp_vector[size_t]] adjacency_map
ctypedef unordered_map[size_t, cpp_vector[size_t]].iterator adjacency_map_iterator

ctypedef cpp_vector[size_t] block_type
ctypedef cpp_vector[block_type] blocks_type
ctypedef cpp_vector[size_t] index_vector

cdef class VPE:
    cdef: 
        Dataframe * dfc
        attr_list blocking_attrs
        attr_list selected_xattrs
        attr_list selected_yattrs
        int join_type
        string join_attr
        bool verbose
        blocks_type blocks 
        dict blocks_dict

    cpdef vp_list enum_vps(self)
    cpdef size_t number_of_rows(self)
    cdef index_vector list_all_ids(self) nogil
    cdef index_vector enum_neighboring_vps(self, size_t df_id) nogil
    cdef vp_list join_proxy(self, block_type block, attr_list x_attrs, attr_list y_attrs, int join_type) nogil except +
    cdef index_vector row_join_proxy(self, block_type block, size_t row_id,  attr_list x_attrs, attr_list y_attrs, int join_type) nogil except +