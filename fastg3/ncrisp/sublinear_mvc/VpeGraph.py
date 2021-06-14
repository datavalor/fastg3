# https://stackoverflow.com/questions/22231912/correct-way-to-cache-only-some-methods-of-a-class-with-joblib
import numpy as np
import logging
import numbers

logger = logging.getLogger('mvc')

class VpeGraph:
    def __init__(self, VPE, verbose=False):
        self.vpe = VPE
        self.neighbors_memoize = {}
        self.nodes = self.vpe.list_all_ids()
        self.n_nodes = len(self.nodes)

    # def nodes(self):
    #     # Returns the indexes of all the tuples in memory
    #     return self.nodes_list

    def edges(self, p):
        # Return all the violation pairs where p is involved if p is an id
        # Return all the violation pairs where p[0] or p[1] is involved if p is a tuple of ids
        if isinstance(p, tuple): # an edge is given
            ns = self.neighbors(p[0])
            try:
                assert p[1] in ns
            except AssertionError:
                logger.error(f'{p} is not an edge in the graph.')
                raise
            return [(p[0],v) for v in ns if v!=p[1]] \
                +[(p[1],v) for v in self.neighbors(p[1]) if v!=p[0]]
        elif isinstance(p, numbers.Number): # a vertex is given
            return [(p,v) for v in self.neighbors(p)]

    def neighbors(self, p):
        if p in self.neighbors_memoize: return self.neighbors_memoize[p]
        # Returns all the tuples in violation with p
        ns = self.vpe.enum_neighboring_vps(p)
        self.neighbors_memoize[p] = ns
        return ns

    def degree(self, p):
        # Returns the number of tuples in violation with p
        return len(self.neighbors(p))

    def number_of_nodes(self):
        # Returns the number of tuples in memory
        return self.n_nodes