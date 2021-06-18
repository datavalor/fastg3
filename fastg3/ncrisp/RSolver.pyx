#distutils: language = c++
cimport cython

from .VPE cimport VPE
from subprocess import run, PIPE
from pathlib import Path
import tempfile
import time

from cython.operator cimport dereference, postincrement
from libcpp.pair cimport pair
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp cimport bool
from libc.stdlib cimport qsort

ctypedef pair[size_t, size_t] vp_type
ctypedef pair[size_t, size_t] size_t_pair
ctypedef cpp_vector[vp_type] vp_list
ctypedef cpp_vector[size_t] index_vector
ctypedef unordered_map[size_t, cpp_vector[size_t]] adjacency_map
ctypedef unordered_map[size_t, cpp_vector[size_t]].iterator adjacency_map_iterator

ctypedef pair[int, int] vp_type_int
ctypedef cpp_vector[vp_type_int] vp_list_int

cdef extern from "libs/LibMVC/numvc.hpp" namespace "libmvc":
    cdef cppclass NuMVC:
        NuMVC(vp_list_int edges, const int& num_vertices, int optimal_size, int cutoff_time_s, bool verbose) nogil except +
        void cover_LS() nogil except +
        int get_best_cover_size() nogil except +
        cpp_vector[int] get_cover() nogil except +

cdef int compare_size_t_pair(const void * a, const void * b) nogil:
    cdef:
        size_t_pair a_e = (<size_t_pair*> a)[0]
        size_t_pair b_e = (<size_t_pair*> b)[0]
    if a_e.second<b_e.second:
        return -1
    else:
        return 1

