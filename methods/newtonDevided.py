def newton_divided_diff_coeffs(xs, ys):
    n = len(xs)
    coeffs = ys.copy()
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coeffs[i] = (coeffs[i] - coeffs[i - 1]) / (xs[i] - xs[i - j])
    return coeffs

def newton_divided(xs, ys, x):
    coeffs = newton_divided_diff_coeffs(xs, ys)
    n = len(xs)
    result = coeffs[-1]
    for i in range(n - 2, -1, -1):
        result = result * (x - xs[i]) + coeffs[i]
    return result
