#%%
import numpy as np
import pandas as pd

import sys
sys.path.insert(1, '../../')
sys.path.insert(1, '../')
import fastg3.crisp as g3crisp

def generate_group_sizes(n_groups, total):
    sizes = np.random.randint(2,total/n_groups,n_groups)
    sizes = np.round((total*sizes/sizes.sum())).astype(int)
    delta = total-sizes.sum()
    sizes[np.argmax(sizes)]+=delta
    return sizes

def generate_group_consequent(target_g3, group_size, n_consequents, percent_classes_per_group):
    p_max_consequent = round(1-target_g3,2)
    # minimum number of unique consequents to achieve g3
    min_nconsequents = np.ceil((1-p_max_consequent)/p_max_consequent).astype(int)+1
    possible_n_consequents = list(range(min_nconsequents, group_size-int(p_max_consequent*group_size)))
    assert min_nconsequents<group_size, "g3 not achievable"
    if len(possible_n_consequents)>0:
        n_different_consequents = possible_n_consequents[int(percent_classes_per_group*(len(possible_n_consequents)-1))]
        p_non_max_consequent = (1-p_max_consequent)/(n_different_consequents-1)
    else:
        n_different_consequents = 1
        p_non_max_consequent=0
    tab_p_non_max_consequent = np.ones(n_different_consequents-1)*p_non_max_consequent
    probs = np.append(tab_p_non_max_consequent, p_max_consequent)
    available_consequents = np.random.random((n_different_consequents, n_consequents))

    repeats=(probs*group_size).astype(int)
    group_size=repeats.sum()
    group_consequent = available_consequents[np.repeat(list(range(n_different_consequents)), repeats)]
    return group_size, group_consequent


def generate_syn(
    target_g3 = 0.6,
    n_antecedents = 2,
    n_consequents = 2,
    n_tuples=50000,
    n_groups=2,
    percent_classes_per_group=0.3,
    verbose=False
):
    assert target_g3<1
    target_g3 = round(target_g3,2)
    # group_mean_size = int(n_tuples/n_groups)
    group_sizes=generate_group_sizes(n_groups, n_tuples)
    
    # if verbose: print(f"{n_tuples} tuple, {n_groups} groups of size {group_size}. g3 is aimed at {target_g3}.")

    actual_group_size, group_consequent = generate_group_consequent(target_g3, int(n_tuples/n_groups), n_consequents, percent_classes_per_group)
    final_array = None
    for group_size in group_sizes:
        # actual_group_size, group_consequent = generate_group_consequent(target_g3, group_size, n_consequents, percent_classes_per_group)
        group_antecedent = np.tile(np.random.random(n_antecedents), (actual_group_size,1))
        final_group = np.hstack((group_antecedent, group_consequent))
        # Stacking !
        if final_array is None:
            final_array=final_group
        else:
            final_array = np.vstack((final_array, final_group))
    antecedent_names = ['X'+str(i) for i in range(n_antecedents)]
    consequent_names = ['Y'+str(i) for i in range(n_consequents)]
    df = pd.DataFrame(final_array, columns=antecedent_names+consequent_names)
    return df, antecedent_names, consequent_names

if __name__ == '__main__':
    df, antecedent_names, consequent_names =  generate_syn(
        target_g3 = 0.5,
        n_tuples=1000000,
        n_groups=2,
        percent_classes_per_group=0,
        n_antecedents = 2,
        n_consequents = 1,
    )
    # df=df.sample(frac=1)
    verbose=False
    print(df.groupby(antecedent_names).size())
    print("exact:", g3crisp.g3_hash(df, antecedent_names, consequent_names))
    print("urs: ", g3crisp.g3_urs(df, antecedent_names, consequent_names, error=0.05, verbose=verbose))
    print("srs:", g3crisp.g3_srs(df, antecedent_names, consequent_names, verbose=verbose))
    print("srsi:", g3crisp.g3_srsi(df, antecedent_names, consequent_names, verbose=verbose))
    print(len(df.groupby(antecedent_names)))
# %%
