# kernprof -l simpleSublinearMVC.py
# python3 -m line_profiler simpleSublinearMVC.py.lprof 

import numpy as np
from random import sample
import random
import time
import logging
import networkx as nx

logger = logging.getLogger('yoshida_mvc')

class YoshidaSubMVC:
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        
        logger.info('Init Yoshida 2009 SMVC')
        
        self.reset()
        
    def reset(self):
        self.ranking = {}
        self.matching_oracle_cache = {}

        self.MOvisits = 0
        self.MOtab = []

    def format_edge(self, e):
        return tuple(sorted(e))

    def get_edge_ranking(self, e):
        #se = self.format_edge(e)
        if e not in self.ranking:
            self.ranking[e]=random.random()
        return self.ranking[e] 

    def estimate_mvc_size(self, n):
        try:
            assert n<=self.G.number_of_nodes()
        except AssertionError: 
            logger.error(f"Error: Sample size must be lower than the number of nodes in graph ({self.G.number_of_nodes()})")
            raise

        self.reset()
        # random.seed(27)
        v_sample = sample(self.G.nodes(), k=n)
        result = []
        for v in v_sample:
            # print(v)
            self.MOvisits = 0
            result.append(self.vertex_oracle(v))
            self.MOtab.append(self.MOvisits)
        return np.mean(result)

    def vertex_oracle(self, v):
        # Get the edges incident to v sorted by ascending ranking
        nedges_zip = [(self.get_edge_ranking(self.format_edge(ne)), ne) for ne in self.G.edges(v)]
        sorted_nedges = [b for _, b in sorted(nedges_zip)]

        # Make a decision
        for e in sorted_nedges:
            if self.matching_oracle(e): return True
        return False

    # @profile
    def matching_oracle(self, e):
        e = self.format_edge(e)

        if e in self.matching_oracle_cache: return self.matching_oracle_cache[e]
        self.MOvisits += 1
        rank = self.get_edge_ranking(e)

        # Get the edges that share an endpoint with e sorted by ascending ranking
        sorted_nedges = sorted([(self.get_edge_ranking(self.format_edge(ne)), ne) for ne in self.G.edges(e)])

        # Make a recursive decision
        i=0
        while i<len(sorted_nedges) and sorted_nedges[i][0] < rank:
            if self.matching_oracle(sorted_nedges[i][1]): 
                self.matching_oracle_cache[e] = False
                return False
            i+=1
        
        for _, ne in sorted_nedges[i:]: self.matching_oracle_cache[self.format_edge(ne)] = False
        self.matching_oracle_cache[e] = True
        return True

if __name__ == "__main__":
    start=time.time()
    G = nx.random_regular_graph(20, 30000)
    ysmvc = YoshidaSubMVC(G)
    size=ysmvc.estimate_mvc_size(5000)
    print(f'{size} estimated in {time.time()-start} seconds.')