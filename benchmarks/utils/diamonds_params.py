DIAMONDS_XPARAMS = {
    'carat':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    },
    'x':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    },
    'y':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    },
    'z':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    },
    'depth':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
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

DIAMONDS_YPARAMS = {
    'price':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [10]
    }
}