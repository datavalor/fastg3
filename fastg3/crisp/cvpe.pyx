#distutils: language = c++
cimport cython
from .c_ArrayKey cimport ArrayKey, ArrayKey_hash

from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp.pair cimport pair
from cython.operator import dereference, postincrement

ctypedef ArrayKey vector_row
ctypedef cpp_vector[size_t] id_array
ctypedef unordered_map[vector_row, id_array, ArrayKey_hash] inner_counter
ctypedef unordered_map[vector_row, id_array, ArrayKey_hash].iterator inner_counter_iterator
ctypedef unordered_map[vector_row, inner_counter, ArrayKey_hash] counter

ctypedef pair[size_t, size_t] vp_type
ctypedef cpp_vector[vp_type] vp_list

cdef ArrayKey _make_key(const int[:] arr) nogil:
    return ArrayKey(&arr[0], arr.shape[0])

@cython.boundscheck(False)
@cython.wraparound(False) 
def vpe(const size_t[:] index, const int[:, :] data_X, const int[:, :] data_Y):
    cdef:
        Py_ssize_t n_rows_X = data_X.shape[0]
        Py_ssize_t n_attrs_X = data_X.shape[1]
        Py_ssize_t n_rows_Y = data_Y.shape[0]
        Py_ssize_t n_attrs_Y = data_Y.shape[1]
    assert n_rows_X > 0
    assert n_rows_X == n_rows_Y
    
    cdef:
        counter M0
        vector_row xd
        vector_row yd
        inner_counter ic
        Py_ssize_t n
    with nogil:
        for n in range(n_rows_X):
            xd = _make_key(data_X[n,:])
            yd = _make_key(data_Y[n,:])
            if M0.find(xd) == M0.end():
                ic = inner_counter()
                ic[yd].push_back(index[n])
                M0[xd] = ic
            else:
                M0[xd][yd].push_back(index[n])

    cdef:
        vp_list vps
        inner_counter_iterator inner_it0
        inner_counter_iterator inner_it1
        unordered_map[vector_row, inner_counter, ArrayKey_hash].iterator it = M0.begin()
        id_array curr_ids
        id_array other_ids
        size_t i
        size_t j
    with nogil:
        while(it != M0.end()):
            inner_it0 = dereference(it).second.begin()
            while(inner_it0 != dereference(it).second.end()):
                curr_ids = dereference(inner_it0).second
                inner_it1 = inner_it0
                postincrement(inner_it1)
                while(inner_it1 != dereference(it).second.end()):
                    other_ids = dereference(inner_it1).second
                    for i in range(curr_ids.size()):
                        for j in range(other_ids.size()):
                            vps.push_back(vp_type(curr_ids[i],other_ids[j]))
                    postincrement(inner_it1)
                postincrement(inner_it0)
            postincrement(it)
            
    return vps