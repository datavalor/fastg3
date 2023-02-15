HYDRO_XPARAMS = {
    'flow':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    },
    'opening':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.03]
    },
    # 'position':{
    #     'type': 'numerical',
    #     'predicate': 'absolute_distance',
    #     'params': [0.05]
    # },
    # 'grid_pressure_drop':{
    #     'type': 'numerical',
    #     'predicate': 'absolute_distance',
    #     'params': [0.05]
    # },
    'elevation':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.03]
    }
}

HYDRO_YPARAMS = {
    'power':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    }
}