# %%
# kernprof -l sublinearMVC.py
# python3 -m line_profiler sublinearMVC.py.lprof 

import numpy as np
import math
from random import sample
import random
import networkx as nx

# %%
class OnakSubMVC:
    def __init__(self, G, verbose=False):
        self.G = G
        self.d = max([d for n, d in G.degree()]) # Max degree of graph
        #self.d = G.number_of_nodes() # It seems to work by using the number of nodes instead which is far easier to get
        self.dstar = np.log(self.d)
        self.verbose = verbose

        if self.verbose: print('Init advanced SMVC')

        self.reset()
        
    def reset(self):
        self.matching_oracle_cache = {}
        self.neighbors = {}

        self.MOtab = []

    def format_edge(self, e):
        return tuple(sorted(e))

    def get_n(self, v):
        if v not in self.neighbors:
            self.neighbors[v] = {
                'lb': 0,
                'next_lb': 2**-self.dstar,
                'assigned_number': {},
                'sorted_list': []
            }
        return self.neighbors[v]

    # @profile
    def get_k_lowest_neighbors(self, v, k):
        while len(self.get_n(v)['sorted_list'])<k+1 and self.get_n(v)['lb']<1:
            lb, next_lb = self.get_n(v)['lb'], self.get_n(v)['next_lb']

            S=[(self.get_n(v)['assigned_number'][vp],vp) for vp in self.get_n(v)['assigned_number'].keys() if (lb<=self.get_n(v)['assigned_number'][vp]<next_lb)]
            
            p=(next_lb-lb)/(1-lb)
            T=[d for d in range(self.G.degree(v)) if random.random()<=p]

            for t in T:
                w=list(self.G.neighbors(v))[t]
                r=random.uniform(lb, next_lb)

                if self.get_n(w)['lb']<=lb:
                    tmp = [i for i, s in enumerate(S) if (w==s[1] and r<s[0])]
                    if tmp:
                        self.get_n(v)['assigned_number'][w]=r
                        self.get_n(w)['assigned_number'][v]=r
                        S[tmp[0]]=(r,w)

                    if w not in self.get_n(v)['assigned_number']:
                        self.get_n(v)['assigned_number'][w]=r
                        self.get_n(w)['assigned_number'][v]=r
                        S+=[(r,w)]

            self.get_n(v)['sorted_list'] += sorted(S)
            self.get_n(v)['lb'] = next_lb
            self.get_n(v)['next_lb'] = 2*next_lb

        if len(self.get_n(v)['sorted_list'])<k+1: return (math.inf, v)
        else: return self.get_n(v)['sorted_list'][k]

    def estimate_mvc_size(self, n):
        assert n<=self.G.number_of_nodes(), f'Error: Sample size must be lower than the number of nodes in graph ({self.G.number_of_nodes()})'
        
        self.reset()
        v_sample = sample(list(self.G.nodes), k=n)
        result = []
        for v in v_sample:
            self.MOvisits = 0
            result.append(self.vertex_oracle(v))
            self.MOtab.append(self.MOvisits)
        return np.mean(result)

    def vertex_oracle(self, v):
        if self.verbose: print(f'Call to vertex oracle for {v}')

        k=0
        r, w = self.get_k_lowest_neighbors(v, k)
        while r!=math.inf:
            if self.matching_oracle((v,w)):
                return True
            k+=1
            r, w = self.get_k_lowest_neighbors(v, k)
        return False 

    #@profile
    def matching_oracle(self, e):
        e = self.format_edge(e)
        if self.verbose: print(f'Call to matching oracle for {e}')

        if e in self.matching_oracle_cache: return self.matching_oracle_cache[self.format_edge(e)]
        self.MOvisits += 1

        u, v = e
        k1, k2 = 0, 0
        r1, w1 = self.get_k_lowest_neighbors(u, k1)
        r2, w2 = self.get_k_lowest_neighbors(v, k2)

        while w1!=v or w2!=u:
            if r1<r2:
                if self.matching_oracle((u,w1)): 
                    self.matching_oracle_cache[e] = False
                    return False
                k1+=1
                r1, w1 = self.get_k_lowest_neighbors(u, k1)
            else:
                if self.matching_oracle((v,w2)): 
                    self.matching_oracle_cache[e] = False
                    return False
                k2+=1
                r2, w2 = self.get_k_lowest_neighbors(v, k2)

        self.matching_oracle_cache[e] = True
        return True

# %%
if __name__ == "__main__":
    G = nx.random_regular_graph(20, 30000)
    osmvc = OnakSubMVC(G)
    osmvc.estimate_mvc_size(5000)


# %%
