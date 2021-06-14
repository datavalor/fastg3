#distutils: language = c++
cimport cython
from .c_ArrayKey cimport ArrayKey, ArrayKey_hash

from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from cython.operator import dereference, postincrement
from libcpp.pair cimport pair

ctypedef ArrayKey vector_row
ctypedef unordered_map[vector_row, int, ArrayKey_hash] inner_counter
ctypedef pair[int, inner_counter] pic
ctypedef unordered_map[vector_row, pic, ArrayKey_hash] counter
ctypedef unordered_map[vector_row, pic, ArrayKey_hash].iterator counter_iterator

@cython.boundscheck(False)
@cython.wraparound(False) 
def hash_based(const int[:, :] data_X, const int[:, :] data_Y):
    cdef:
        Py_ssize_t n_rows_X = data_X.shape[0]
        Py_ssize_t n_attrs_X = data_X.shape[1]
        Py_ssize_t n_rows_Y = data_Y.shape[0]
        Py_ssize_t n_attrs_Y = data_Y.shape[1]
    assert n_rows_X > 0
    assert n_rows_X == n_rows_Y

    cdef:
        long C = 0
        int tmp=0
        counter M0
        vector_row xd
        vector_row yd
        inner_counter ic
        counter_iterator cit
        Py_ssize_t n
    with nogil:
        for n in range(n_rows_X):
            xd = ArrayKey(&data_X[n,:][0], data_X[n,:].shape[0])
            yd = ArrayKey(&data_Y[n,:][0], data_Y[n,:].shape[0])
            cit = M0.find(xd)
            # neither xd nor yd are in the map
            if cit == M0.end():
                ic = inner_counter()
                ic[yd] = 1
                M0[xd] = pic(1, ic)
                C+=1
            else:
                # xd is in the map but not yd
                if dereference(cit).second.second.find(yd) == dereference(cit).second.second.end():
                    dereference(cit).second.second[yd] = 1
                # both xd and yd are in the map, incrementing and keeping track of the max
                else:
                    tmp = dereference(cit).second.second[yd]+1
                    dereference(cit).second.second[yd] = tmp
                    if dereference(cit).second.first<tmp:
                        dereference(cit).second.first=tmp
                        C+=1
    
    return 1-C/n_rows_X