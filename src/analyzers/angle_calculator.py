import math
import numpy as np

def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

def test_angles():    
    test_ax = [0,0,0.5]
    test_ay = [0,0,0.5]
    test_bx = [0,1,0]
    test_by = [1,0,0]
    test_cx = [1,2,0.5]
    test_cy = [1,0,0]

    for i in range(0, len(test_ax)):
        out = math.floor(calculate_angle((test_ax[i], test_ay[i]), (test_bx[i], test_by[i]), (test_cx[i], test_cy[i])))
        print(f'{i} : angle: {out}') 