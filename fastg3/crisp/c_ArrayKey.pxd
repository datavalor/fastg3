cdef extern from "ArrayKey.h":
    cdef cppclass ArrayKey:
        ArrayKey(const int*, unsigned int size) nogil except +
        ArrayKey() nogil except +
    cdef cppclass ArrayKey_hash:
        pass