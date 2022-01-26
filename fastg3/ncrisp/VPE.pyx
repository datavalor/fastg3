#distutils: language = c++
cimport cython
from cython import parallel

import logging
logger = logging.getLogger('fastg3_vpe')

import numpy as np
cimport numpy as np

from cython.operator cimport dereference, postincrement
from libcpp.string cimport string
from libcpp.pair cimport pair
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector as cpp_vector
from libcpp cimport bool

cdef class VPE:
    def __cinit__(self, verbose=False):
        self.join_attr=b""
        self.verbose = verbose
        if verbose: logger.setLevel(level=logging.DEBUG)
        else: logger.setLevel(level=logging.WARNING)

    def _make_groups(self, df, blocking_attrs):
        # Returns a uint numpy 2D array, first axis corresponds to the blocks and second to the indexes contained block delimited by the last value being repeated.
        pandas_groups = df.reset_index(drop=True).groupby(blocking_attrs, sort=True)
        cdef:
            dict dfgroups = dict(pandas_groups.groups)
            dict blocks_dict = dict()
            block_type block
            blocks_type blocks
            size_t nid
        for i, gname in enumerate(dfgroups): 
            block = block_type()
            for nid in dfgroups[gname]: block.push_back(nid)
            blocks.push_back(block)
            blocks_dict[gname] = i
        return blocks, blocks_dict, pandas_groups.ngroup()

    def check_feasability(self):
        if len(self.selected_xattrs)==0 or len(self.selected_yattrs)==0:
            logger.error(f'{len(self.selected_xattrs)} left attributes and {len(self.selected_yattrs)} right attributes remaining. VPE can\'t be done.')
            return False
        else:
            return True

    def prepare_enumeration(self, df, dict x_attrs, dict y_attrs, blocking_attrs=[], str pjoin_type="brute_force", join_attr=None):
        # Handle join type and perform preprocessing when needed
        if pjoin_type=="ordered":
            if join_attr is None:
                raise Exception("If ordered join is requested, [join_attr] must be specified.")
            df = df.sort_values(join_attr, ascending=True)
            self.join_type=1
            self.join_attr = str.encode(join_attr)
        else:
            self.join_type=0 #default: brute force
        
        # Creates a Dataframe object accessible from C++ for accessing the data
        global_params = {**x_attrs, **y_attrs}
        self.dfc = _create_dataframe(df, global_params)
        available_attributes = list(dereference(self.dfc).get_columns())
        if pjoin_type=="ordered":
            try:
                available_attributes.index(self.join_attr)
            except ValueError:
                logger.info("The requested join attribute hasn't been added to the dataframe. Going back to brute force.")
                self.join_type=0
        available_attributes = sorted(available_attributes, key=lambda x: global_params[x.decode()].get('position', len(df.columns)))
        for attr in available_attributes:
            if attr.decode() in list(x_attrs.keys()): self.selected_xattrs.push_back(attr)
            if attr.decode() in list(y_attrs.keys()): self.selected_yattrs.push_back(attr)
        if not self.check_feasability(): return False

        # Creates the blocks for blocking
        cdef:
            size_t n_rows = df.shape[0]
            size_t i
            long[:] row_group_col
            cpp_vector[long] row_group_col_vec
        if blocking_attrs:
            self.blocks, self.blocks_dict, blocks_index = self._make_groups(df, blocking_attrs)
            for attr in blocking_attrs: self.blocking_attrs.push_back(str.encode(attr))
            row_group_col = np.array(blocks_index, dtype=np.int64)
            for i in range(n_rows): row_group_col_vec.push_back(row_group_col[i])
        else:
            self.blocks = np.ascontiguousarray([df.reset_index(drop=True).index.to_numpy()], dtype=np.uint)
            for i in range(n_rows): row_group_col_vec.push_back(0)
        dereference(self.dfc).set_block_index(row_group_col_vec)

        self.describe()
        return True

    cpdef vp_list enum_vps(self):
        cdef size_t n_rows = self.number_of_rows()
        if n_rows<=1 or not self.check_feasability(): return []
        cdef:
            vp_list vps
            vp_list vps_tmp
            size_t n_blocks = self.blocks.size()
            size_t i
        with nogil:
            if n_blocks==1:
                vps = self.join_proxy(self.blocks[0], self.selected_xattrs, self.selected_yattrs, self.join_type)
            elif n_blocks>1:
                with parallel.parallel(num_threads=1):
                    for i in parallel.prange(n_blocks):
                        vps_tmp=self.join_proxy(self.blocks[i], self.selected_xattrs, self.selected_yattrs, self.join_type)
                        vps.insert(vps.end(), vps_tmp.begin(), vps_tmp.end())
        return vps

    cdef index_vector enum_neighboring_vps(self, size_t df_id) nogil:
        # if not self.check_feasability(): return
        cdef:
            size_t row_id = self.dfc.get_mem_from_user_index(df_id)
            size_t block_id = self.dfc.get_block_index(row_id)
            cpp_vector[size_t] ns
        # logger.info(f'Join row {df_id} ({row_id} in memory) from block {block_id}.')
        ns=self.row_join_proxy(self.blocks[block_id], row_id, self.selected_xattrs, self.selected_yattrs, self.join_type)
        return ns

    cpdef size_t number_of_rows(self):
        return dereference(self.dfc).get_n_rows()

    cdef index_vector list_all_ids(self) nogil:
        return dereference(self.dfc).get_user_index()

    def describe(self):
        x_descr, y_descr = [], []
        for attr in list(self.selected_xattrs):
            if self.join_attr!=b'' and attr.decode()==self.join_attr.decode(): x_descr.append(f"{attr} [join]")
            else: x_descr.append(f"{attr}")
        for attr in list(self.selected_yattrs): y_descr.append(f"{attr}")
        logger.info(f"*FINAL OPERATION* ({self.number_of_rows()} rows) X: Blocking({list(self.blocking_attrs)}), [{', '.join(x_descr)}] -> Y: [{', '.join(y_descr)}]")

    cdef vp_list join_proxy(self, block_type block, attr_list x_attrs, attr_list y_attrs, int join_type) nogil except +:
        if join_type==0: return dereference(self.dfc).bf_join(block, x_attrs, y_attrs)
        elif join_type==1: return dereference(self.dfc).ordered_join(block, x_attrs, y_attrs)

    cdef index_vector row_join_proxy(self, block_type block, size_t row_id,  attr_list x_attrs, attr_list y_attrs, int join_type) nogil except +:
        if join_type==0: return dereference(self.dfc).bf_row_join(block, row_id, x_attrs, y_attrs)
        elif join_type==1: return dereference(self.dfc).ordered_row_join(block, row_id, x_attrs, y_attrs)

