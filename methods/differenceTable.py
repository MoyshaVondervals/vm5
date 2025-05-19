from typing import List

def build_difference_table(xs, ys):
    n = len(ys)
    table = [ys.copy()]
    for k in range(1, n):
        prev = table[-1]
        column = [prev[i+1] - prev[i] for i in range(n-k)]
        table.append(column)
    return table
