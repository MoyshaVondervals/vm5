from methods.differenceTable import build_difference_table

def newtonFinalBack(xs, ys, x):
    h = xs[1] - xs[0]
    diff = build_difference_table(xs, ys)
    n = len(xs)
    t = (x - xs[-1]) / h
    result = ys[-1]
    factorial = 1.0
    prod = 1.0
    for k in range(1, n):
        prod *= t + (k - 1)
        factorial *= k
        result += (prod / factorial) * diff[k][n - k - 1]
    return result