from math import factorial  # factorial нужен только для наглядности формул

from methods.differenceTable import build_difference_table

def bessel_interpolate(xs, ys, x0):
    diff = build_difference_table(xs, ys)

    h = xs[1] - xs[0]
    n = len(xs)
    m = n // 2 - 1

    t = (x0 - xs[m]) / h
    result = (ys[m] + ys[m + 1]) / 2
    result += (t - 0.5) * diff[1][m]

    even_coeff = t * (t - 1) / 2
    odd_coeff  = (t - 0.5) * t * (t - 1) / 6

    r = 1
    while True:
        k_even = 2 * r
        k_odd  = k_even + 1
        if k_even < len(diff):
            left  = m - r
            right = left + 1
            if 0 <= left and right < len(diff[k_even]):
                avg = (diff[k_even][left] + diff[k_even][right]) / 2
                result += even_coeff * avg
        if k_odd < len(diff):
            idx = m - r
            if 0 <= idx < len(diff[k_odd]):
                result += odd_coeff * diff[k_odd][idx]

        if k_even >= len(diff) and k_odd >= len(diff):
            break
        if m - r - 1 < 0:
            break
        even_coeff *= (t + r) * (t - r - 1) / ((2 * r + 2) * (2 * r + 1))
        odd_coeff  *= (t + r) * (t - r - 1) / ((2 * r + 3) * (2 * r + 2))

        r += 1

    return result
