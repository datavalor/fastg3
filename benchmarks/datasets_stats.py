import sys
sys.path.insert(1, 'utils/')
sys.path.insert(1, '../')
from dataset_utils import load_dataset, load_syn
import fastg3.crisp as g3crisp
import fastg3.ncrisp as g3ncrisp

if __name__ == '__main__':
    datasets_crisp = {
        'diamonds': load_dataset('diamonds'),
        'hydroturbine': load_dataset('hydroturbine'),
        'syn': load_syn()
    }

    datasets_ncrisp = {
        'diamonds': load_dataset('diamonds', ncrisp=True),
        'hydroturbine': load_dataset('hydroturbine', ncrisp=True)
    }

    for name in datasets_crisp:
        crisp_data = datasets_crisp[name]
        print(f"-------- {name}")
        print(f"-> CRISP")
        print(f"{len(crisp_data[0].index)} tuples")
        print(f'It default crisp FDs is {crisp_data[1]}->{crisp_data[2]}')
        print(f"g3={g3crisp.g3_hash(crisp_data[0], crisp_data[1], crisp_data[2])}")
        print(f"{len(crisp_data[0].groupby(crisp_data[1]))} equivalence classes")
        if name!='syn':
            ncrisp_data = datasets_ncrisp[name]
            print(f"-> NON-CRISP")
            print(f"{len(ncrisp_data[0].index)} tuples")
            VPE = g3ncrisp.create_vpe_instance(ncrisp_data[0], ncrisp_data[1], ncrisp_data[2]) 
            rg3 = g3ncrisp.RSolver(VPE, precompute=True)
            print(len(VPE.enum_vps()), "violating pairs.")
            print(f"g3={rg3.exact(method='wgyc')}")
