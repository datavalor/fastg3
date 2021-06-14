from cython.operator cimport dereference, postincrement
from libcpp.string cimport string
from libcpp.pair cimport pair
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp cimport bool

ctypedef pair[size_t, size_t] vp_type
ctypedef cpp_vector[vp_type] vp_list
ctypedef cpp_vector[string] attr_list

ctypedef cpp_vector[size_t] block_type
ctypedef cpp_vector[block_type] blocks_type
ctypedef cpp_vector[size_t] index_vector

cdef extern from "cpp/NumAttribute.h": pass
cdef extern from "cpp/StrAttribute.h": pass
cdef extern from "cpp/NumDistance.h": pass
cdef extern from "cpp/StrDistance.h": pass

cdef extern from "cpp/Dataframe.h":
    cdef cppclass Dataframe:
        Dataframe(size_t* index, size_t pnrows) nogil except +
        void add_column[T](string col_name, T* attr, string metric, double thresold) nogil except +
        void add_str_column(string col_name, cpp_vector[string] attr, string metric, double thresold) nogil except +
        size_t get_n_rows() nogil except +
        attr_list get_columns() nogil except +
        void set_block_index(cpp_vector[long] input) nogil except +
        long get_block_index(size_t i) nogil except +
        index_vector get_user_index() nogil except +
        size_t get_mem_from_user_index(size_t i) nogil except +
        vp_list bf_join(block_type block, attr_list x_attrs, attr_list y_attrs) nogil except +
        vp_list ordered_join(block_type block, attr_list x_attrs, attr_list y_attrs) nogil except +
        index_vector bf_row_join(block_type block, size_t row, attr_list x_attrs, attr_list y_attrs) nogil except +
        index_vector ordered_row_join(block_type block, size_t row, attr_list x_attrs, attr_list y_attrs) nogil except +