cdef Dataframe * _create_dataframe(df, dict attrs):
    # pandas uses four dtypes in pratice int64, float64, bool, object
    cdef size_t n_rows = df.shape[0]
    logger.info(f'{n_rows} usable rows detected!')
    cdef size_t[:] index = np.ascontiguousarray(df.index, dtype=np.uint)
    df = df.reset_index(drop=True)

    cdef: 
        long[:] long_arr
        double[:] double_arr
        str[:] str_arr
        cpp_vector[string] strb_arr
        Dataframe * dfc = new Dataframe(&index[0], n_rows) 

        string enc_col
        string metric
        cpp_vector[double] params
        size_t i
    for col in attrs:
        if col not in df.columns:
            logger.error(f'Provided column [{col}] not in dataframe! Column ignored.')
        else:
            dt = df[col].dtype
            enc_col = str.encode(col)
            predicate = str.encode(attrs[col]['predicate'])
            params = attrs[col]["params"]
            logger.debug(f'Handling column [{col}] of type [{dt}].')    
            if dt=='int64':
                long_arr = np.ascontiguousarray(df[col])
                dereference(dfc).add_column[long](enc_col, &long_arr[0], predicate, params)
            elif dt=='float64':
                double_arr = np.ascontiguousarray(df[col])
                print(enc_col)
                dereference(dfc).add_column[double](enc_col, &double_arr[0], predicate, params)
            elif dt=='object':
                str_arr=df[col].to_numpy()
                for i in range(n_rows): strb_arr.push_back(str.encode(str_arr[i]))
                dereference(dfc).add_str_column(enc_col, strb_arr, predicate, params)
                strb_arr.clear()
            else:
                logger.error(f'Numpy dtype [{dt}] of column [{col}] not supported... yet! Column ignored.')
    return dfc