cdef class RSolver:
    cdef:
        VPE vpe
        vp_list vps
        adjacency_map vps_am
        index_vector tuples
        size_t n_tuples
        size_t max_id
        bool computed

    def __cinit__(self, VPE v, bool precompute=False):
        self.vpe = v
        self.tuples = self.vpe.list_all_ids()
        self.n_tuples = self.tuples.size()
        self.computed = False
        self.max_id = 0
        cdef size_t i
        for i in range(self.tuples.size()): 
            if self.tuples[i]>self.max_id:
                self.max_id=self.tuples[i]

        if precompute:
            self.vp_enum()
            for i in range(self.vps.size()):
                self.vps_am[self.vps[i].first].push_back(self.vps[i].second)
                self.vps_am[self.vps[i].second].push_back(self.vps[i].first)


    cpdef vp_list vp_enum(self):
        if not self.computed:
            self.vps=self.vpe.enum_vps()
            self.computed=True

    def get_vps(self):
        return self.vps

    def exact(self, method="wgyc", timeout=10, return_cover=False):
        """
        Provides the exact value of g3/mvc.
        """
        cover = []
        if method=="wgyc":
            cover = self.wgyc(time_s=timeout)
        
        if return_cover: return cover
        else: return len(cover)/self.n_tuples

    def upper_bound(self, method="gic", numvc_time=2, return_cover=False):
        """
        Provides an upper bound on g3/mvc.
        """
        cover = []
        if method=="gic":
            cover = self.gic()
        elif method=="2approx":
            cover = self.mvc_2_approx()
        elif method=="numvc":
            cover = self.numvc(time_s=numvc_time)

        if return_cover: return cover
        else: return len(cover)/self.n_tuples

    def lower_bound(self, method="maxmatch", numvc_time=2, return_cover=False):
        """
        Provides a lower bound on g3/mvc.
        """
        size = []
        if method=="maxmatch":
            size = self.maximal_matching()
        elif method=="mvmatch":
            size = self.mv_matching()
        return size/self.n_tuples

    cdef cpp_vector[size_t] mvc_2_approx(self):
        """
        Classical greedy mvc algorithm.
        Finds a 2-approximate minimum vertex cover.
        """
        cdef: 
            unordered_map[size_t, long] cost
            unordered_map[size_t, long].iterator cost_it
            long min_cost
            size_t i
            size_t u
            size_t v
            cpp_vector[size_t] cover
        with nogil:
            for i in range(self.tuples.size()):
                cost[self.tuples[i]]=1
            for i in range(self.vps.size()):
                u = self.vps[i].first
                v = self.vps[i].second
                min_cost = min(cost[u], cost[v])
                cost[u] -= min_cost
                cost[v] -= min_cost
            cost_it = cost.begin()
            while(cost_it!=cost.end()):
                if dereference(cost_it).second==0: 
                    cover.push_back(dereference(cost_it).first)
                postincrement(cost_it)
        return cover

    cdef cpp_vector[size_t] gic(self):
        """
        Greedy independent cover.
        Finds a approximate minimum vertex cover.
        """
        cdef:
            unordered_map[size_t, int] removed_vertices
            adjacency_map_iterator am_it = self.vps_am.begin()
            cpp_vector[size_t_pair] ordered_vertices
            cpp_vector[size_t] cover
            size_t i
            size_t j
            size_t neighbor
        with nogil:
            while(am_it!=self.vps_am.end()):
                ordered_vertices.push_back(size_t_pair(dereference(am_it).first, dereference(am_it).second.size()))
                postincrement(am_it)
            qsort(&ordered_vertices[0], ordered_vertices.size(), sizeof(ordered_vertices[0]), compare_size_t_pair)
            for i in range(ordered_vertices.size()):
                if removed_vertices.find(ordered_vertices[i].first)==removed_vertices.end():
                    removed_vertices[ordered_vertices[i].first]=0
                    for j in range(self.vps_am[ordered_vertices[i].first].size()):
                        neighbor=self.vps_am[ordered_vertices[i].first][j]
                        if removed_vertices.find(neighbor)==removed_vertices.end():
                            cover.push_back(neighbor)
                        removed_vertices[neighbor]=0
        return cover

    cdef int maximal_matching(self):
        """
        Finds a maximal matching (lower bound on minimum vertex cover)
        """
        cdef: 
            size_t i
            size_t u
            size_t v
            unordered_map[size_t, int] nodes
            cpp_vector[vp_type] matching
        with nogil:
            for i in range(self.vps.size()):
                u = self.vps[i].first
                v = self.vps[i].second
                if nodes.find(u)==nodes.end() and nodes.find(v)==nodes.end() and u!=v:
                    matching.push_back(vp_type(u, v))
                    nodes[u]=0
                    nodes[v]=0
        return <int>matching.size()

    cdef cpp_vector[int] numvc(self, int time_s):
        """
        Numvc: Heuristic algorithm for solving the MVC.
        """
        cdef:
            vp_list_int numvc_edges
            size_t i
            NuMVC * solver
        with nogil:
            for i in range(self.vps.size()):
                numvc_edges.push_back(<vp_type_int> self.vps[i])
            solver = new NuMVC(numvc_edges, self.max_id+1, 0, time_s, False);
            solver.cover_LS()
        # mvc_size = get_best_cover_size()
        return solver.get_cover()

    cdef cpp_vector[size_t] wgyc(self, int time_s=10):
        """
        WeGotYouCovered: Exact algorithm for solving the MVC.
        """
        cdef size_t i
        input_string = "<<EOF-MARKER\n"
        input_string += f"p td {self.max_id+2} {self.vps.size()}\n"
        input_string += "\n".join([f"{str(self.vps[i].first+1)} {str(self.vps[i].second+1)}" for i in range(self.vps.size())])
        input_string += "EOF-MARKER"

        solver_path = Path(__file__).parent / "./libs/wgyc"
        output = run([solver_path, f'--time_limit={str(time_s)}'],
            capture_output=True, text=True, check=True,
            input=input_string, encoding='ascii')
        r = output.stdout
        try:
            # mvc_size = int(r.split('\n')[0].split(' ')[3])
            cover = [int(v) for v in r.split('\n')[1:-1]]
        except ValueError:
            print("Error while computing exact value with WeGotYouCovered.")
            raise
        return cover

    cdef int mv_matching(self):
        """
        Micali and Vazirani maximum matching
        """
        cdef size_t i
        r=""
        with tempfile.NamedTemporaryFile() as tf:
            header = f"{self.max_id+1}\n"
            edges = "\n".join([f"{str(self.vps[i].first)} {str(self.vps[i].second)}" for i in range(self.vps.size())])
            tf.write(header.encode())
            tf.write(edges.encode())
            solver_path = Path(__file__).parent / "./libs/mvmatching"
            output = run([solver_path, tf.name],
                timeout=30,
                capture_output=True, 
                text=True, 
                check=True)
            r = output.stdout
        return int(r.split("\n")[1])