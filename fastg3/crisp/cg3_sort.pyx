#distutils: language = c++
cimport cython
from libcpp cimport bool

@cython.boundscheck(False)
@cython.wraparound(False) 
cdef bool _slices_equal(const int[:] s1, const int[:] s2, Py_ssize_t n_attrs) nogil except +:
    cdef Py_ssize_t i
    for i in range(n_attrs):
        if s1[i] != s2[i]:
            return False
    return True

@cython.boundscheck(False)
@cython.wraparound(False) 
def sort_based(const int[:, :] data_X, const int[:, :] data_Y):
    cdef:
        Py_ssize_t n_rows_X = data_X.shape[0]
        Py_ssize_t n_attrs_X = data_X.shape[1]
        Py_ssize_t n_rows_Y = data_Y.shape[0]
        Py_ssize_t n_attrs_Y = data_Y.shape[1]
    assert n_rows_X > 0
    assert n_rows_X == n_rows_Y
    
    cdef:
        Py_ssize_t x_cur_index = 0
        Py_ssize_t y_cur_index = 0
        long C = 0
        long c_cur = 0
        long c_max = 0
        Py_ssize_t n
    with nogil:
        for n in range(n_rows_X):
            if not _slices_equal(data_X[n,:], data_X[x_cur_index,:], n_attrs_X):
                C += c_max
                c_cur = 0
                c_max = 0
                x_cur_index = n
                y_cur_index = n

            if _slices_equal(data_Y[n,:], data_Y[y_cur_index,:], n_attrs_Y): 
                c_cur += 1
            else:
                c_cur = 1
                y_cur_index = n
            if c_max<c_cur: c_max = c_cur
        C += c_max

    return 1-C/n_rows_X