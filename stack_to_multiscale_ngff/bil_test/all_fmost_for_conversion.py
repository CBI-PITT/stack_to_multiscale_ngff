# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 16:20:11 2021
@author: alpha
"""

'''
Dataset dict should be structured as:
    key = dataset_ID
    dict = {
        url: list of STR in decending resolution order
        scale: tuple (z,y,x) of the highest resolution level
        contrast_limits: list of int signifying low and high for 16 bit [0, 65535]
        }
'''

datasets = {

    'mouseID_404421-182720': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH1',  # full res
            2: 'https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_404421-182720/CH2',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    'mouseID_405429-182725': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_405429-182725/CH2',  # full res
            2: 'https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_405429-182725/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_418245-182727': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_418245-182727/CH1',  # full res
            2: 'https://download.brainimagelibrary.org/2b/da/2bdaf9e66a246844/mouseID_418245-182727/CH2',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_380471-191813': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_380471-191813/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_380471-191813/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_362188-191815': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_362188-191815/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_362188-191815/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_380470-191812': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_380470-191812/CH1',  # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_380470-191812/CH2',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_426124-191808': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_426124-191808/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_426124-191808/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_439168-191807': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_439168-191807/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_439168-191807/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_443055-191805': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_443055-191805/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_443055-191805/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_383680-18463': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_383680-18463/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_383680-18463/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_383128-18465': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_383128-18465/red/montage',
            # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_383128-18465/green/montage',
            # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),

    },

    'mouseID_431038-191804': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_431038-191804/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_431038-191804/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_381488-18464': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_381488-18464/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_381488-18464/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),

    },

    'mouseID_423019-191803': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_423019-191803/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_423019-191803/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_373187-191817': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_373187-191817/CH1',  # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_373187-191817/CH2',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_377387-18466': {  # checked, works
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_377387-18466/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_377387-18466/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),

    },

    'mouseID_325875-17543': {  # checked, works
        'channel': {
            # 'extra':'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_325875-17543/CH1',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_325875-17543/green/montage',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_325875-17543/red/montage',
            # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_405426-182724': {  # checked, works
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_405426-182724/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_405426-182724/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_420489-191801': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_420489-191801/CH1',  # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_420489-191801/CH2',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },

    'mouseID_417571-182722': {  # checked, works
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_417571-182722/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_417571-182722/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),

    },

    'mouseID_417570-182721': {  # checked, works
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_417570-182721/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_417570-182721/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),

    },
    'mouseID_445241-211779': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_445241-211779/CH1'  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_445241-211779/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_445243-211780': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_445243-211780/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_445243-211780/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),

    },

    'mouseID_467362-211782': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_467362-211782/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_467362-211782/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_486478-196478': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_486478-196478/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_486478-196478/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_494230-211775': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_494230-211775/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_494230-211775/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_497458-211786': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_497458-211786/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_497458-211786/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_497462-211787': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_497462-211787/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_497462-211787/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_497520-211776': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_497520-211776/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_497520-211776/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_500861-211788': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_500861-211788/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_500861-211788/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_510498-211777': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_510498-211777/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_510498-211777/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_510502-211778': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_510502-211778/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_510502-211778/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_522151-211806': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_522151-211806/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_522151-211806/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_522152-211807': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_522152-211807/CH1',
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_522152-211807/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_586838-211801': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_586838-211801/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_586838-211801/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_586840-211802': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_586840-211802/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_586840-211802/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_588922-211800': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_588922-211800/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_588922-211800/CH2_10_10_10um'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_588923-211799': {  # checked, works
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_588923-211799/CH1',  # full res
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.35, 0.35),
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ec/6a/ec6aac7d4d37b073/mouseID_588923-211799/CH2_10_10_10um/'
        },
        'alt_label': {
            1: None
        },
        'alt_scale': (10, 10, 10),
    },

    #####################################################################################################################
    #################################################################################################################

    'mouseID_210254-15257': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_210254-15257/Green/Origin',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_210254-15257/Red/Origin'
            # full res
        },
        'scale': (1, 0.23, 0.23),
        ## Scale is not recorded for this dataset, but this scale is used for other datasets in this series
    },

    'mouseID_360835-18049': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_360835-18049/Green/montage',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_360835-18049/Red/montage',
            # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    'mouseID_362191-191816': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_362191-191816/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_362191-191816/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_367667-18052': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_367667-18052/Green/montage',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_367667-18052/Red/montage',
            # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    'mouseID_373641-18462': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_373641-18462/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_373641-18462/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_374706-18461': {
        'channel': {
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_374706-18461/CH2',  # full res
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_374706-18461/CH1',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_374707-18452': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_374707-18452/Green/montage',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_374707-18452/Red/montage'
            # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    'mouseID_375394-18468': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_375394-18468/Green/montage',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_375394-18468/Red/montage',
            # full res
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': (1, 0.23, 0.23),
        ## Scale is not recorded for this dataset, but this scale is used for other datasets in this series
    },

    'mouseID_378667-18469': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_378667-18469/Green/montage',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_378667-18469/Red/montage',
            # full res
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': (1, 0.23, 0.23),
        ## Scale is not recorded for this dataset, but this scale is used for other datasets in this series
    },

    'mouseID_378668-18470': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_378668-18470/Green/montage',
            # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_378668-18470/Red/montage',
            # full res
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': (1, 0.23, 0.23),
        ## Scale is not recorded for this dataset, but this scale is used for other datasets in this series
    },

    'mouseID_381487-18458': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_381487-18458/green',  # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_381487-18458/red',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    'mouseID_394528-18867': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_394528-18867/green'  # full res
        },
        'label': {
            1: 'GFP'
        },
        'scale': (1, 0.23, 0.23),
    },

    'mouseID_411732-182718': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_411732-182718/CH1',  # full res
            2: 'https://download.brainimagelibrary.org/df/75/df75626840c76c15/mouseID_411732-182718/CH2',  # full res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    '321237-17302': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/321237-17302/green',
            2: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/321237-17302/red'
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': None,
    },

    '321244-17545': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/321244-17545/green',
            2: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/321244-17545/red'
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': None,
    },

    '326952-17304': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/326952-17304/green',
            2: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/326952-17304/red'
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': None,
    },

    '339951-17781': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/339951-17781/green',
            2: 'https://download.brainimagelibrary.org/94/77/94775d6a2ddab320/339951-17781/red'
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': None,
    },

    '339952-17782': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/339952-17782/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/339952-17782/red/montage'  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.2, 0.2),
    },

    '351327-17787': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/351327-17787/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/351327-17787/red/montage'  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    '351331-17788': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/351331-17788/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/351331-17788/red/montage'  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    '355458-18053': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/355458-18053/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/355458-18053/red/montage'  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    '355459-18054': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/355459-18054/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/355459-18054/red/montage',  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.35, 0.35),
    },

    '358361-18047': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/358361-18047/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/358361-18047/red/montage',  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    '373367-18454': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/373367-18454/green/montage',
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/373367-18454/red/montage'
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    '373368-18455': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/373368-18455/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/373368-18455/red/montage'  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    '381484-18457': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/381484-18457/green/montage',  # full_res
            2: 'https://download.brainimagelibrary.org/f1/dc/f1dcaeb016197373/381484-18457/red/montage'  # full_res
        },
        'label': {
            1: 'GFP',
            2: 'PI',
        },
        'scale': (1, 0.23, 0.23),
    },

    '182683': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ec/d7/ecd76000aad716f8/182683/182683/CH1',
            2: 'https://download.brainimagelibrary.org/ec/d7/ecd76000aad716f8/182683/182683/CH2'
        },
        'label': {
            1: None,
            2: None,
        },
        'scale': (1, 0.35, 0.35),
    },

    'mouseID_18011710-18066': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/df/8d/df8d3922f971e331/mouseID_18011710-18066/CH1',
        },
        'label': {
            1: 'GFP',
        },
        'scale': (1, 0.23, 0.23),
    },

    'mouseID_18011809-18072': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/73/ec/73ec63a56c799b6a/mouseID_18011809-18072/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18011810-18073': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/2f/f9/2ff927b79ce7c247/mouseID_18011810-18073/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18082503-18965': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/6d/b5/6db5ad6bbb46afcb/mouseID_18082503-18965/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18082506-18968': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/49/02/4902417b7c636fcc/mouseID_18082506-18968/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18082513-18975': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/cf/6c/cf6cbb30bd18f3ad/mouseID_18082513-18975/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18082518-18980': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/05/79/057964871bc6ecfb/mouseID_18082518-18980/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18082519-18981': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/20/e9/20e90875c9ae4542/mouseID_18082519-18981/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18101517-182280': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/69/19/6919a5da8261ea78/mouseID_18101517-182280/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18103003-182051': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/e9/a2/e9a2af1aaa175f9b/mouseID_18103003-182051/CH1',
        },
        'scale': (2, 0.325, 0.325),
        'label': {
            1: 'YFP',
        },
    },

    'mouseID_18103012-182056': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/21/7f/217f83338fcc1632/mouseID_18103012-182056/CH1',
        },
        'scale': (2, 0.325, 0.325),
        'label': {
            1: 'YFP',
        },
    },

    'mouseID_18110102-182061': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/16/a5/16a50e365f275fc2/mouseID_18110102-182061/CH1',
        },
        'scale': (2, 0.325, 0.325),
        'label': {
            1: 'YFP',
        },
    },

    'mouseID_18110103-182062': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/55/50/555003a95bda40ec/mouseID_18110103-182062/CH1',  # full res
        },
        'scale': (2, 0.325, 0.325),
        'label': {
            1: 'YFP',
        },
    },

    'mouseID_18110108-182065': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/11/63/1163b556224cc1e6/mouseID_18110108-182065/CH1',  # full res
        },
        'scale': (2, 0.325, 0.325),
        'label': {
            1: 'YFP',
        },
    },

    'mouseID_18110113-182069': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/07/51/0751d3f0a5bd672c/mouseID_18110113-182069/CH1',  # full res
        },
        'scale': (2, 0.325, 0.325),
        'label': {
            1: 'YFP',
        },
    },

    'mouseID_18121215-182932': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/2e/31/2e31d0b226c4de3e/mouseID_18121215-182932/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_19112221-195401': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/8a/f0/8af04b5469e576a7/mouseID_19112221-195401/CH1',  # full res
        },
        'scale': (1, 0.325, 0.325),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_236174': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/7f/53/7f537a62e521a26a/mouseID_236174/Raw-part1',
            # 'https://download.brainimagelibrary.org/7f/53/7f537a62e521a26a/mouseID_236174/Raw-part2' #Empty
        },
        'scale': None,
        'label': {
            1: None,
        },
    },

    'mouseID_297974': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/7f/53/7f537a62e521a26a/mouseID_297974/green',
            2: 'https://download.brainimagelibrary.org/7f/53/7f537a62e521a26a/mouseID_297974/red',
        },
        'scale': None,
        'label': {
            1: None,
            2: None,
        },
    },

    'mouseID_314107': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/7f/53/7f537a62e521a26a/mouseID_314107/green',
            2: 'https://download.brainimagelibrary.org/7f/53/7f537a62e521a26a/mouseID_314107/red'
        },
        'scale': None,
        'label': {
            1: None,
            2: None,
        },
    },

    'mouseID_327010-17298': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_327010-17298/17298_1/Green/montage',
            2: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_327010-17298/17298_1/Red/montage',
        },
        'scale': None,
        'label': {
            1: None,
            2: None,
        },
    },

    'mouseID_342870-17541': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_342870-17541/green',
            2: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_342870-17541/red'
        },
        'scale': None,
        'label': {
            1: None,
            2: None,
        },
    },

    'mouseID_344548-17542': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_344548-17542/green',
            2: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_344548-17542/red'
        },
        'scale': None,
        'label': {
            1: None,
            2: None,
        },
    },

    'mouseID_351325-17786': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_351325-17786/Green/montage',
            2: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_351325-17786/Red/montage',
        },
        'scale': None,
        'label': {
            1: None,
            2: None,
        },
    },

    'mouseID_369739-18459': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_369739-18459/green',
            2: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_369739-18459/red'
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',
        },
    },

    'mouseID_374712-18453': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_374712-18453/green',
            2: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_374712-18453/mouseID_374712-18453_CH2/red/montage'
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',
        },
    },

    'mouseID_396477-18869': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_396477-18869/green',
            2: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_396477-18869/red',
            # Resolution may be reduced
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',
        },
    },

    'mouseID_unknown-181349': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/6f/2c/6f2cea13d7d94efd/mouseID_unknown-181349/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_019081501-193388': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081501-193388/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081503-193374': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081503-193374/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081504-193375': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081504-193375/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081505-193376': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081505-193376/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081506-193377': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081506-193377/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081507-193378': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081507-193378/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081508-193379': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081508-193379/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081510-193381': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081510-193381/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081511-193382': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081511-193382/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081512-193383': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081512-193383/CH1',  # full res
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081513-193385': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081513-193385/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081514-193386': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081514-193386/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_019081515-193387': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_019081515-193387/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_18082502-18964': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/06/f4/06f4ef728fd23689/mouseID_18082502-18964/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18082511-18973': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/95/39/953951d23ff7dee2/mouseID_18082511-18973/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18082512-18974': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/94/27/9427ada8f2699b11/mouseID_18082512-18974/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18101512-182275': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/36/cd/36cd086800a14408/mouseID_18101512-182275/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18101514-182278': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/52/2d/522d38ee2fea3ff5/mouseID_18101514-182278/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
    },

    'mouseID_18112111-182448': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_18112111-182448/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_18112613-182680': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_18112613-182680/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_18112614-182681': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_18112614-182681/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_18112615-182682': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_18112615-182682/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_18121216-182931': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_18121216-182931/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010302-190132': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010302-190132/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010303-190134': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010303-190134/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010304-190133': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010304-190133/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010305-190128': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010305-190128/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010306-190130': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010306-190130/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010307-190131': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010307-190131/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010308-190129': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010308-190129/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010309-190138': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010309-190138/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010310-190135': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010310-190135/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19010312-190136': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19010312-190136/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011801-190363': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011801-190363/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011802-190364': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011802-190364/CH1',  # full res
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011803-190365': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011803-190365/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011804-190366': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011804-190366/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011805-190367': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011805-190367/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011806-190368': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011806-190368/CH1',  # full res
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011807-190369': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011807-190369/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19011808-190370': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19011808-190370/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19012101-190381': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/a2/6b/a26b3e1028ce1f09/mouseID_19012101-190381/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022512-190902': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022512-190902/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022513-190891': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022513-190891/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022514-190892': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022514-190892/CH1',  # full res
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022515-190900': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022515-190900/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022516-190901': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022516-190901/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022518_190903': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022518_190903/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022519-190905': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022519-190905/CH1',  # full res
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022520-190904': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022520-190904/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022521-190896': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022521-190896/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022522-190895': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022522-190895/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022523-190893': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022523-190893/CH1',  # full res
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022524-190894': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022524-190894/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022525-190897': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022525-190897/CH1',  # full res
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022526-190898': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022526-190898/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022714-190909': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022714-190909/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022715-190906': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022715-190906/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19022716-190907': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022716-190907/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },

    },

    'mouseID_19022717-190908': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19022717-190908/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },

    },

    'mouseID_19030601-191223': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030601-191223/CH1',  # full res
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },

    },

    'mouseID_19030602-191224': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030602-191224/CH1',  # full res
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030603-191225': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030603-191225/CH1',  # full res
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030606-191227': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030606-191227/CH1',  # full res
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030607-191192': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030607-191192/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030608-191193': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030608-191193/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030609-191194': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030609-191194/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030610-191195': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030610-191195/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030611-191196': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030611-191196/CH1',  # full res
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030612-191228': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030612-191228/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030613-191229': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030613-191229/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030614-191197': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030614-191197/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030615-191198': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030615-191198/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19030616-191199': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19030616-191199/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032503-191186': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032503-191186/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032504-191187': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032504-191187/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032505-191185': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032505-191185/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032506-191184': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032506-191184/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032507-191175': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032507-191175/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032508-191171': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032508-191171/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032509-191174': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032509-191174/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032510-191173': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032510-191173/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032511-191176': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032511-191176/CH1',
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032514-191183': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032514-191183/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032515-191182': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032515-191182/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032516-191180': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032516-191180/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032517-191178': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032517-191178/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032518-191177': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032518-191177/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_19032519-191179': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_19032519-191179/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_463865-192341': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_463865-192341/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
        },
        'alt_channel': {
            1: 'https://download.brainimagelibrary.org/ee/01/ee01a74d90e26226/mouseID_463865-192341/CH2_10_10_10um/'
        },
        'alt_label': {
            1: 'PI'
        },
        'alt_scale': (10, 10, 10),
    },

    'mouseID_w19051002-192869': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051002-192869/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051003-192868': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051003-192868/CH1',
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051004-192867': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051004-192867/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051005-192870': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051005-192870/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051006-192865': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051006-192865/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051007-192858': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051007-192858/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051009-192860': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051009-192860/CH1',
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051010-192861': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051010-192861/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051011-192855': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051011-192855/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051012-192856': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051012-192856/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051013-192862': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051013-192862/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051015-192853': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051015-192853/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051017-192863': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051017-192863/CH1',
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19051020-192857': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19051020-192857/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19082902-193644': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19082902-193644/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19082904-193646': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19082904-193646/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19082905-193647': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19082905-193647/CH1',
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19082908-193650': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19082908-193650/CH1',
        },
        'scale': (1, 0.23, 0.23),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19082909-193651': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19082909-193651/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19082922-193663': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19082922-193663/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19082925-193666': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19082925-193666/CH1',
        },
        'scale': (1, 0.35, 0.35),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19091704-194089': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19091704-194089/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19091705-194090': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19091705-194090/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19091706-194091': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19091706-194091/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19091707-194092': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19091707-194092/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19091708-194093': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19091708-194093/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19091709-194094': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19091709-194094/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

    'mouseID_w19091710-194095': {
        'channel': {
            1: 'https://download.brainimagelibrary.org/00/9c/009c1e6fcc03ebac/mouseID_w19091710-194095/CH1',
        },
        'scale': (1, 0.32, 0.32),
        'label': {
            1: 'GFP',
            2: 'PI',  # Metadata lists PI, but no image information exists
        },
    },

}
