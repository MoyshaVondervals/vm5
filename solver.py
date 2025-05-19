# -*- coding: utf-8 -*-
"""
Модуль solver.py
Содержит всю «математику» и обновляет интерфейс через объект main GUI.
"""

from __future__ import annotations

import math

import numpy as np

from eqDelta import eqDelta
from methods.bessel import bessel_interpolate
from methods.differenceTable import build_difference_table
from methods.lagrange import lagrange
from methods.newtonDevided import newton_divided
from methods.newtonFinalBack import newtonFinalBack
from methods.newtonFinalForward import newtonFinalForward
from methods.stirling import stirling_interpolate

FUNC_MAP = {
    "sin(x)": np.sin,
    "cos(x)": np.cos,
    "exp(x)": np.exp,
}
def process_data(payload_kind, payload_data, methods, x0, gui):
    print(payload_kind, payload_data, methods, x0)

    x = 0
    y = 0
    if payload_kind == "table":
        pts = payload_data  # list of (x,y)
        x = np.array([p[0] for p in pts], dtype=float)
        y = np.array([p[1] for p in pts], dtype=float)
        print("X table:",x)
        print("Y table:",y)
    elif payload_kind == "file":
        xs: list[float] = []
        ys: list[float] = []
        path = payload_data
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.replace(",", ".").split()
                if len(parts) != 2:
                    gui.err(f"Файл: строка {i} — нужно 2 числа, а не {len(parts)}")
                    return False
                try:
                    xv, yv = map(float, parts)
                except ValueError:
                    gui.err(f"Файл: строка {i} — неверный формат числа")
                    return False
                xs.append(xv)
                ys.append(yv)
        if len(xs) < 2:
            gui.err("В файле меньше 2 точек")
            return False
        x = np.array(xs, dtype=float)
        y = np.array(ys, dtype=float)
        print("X file:", x)
        print("Y file:", y)

    else:
        cfg = payload_data
        name = cfg["name"]
        left = cfg["left"]
        right = cfg["right"]
        n = cfg["n"]
        func = FUNC_MAP[name]
        x = np.linspace(left, right, n)
        y = func(x)
        print("X func:", x)
        print("Y func:", y)
    if (methods.get("lagrange", True) or methods.get("newtonPP", True) or methods.get("newtonKP1", True)
            or methods.get("newtonKP2", True) or methods.get("stirling", True)) or methods.get("bessel", True):
        gui.clear_diff_table()
        gui.clear_results()
        gui.ax.clear()
        init_plot(x, y, gui)
        if methods.get("lagrange", True):
            P = lagrange(x, y, x0)
            gui.add_result("Лагранж", f"P({x0:.4g}) = {P:.6g}")
            plot_lagrange_curve(x, y, x0, gui)


        if methods.get("newtonPP", True):
            P = newton_divided(x, y, x0)
            gui.add_result("Многочлен Ньютона (РР)", f"P({x0:.4g}) = {P:.6g}")
            plot_newtonPP_curve(x, y, gui)
        if eqDelta(x):
            isForward = False;
            mid = (x[0]+x[-1])/2
            if x0<=mid:
                isForward = True

            if methods.get("newtonKP1", True) and isForward:
                P = newtonFinalForward(x, y, x0)
                gui.add_result("Многочлен Ньютона (KP)1", f"P({x0:.4g}) = {P:.6g}")
                plot_newtonKP1_curve(x, y, gui)

            if methods.get("newtonKP1", True) and not isForward:

                P = newtonFinalBack(x, y, x0)
                gui.add_result("Многочлен Ньютона (KP)2", f"P({x0:.4g}) = {P:.6g}")
                plot_newtonKP2_curve(x, y, gui)


            if methods.get("stirling", True) and len(x)%2!=0:

                P = stirling_interpolate(x, y, x0)
                gui.add_result("Схема Стирлинга", f"P({x0:.4g}) = {P:.6g}")
                plot_stirling_curve(x, y, gui)

            if methods.get("bessel", True)and len(x)%2==0:
                P = bessel_interpolate(x, y, x0)
                gui.add_result("Схема Бесселя", f"P({x0:.4g}) = {P:.6g}")
                plot_bessel_curve(x, y, gui)



        else:
            gui.ok("Для методов Ньютона КР1-2, Стирлинга и Бесселя, узлы должны быть равноотстоящими по X")

        gui.tbl_results.resizeColumnsToContents()
        gui.tbl_results.resizeRowsToContents()
        print("printing")
        if eqDelta(x):
            diffTable = build_difference_table(x, y)
            gui.update_diff_table(diffTable)
        gui.ax.legend()
        gui.ax.set_title("Интерполяция")
        gui.canvas.draw()
        return True
    else:
        gui.err("Методы не выбраны")
        return False



def init_plot(x, y, gui):
    print("graph init")
    gui.ax.plot(x, y, 'o', label='Узлы')

def plot_lagrange_curve(x: np.ndarray, y: np.ndarray, x0, gui):
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.array([lagrange(x, y, xv) for xv in xi])
    gui.ax.plot(xi, yi, '-',  label='Лагранж P(x)')
    gui.ax.scatter(x0, lagrange(x, y, x0), color='red')
    print("lagrange graph")

def plot_newtonPP_curve(x: np.ndarray, y: np.ndarray, gui):
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.array([newton_divided(x, y, xv) for xv in xi])
    gui.ax.plot(xi, yi, '-', label='Ньютона (РР)')
    print("newtonPP graph")

def plot_newtonKP1_curve(x: np.ndarray, y: np.ndarray, gui):
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.array([newtonFinalForward(x, y, xv) for xv in xi])
    gui.ax.plot(xi, yi, '--', label='Ньютона (KР1)')
    print("newtonKP1 graph")

def plot_newtonKP2_curve(x: np.ndarray, y: np.ndarray, gui):
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.array([newtonFinalBack(x, y, xv) for xv in xi])
    gui.ax.plot(xi, yi, '--', label='Ньютона (KР2)')
    print("newtonKP2 graph")

def plot_stirling_curve(x: np.ndarray, y: np.ndarray, gui):
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.array([stirling_interpolate(x, y, xv) for xv in xi])
    gui.ax.plot(xi, yi, '-.', label='Стирлинг')
    print("stirling graph")

def plot_bessel_curve(x: np.ndarray, y: np.ndarray, gui):
    print("bessel graph")
    xi = np.linspace(x.min(), x.max(), len(x)*5)
    yi = np.array([bessel_interpolate(x, y, xv) for xv in xi])
    gui.ax.plot(xi, yi, ':', label='Бессель')