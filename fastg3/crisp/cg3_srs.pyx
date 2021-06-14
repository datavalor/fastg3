#distutils: language = c++
cimport cython
from .c_ArrayKey cimport ArrayKey, ArrayKey_hash

from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from cython.operator import dereference, postincrement
from libcpp cimport bool
from libc.stdlib cimport rand, RAND_MAX
from libcpp.pair cimport pair

ctypedef ArrayKey vector_row
ctypedef unordered_map[vector_row, long, ArrayKey_hash] first_pass
ctypedef unordered_map[vector_row, long, ArrayKey_hash].iterator first_pass_iterator
ctypedef cpp_vector[unsigned long] second_pass_counter
ctypedef unordered_map[vector_row, second_pass_counter, ArrayKey_hash] second_pass
ctypedef unordered_map[vector_row, second_pass_counter, ArrayKey_hash].iterator second_pass_iterator

#in the pair, the first number if the size of the reservoir and the second the counter to perform reservoir sampling
ctypedef pair[unsigned long, unsigned long] reservoir_pair
ctypedef unordered_map[vector_row, reservoir_pair, ArrayKey_hash] reservoir_size_pass_2 
ctypedef unordered_map[vector_row, reservoir_pair, ArrayKey_hash].iterator reservoir_size_pass_2_iterator

cdef inline ArrayKey _make_key(const int[:] arr) nogil:
    return ArrayKey(&arr[0], arr.shape[0])

cdef extern from "math.h":
    double log(double x) nogil
    double exp(double x) nogil
    double ceil(double x) nogil
    double floor(double x) nogil

cdef inline unsigned long _rand_from_one_to(long b) nogil except +:
    return <long> rand() % b + 1;

def srs_based(
    const int[:, :] data_X, 
    const int[:, :] data_Y, 
    unsigned long t, 
    unsigned long z=20, 
    bool auto_z=False,
    double confidence=0.95,
    double error=0.01
):
    cdef:
        unsigned long n_rows_X = data_X.shape[0]
        unsigned long n_attrs_X = data_X.shape[1]
        unsigned long n_rows_Y = data_Y.shape[0]
        unsigned long n_attrs_Y = data_Y.shape[1]
    assert n_rows_X > 0
    assert n_rows_X == n_rows_Y

    cdef:
        vector_row xd
        vector_row yd
        unsigned long n

    # -----> FIRST PASS
    cdef:
        cpp_vector[unsigned long] rs1
        unsigned long j
        double W
    ## Reservoir sampling
    with nogil:
        for n in range(t):
            rs1.push_back(n)
        W=exp(log(rand()/RAND_MAX)/t)
        n = t+1
        while n < n_rows_X:
            n+=<unsigned long>floor(log(rand()/RAND_MAX)/log(1-W))+1
            if n < n_rows_X:
                rs1[_rand_from_one_to(t)-1] = n
                W*=exp(log(rand()/RAND_MAX)/t)
    cdef:
        first_pass S1
        second_pass S2
    ## Sampling
    with nogil:
        for n in range(rs1.size()):
            # with gil: print(rs1[n])
            xd = _make_key(data_X[rs1[n],:])
            if S1.find(xd) == S1.end():
                S1[xd]=1
                S2[xd]=second_pass_counter()
            else:
                S1[xd]+=1
    cdef: 
        reservoir_size_pass_2 zs
        first_pass_iterator it_fp = S1.begin()
        unsigned long tmp
        unsigned long total=0
        double add_term
    with nogil:
        if auto_z:
            add_term = 2*error*error/log(2.0/(1-confidence))
            while(it_fp != S1.end()):
                xd = dereference(it_fp).first
                # with gil: print(S1[xd], (n_rows_X*S1[xd]/<double>t), add_term)
                tmp = <unsigned long> max(ceil(1/(1.0/(n_rows_X*S1[xd]/<double>t) + add_term)), 2)
                zs[xd] = reservoir_pair(tmp, tmp)
                postincrement(it_fp)
        else:
            while(it_fp != S1.end()):
                xd = dereference(it_fp).first
                zs[xd] = reservoir_pair(z, z)
                postincrement(it_fp)

    ## -----> SECOND PASS
    cdef: 
        unsigned long zx
        second_pass_iterator it_find
        reservoir_pair rsp2_pair
    with nogil:
        for n in range(n_rows_X):
            xd = _make_key(data_X[n,:])
            it_find = S2.find(xd)
            if it_find != S2.end():
                rsp2_pair = zs[xd]
                if dereference(it_find).second.size() < rsp2_pair.first:
                    dereference(it_find).second.push_back(n)
                else:
                    zs[xd].second=rsp2_pair.second+1
                    j = _rand_from_one_to(rsp2_pair.second+1)-1
                    if j < rsp2_pair.first:
                        dereference(it_find).second[j] = n

    ## -----> WEIGHTED SUM
    cdef:
        double C = 0
        long max_val
        first_pass_iterator it_pass1 = S1.begin()
        second_pass_counter ec_vec
        first_pass counter
        first_pass_iterator counter_iterator_find
    with nogil:
        while(it_pass1 != S1.end()):
            max_val = 1
            counter.clear()
            ec_vec = S2[dereference(it_pass1).first]
            for n in range(ec_vec.size()):
                yd = _make_key(data_Y[ec_vec[n],:])
                counter_iterator_find = counter.find(yd)
                if counter_iterator_find == counter.end(): 
                    counter[yd]=1
                else: 
                    dereference(counter_iterator_find).second=dereference(counter_iterator_find).second+1
                    if max_val<dereference(counter_iterator_find).second: max_val+=1
            if ec_vec.size()!=0:
                C += dereference(it_pass1).second*(max_val/(<long>ec_vec.size()))
            postincrement(it_pass1)  
            
    return 1-C/t