from PIL.ImageChops import difference

from methods.differenceTable import build_difference_table

def newtonFinalForward(xs, ys, x):
    h = xs[1] - xs[0]
    diff = build_difference_table(xs, ys)
    t = (x - xs[0]) / h
    result = ys[0]
    factorial = 1.0
    prod = 1.0
    for k in range(1, len(xs)):
        prod *= t - (k - 1)
        factorial *= k
        result += (prod / factorial) * diff[k][0]
    return result