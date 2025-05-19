from methods.differenceTable import build_difference_table


def stirling_interpolate(xs, ys, x0):

    h = xs[1] - xs[0]
    diff = build_difference_table(xs, ys)

    n = len(xs) - 1
    alpha = n // 2
    t = (x0 - xs[alpha]) / h

    s1 = ys[alpha]
    s2 = ys[alpha]

    prod1 = 1.0
    prod2 = 1.0
    fact = 1.0

    shifts = [0]
    for i in range(1, n + 1):
        shifts.extend([-i, i])
    shifts = shifts[:n]

    for k in range(1, n + 1):
        fact *= k
        shift = shifts[k - 1]

        prod1 *= t + shift
        prod2 *= t - shift

        idx_c = len(diff[k]) // 2
        delta_c = diff[k][idx_c]

        idx_s = idx_c - (1 - len(diff[k]) % 2)
        delta_s = diff[k][idx_s]

        s1 += prod1 * delta_c / fact
        s2 += prod2 * delta_s / fact

    return (s1 + s2) / 2