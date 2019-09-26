#!/usr/bin/env python3
"""
Calculate the extrapolation matrices for various elements.

"""
import numpy as np


def shape_funcs_c3d6(n, r, s, t):
    n += 1

    if n == 1:
        return (1 - r - s)*(1 - t)/2

    if n == 2:
        return r*(1 - t)/2

    if n == 3:
        return s*(1 - t)/2

    if n == 4:
        return (1 - r - s)*(1 + t)/2

    if n == 5:
        return r*(1 + t)/2

    if n == 6:
        return s*(1 + t)/2


def shape_funcs_c3d8(n, r, s, t):
    n += 1

    if n == 1:
        return (1 - r)*(1 - s)*(1 - t)/8

    if n == 2:
        return (1 + r)*(1 - s)*(1 - t)/8

    if n == 3:
        return (1 + r)*(1 + s)*(1 - t)/8

    if n == 4:
        return (1 - r)*(1 + s)*(1 - t)/8

    if n == 5:
        return (1 - r)*(1 - s)*(1 + t)/8

    if n == 6:
        return (1 + r)*(1 - s)*(1 + t)/8

    if n == 7:
        return (1 + r)*(1 + s)*(1 + t)/8

    if n == 8:
        return (1 - r)*(1 + s)*(1 + t)/8

def shape_funcs_c3d15(n, r, s, t):
    """
    Shape functions for C3D15R element.

    """
    n += 1

    if (n==1):
        return -(1-r-s)*(1-t)*(2*r + 2*s + t)/2

    if (n==2):
        return r*(1-t)*(2*r - t - 2)/2

    if (n==3):
        return s*(1-t)*(2*s - t - 2)/2

    if (n==4):
        return -(1-r-s)*(1+t)*(2*r + 2*s - t)/2

    if (n==5):
        return r*(1 + t)*(2*r + t - 2)/2

    if (n==6):
        return s*(1 + t)*(2*s + t - 2)/2

    if (n==7):
        return 2*r*(1-r-s)*(1-t)

    if (n==8):
        return 2*r*s*(1-t)

    if (n==9):
        return 2*s*(1-r-s)*(1-t)

    if (n==10):
        return 2*r*(1-r-s)*(1+t)

    if (n==11):
        return 2*r*s*(1+t)

    if (n==12):
        return 2*s*(1-r-s)*(1+t)

    if (n==13):
        return (1-r-s)*(1-t*t)

    if (n==14):
        return r*(1-t*t)

    if (n==15):
        return s*(1-t*t)


def shape_funcs_c3d20(n, r, s, t):
    """
    Shape functions for C3D20R element.

    """
    n += 1

    if (n==1):
        return -(1-r)*(1-s)*(1-t)*(2+r+s+t)/8

    if (n==2):
        return -(1+r)*(1-s)*(1-t)*(2-r+s+t)/8

    if (n==3):
        return -(1+r)*(1+s)*(1-t)*(2-r-s+t)/8

    if (n==4):
        return -(1-r)*(1+s)*(1-t)*(2+r-s+t)/8


    if (n==5):
        return -(1-r)*(1-s)*(1+t)*(2+r+s-t)/8

    if (n==6):
        return -(1+r)*(1-s)*(1+t)*(2-r+s-t)/8

    if (n==7):
        return -(1+r)*(1+s)*(1+t)*(2-r-s-t)/8

    if (n==8):
        return -(1-r)*(1+s)*(1+t)*(2+r-s-t)/8


    if (n==9):
        return (1-r)*(1+r)*(1-s)*(1-t)/4

    if (n==10):
        return (1+r)*(1-s)*(1+s)*(1-t)/4

    if (n==11):
        return (1-r)*(1+r)*(1+s)*(1-t)/4

    if (n==12):
        return (1-r)*(1-s)*(1+s)*(1-t)/4


    if (n==13):
        return (1-r)*(1+r)*(1-s)*(1+t)/4

    if (n==14):
        return (1+r)*(1-s)*(1+s)*(1+t)/4

    if (n==15):
        return (1-r)*(1+r)*(1+s)*(1+t)/4

    if (n==16):
        return (1-r)*(1-s)*(1+s)*(1+t)/4


    if (n==17):
        return (1-r)*(1-s)*(1-t)*(1+t)/4

    if (n==18):
        return (1+r)*(1-s)*(1-t)*(1+t)/4

    if (n==19):
        return (1+r)*(1+s)*(1-t)*(1+t)/4

    if (n==20):
        return (1-r)*(1+s)*(1-t)*(1+t)/4



