import tempfile
from subprocess import run, PIPE
from os import path

class MVC:
    def __init__(self, vpe, verbose=False):
        self.vpe = vpe
        self.tuples = self.vpe.list_all_ids()
        self.n_tuples = len(self.tuples)
        self.max_id = max(self.tuples)
        self.vps = None

    def vp_enum(self):
        if self.vps is None: self.vps=self.vpe.enum_vps()
        return self.vps

    def mvc_2_approx(self):
        cost = dict(zip(self.tuples, [1]*len(self.tuples)))
        for u, v in self.vp_enum():
            min_cost = min(cost[u], cost[v])
            cost[u] -= min_cost
            cost[v] -= min_cost
        cover = {u for u, c in cost.items() if c == 0}
        return len(cover)/self.n_tuples, cover

    def maximal_matching(self):
        matching = set()
        nodes = set()
        for u, v in self.vp_enum():
            if u not in nodes and v not in nodes and u != v:
                matching.add((u, v))
                nodes.add(u)
                nodes.add(v)
        return len(matching)/self.n_tuples, matching

    def to_dimacs(self):
        return [f'p edge {self.max_id+1} {len(self.vp_enum())}'] + [f'e {u+1} {v+1}' for u, v in self.vpe.enum_vps()]

    def numvc(self, time=2):
        numvc_path = path.join(path.dirname(__file__), 'libs/', 'numvc')
        print(numvc_path)
        tmpf = tempfile.NamedTemporaryFile()
        with open(tmpf.name, "w") as f:
            f.write('\n'.join(self.to_dimacs()))
        p = run([numvc_path, tmpf.name, '0', str(time)], stdout=PIPE)
        tmpf.close()
        r = str(p.stdout)
        keyword = 'independent set:\\n'
        start = r.find(keyword)+len(keyword)
        end = r.index(" \\n", start)
        iset = [int(i)-1 for i in r[start:end].split(" ")]
        mvc = [node for node in list(self.tuples) if node not in iset]
        return len(mvc)/self.n_tuples, mvc