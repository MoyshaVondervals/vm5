def lagrange(xs, ys, x):
    n = len(xs)
    total = 0.0
    for i in range(n):
        term = ys[i]
        for j in range(n):
            if i == j:
                continue
            term *= (x - xs[j]) / (xs[i] - xs[j])
        total += term
    return total