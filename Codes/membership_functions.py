import math
import numpy as np
import matplotlib as plt


def triangular(x, a, b, c):
    if x <= a or x >= c:
        return 0
    elif a <= x <= b:
        return (x-a)/(b-a)
    elif b <= x <= c:
        return (c-x)/(c-b)


def trapezoidal(x, a, b, c, d):
    if x <= a or x >= d:
        return 0
    elif a <= x <= b:
        return (x-a)/(b-a)
    elif b <= x <= c:
        return 1
    elif c <= x <= d:
        return (d-x)/(d-c)


def gaussian(x, c, sigma):
    return math.exp((-math.pow(x-c, 2))/(2*math.pow(sigma, 2)))


def sigmoidal(x, a, c):
    return math.pow((1+math.exp((-a*(x-c)))), -1)
