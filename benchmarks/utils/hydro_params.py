HYDRO_XPARAMS = {
    'flow':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    },
    'opening':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.03
    },
    # 'position':{
    #     'type': 'numerical',
    #     'predicate': 'metric',
    #     'metric': 'absolute',
    #     'thresold': 0.05
    # },
    # 'grid_pressure_drop':{
    #     'type': 'numerical',
    #     'predicate': 'metric',
    #     'metric': 'absolute',
    #     'thresold': 0.05
    # },
    'elevation':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.03
    }
}

HYDRO_YPARAMS = {
    'power':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    }
}