sqrt_3 = np.sqrt(3)
sqrt_3_over_5 = np.sqrt(3/5)

element_types = {
    'c3d6': {
        'node_count': 6,
        'integration_point_count': 9,
        'integration_points': [
            [1/6, 1/6, -sqrt_3_over_5],  # 1
            [4/6, 1/6, -sqrt_3_over_5],  # 2
            [1/6, 4/6, -sqrt_3_over_5],  # 3
            [1/6, 1/6, 0],  # 4
            [4/6, 1/6, 0],  # 5
            [1/6, 4/6, 0],  # 6
            [1/6, 1/6, sqrt_3_over_5],  # 7
            [4/6, 1/6, sqrt_3_over_5],  # 8
            [1/6, 4/6, sqrt_3_over_5]   # 9
        ],
        'shape_funcs': shape_funcs_c3d6
    },
    'c3d8': {
        'node_count': 8,
        'integration_point_count': 8,
        'integration_points': [
            [-1/sqrt_3, -1/sqrt_3, -1/sqrt_3],  # 1
            [+1/sqrt_3, -1/sqrt_3, -1/sqrt_3],  # 2
            [+1/sqrt_3, +1/sqrt_3, -1/sqrt_3],  # 3
            [-1/sqrt_3, +1/sqrt_3, -1/sqrt_3],  # 4
            [-1/sqrt_3, -1/sqrt_3, +1/sqrt_3],  # 5
            [+1/sqrt_3, -1/sqrt_3, +1/sqrt_3],  # 6
            [+1/sqrt_3, +1/sqrt_3, +1/sqrt_3],  # 7
            [-1/sqrt_3, +1/sqrt_3, +1/sqrt_3]   # 8
        ],
        'shape_funcs': shape_funcs_c3d8
    },
    'c3d15': {
        'node_count': 15,
        'integration_point_count': 9,
        'integration_points': [
            [1/6, 1/6, -sqrt_3_over_5],  # 1
            [4/6, 1/6, -sqrt_3_over_5],  # 2
            [1/6, 4/6, -sqrt_3_over_5],  # 3
            [1/6, 1/6, 0],  # 4
            [4/6, 1/6, 0],  # 5
            [1/6, 4/6, 0],  # 6
            [1/6, 1/6, sqrt_3_over_5],  # 7
            [4/6, 1/6, sqrt_3_over_5],  # 8
            [1/6, 4/6, sqrt_3_over_5]   # 9
        ],
        'shape_funcs': shape_funcs_c3d15
    },
    'c3d20': {
        'node_count': 20,
        'integration_point_count': 8,
        'integration_points': [
            [-1/sqrt_3, -1/sqrt_3, -1/sqrt_3],  # 1
            [+1/sqrt_3, -1/sqrt_3, -1/sqrt_3],  # 2
            [+1/sqrt_3, +1/sqrt_3, -1/sqrt_3],  # 3
            [-1/sqrt_3, +1/sqrt_3, -1/sqrt_3],  # 4
            [-1/sqrt_3, -1/sqrt_3, +1/sqrt_3],  # 5
            [+1/sqrt_3, -1/sqrt_3, +1/sqrt_3],  # 6
            [+1/sqrt_3, +1/sqrt_3, +1/sqrt_3],  # 7
            [-1/sqrt_3, +1/sqrt_3, +1/sqrt_3]   # 8
        ],
        'shape_funcs': shape_funcs_c3d20
    }

}


for elem_type in ['c3d6', 'c3d8', 'c3d15', 'c3d20']:
    int_points = element_types[elem_type]['integration_points']
    node_count = element_types[elem_type]['node_count']
    func = element_types[elem_type]['shape_funcs']
    int_point_count = element_types[elem_type]['integration_point_count']

    target = np.empty([int_point_count, node_count])
    for i in range(int_point_count):
        for j in range(node_count):
            target[i, j] = func(j, *int_points[i])  # asterisk is unpacking of list

    pinv_target = np.linalg.pinv(target)
    int_to_node = pinv_target

    print(elem_type)
    print(repr(int_to_node))
    print()
