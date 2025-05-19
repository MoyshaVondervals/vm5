def eqDelta(xs):
    h = xs[1] - xs[0]
    if any(abs((xs[i + 1] - xs[i]) - h) > 1e-9 for i in range(len(xs) - 1)):
        return False
    else:
        return True