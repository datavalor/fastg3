from pydataset import data
import time
import line_profiler

import networkx as nx
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '../')
import fastg3.ncrisp as g3ncrisp

n=20000
n_sampled=20000
df = data("diamonds").sample(n=n, replace=True, random_state=27).reset_index(drop=True)
# print(df.head())

xparams = {
    'carat':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    },
    'cut':{
        'type': 'categorical',
        'predicate': 'equality'
    },
    'color':{
        'type': 'categorical',
        'predicate': 'equality'
    },
    'clarity':{
        'type': 'categorical',
        'predicate': 'equality'
    }
}

yparams = {
    'price':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 10
    }
}

if __name__ == '__main__':
    VPE = g3ncrisp.create_vpe_instance(
    df, 
    xparams, 
    yparams, 
    blocking=True,
    # join_type="brute_force",
    join_type="auto",
    opti_ordering=False,
    verbose=False)

    # print(len(VPE.enum_vps()), "violating pairs.")

    # Exact
    start=time.time()
    rg3 = g3ncrisp.RSolver(VPE, precompute=True)
    gic = rg3.upper_bound(method="gic", return_cover=True)
    print(f'Greedy independent Cover upper bound computed in {1000*(time.time()-start)}ms')
    print("GIC g3 is", len(gic)/len(df.index))


    sub_GIC = g3ncrisp.SubGIC(g3ncrisp.VPEGraph(VPE))
    start=time.time()
    sub_gic_cover = sub_GIC.estimate_mvc_size(n_sampled)
    print(f"GIC sublinear in {1000*(time.time()-start)}ms")
    # print("Sublinear GIC g3 is", len(sub_gic_cover)/len(df.index))
    print("Sublinear GIC g3 is", sub_gic_cover)
    # print(f"Estimation: {estimated_size}")

    # nodes_color = []
    # for n in list(df.index):
    #     if n in gic:
    #         nodes_color.append('r')
    #     else:
    #         nodes_color.append('k')
    # G = nx.Graph()
    # G.add_nodes_from(list(df.index))
    # G.add_edges_from(VPE.enum_vps())
    # pos = nx.spring_layout(G, k=0.30, iterations=20, seed=27)
    # nx.draw(G, 
    #     nodelist=list(df.index),
    #     node_size=5, 
    #     with_labels=True, 
    #     node_color=nodes_color,
    #     pos=pos, 
    #     font_size=9, 
    #     width=0.1)
    # plt.gcf().set_dpi(500)
    # plt.savefig("./test.png")

    # nodes_color = []
    # for n in list(df.index):
    #     if n in sub_gic_cover:
    #         nodes_color.append('r')
    #     else:
    #         nodes_color.append('k')
    # G = nx.Graph()
    # G.add_nodes_from(list(df.index))
    # G.add_edges_from(VPE.enum_vps())
    # pos = nx.spring_layout(G, k=0.30, iterations=20, seed=27)
    # nx.draw(G, 
    #     nodelist=list(df.index),
    #     node_size=5, 
    #     with_labels=True, 
    #     node_color=nodes_color,
    #     pos=pos, 
    #     font_size=9, 
    #     width=0.1)
    # plt.gcf().set_dpi(500)
    # plt.savefig("./test2.png")


    # print("GIC cover", gic)
    print("-> Exact computation")
    start=time.time()
    wgyc = rg3.exact(method="wgyc")
    print(f'WeGotYouCovered value computed in {time.time()-start}s')
    print("Exact g3 is", wgyc)

    # print(VPE.enum_vps())


    print("-> Sublinear computation")
    sub_solverY = g3ncrisp.Yoshida2009(g3ncrisp.VPEGraph(VPE))
    start=time.time()
    estimated_size = sub_solverY.estimate_mvc_size(n_sampled)
    print(f"Yoshida sublinear in {1000*(time.time()-start)}ms")
    print(f"Estimation: {estimated_size}")
    sub_solverO = g3ncrisp.Onak2011(g3ncrisp.VPEGraph(VPE))
    start=time.time()
    estimated_size = sub_solverO.estimate_mvc_size(n_sampled)
    print(f"Onak sublinear in {1000*(time.time()-start)}ms")
    print(f"Estimation: {estimated_size}")





    
