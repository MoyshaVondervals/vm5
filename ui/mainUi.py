#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
interpolator_gui.py — главное окно.
Никаких вычислений конечных разностей здесь НЕТ.
"""

import sys
from pathlib import Path
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
    QCheckBox, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QComboBox, QLineEdit, QSpinBox, QStackedWidget, QStatusBar,
    QSizePolicy, QDoubleSpinBox, QAbstractItemView
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# -------------------- внешний модуль -------------------------------------------
from solver import process_data        # функция вычислений

# -------------------- константы -------------------------------------------------
MAX_POINTS = 20
FUNCTION_MAP = {
    "sin(x)": np.sin,
    "cos(x)": np.cos,
    "exp(x)": np.exp,
}

# ===============================================================================
class InterpolatorGUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Интерполятор")
        self.resize(1200, 700)
        self._build_ui()


    # ----------------------- построение интерфейса ----------------------------
    def _build_ui(self) -> None:

        root = QVBoxLayout(self)

        # 1-я строка: радиокнопки, чекбоксы, результаты
        top = QHBoxLayout(); root.addLayout(top)

        # источник данных
        self.source_group = QGroupBox("Метод ввода данных")
        sl = QVBoxLayout(self.source_group)
        self.rb_table = QRadioButton("Таблица")
        self.rb_file  = QRadioButton("Файл .txt")
        self.rb_func  = QRadioButton("Функция")
        self.rb_table.setChecked(True)
        for rb in (self.rb_table, self.rb_file, self.rb_func):
            sl.addWidget(rb); rb.toggled.connect(self._switch_page)
        top.addWidget(self.source_group)



        self.method_group = QGroupBox("Методы расчёта")
        ml = QVBoxLayout(self.method_group)
        self.cb_lagr = QCheckBox("Многочлен Лагранжа")
        self.cb_newtPP = QCheckBox("Многочлен Ньютона (РР)")
        self.cb_newtKP1 = QCheckBox("Формула Ньютона (КР)")
        # self.cb_newtKP2 = QCheckBox("Формула Ньютона 2 (КР)")
        self.cb_stirling = QCheckBox("Схема Стирлинга")
        self.cb_bessel = QCheckBox("Схема Бесселя")
        # for cb in (self.cb_lagr, self.cb_newtPP, self.cb_newtKP1, self.cb_newtKP2, self.cb_stirling, self.cb_bessel):
        for cb in (self.cb_lagr, self.cb_newtPP, self.cb_newtKP1, self.cb_stirling, self.cb_bessel):
            ml.addWidget(cb)

        # добавляем кнопку выбора всех чекбоксов
        self.btn_select_all = QPushButton("Выбрать всё")
        ml.addWidget(self.btn_select_all)
        self.btn_select_all.clicked.connect(self._select_all_methods)
        top.addWidget(self.method_group)



        # мини-таблица «Метод: ответ»
        self.result_box = QGroupBox("Результаты")
        rl = QVBoxLayout(self.result_box)
        self.tbl_results = QTableWidget(0, 2)
        self.tbl_results.setHorizontalHeaderLabels(["Метод", "Ответ"])
        self.tbl_results.horizontalHeader().setStretchLastSection(True)
        self.tbl_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        rl.addWidget(self.tbl_results)
        top.addWidget(self.result_box)

        # 2-я строка: таблица конечных разностей
        diff_box = QGroupBox("Таблица конечных разностей")
        dl = QVBoxLayout(diff_box)
        self.tbl_diffs = QTableWidget(0, 1)
        self.tbl_diffs.setSizePolicy(QSizePolicy.Policy.Expanding,
                                     QSizePolicy.Policy.Fixed)
        self.tbl_diffs.setFixedHeight(120)
        dl.addWidget(self.tbl_diffs)
        root.addWidget(diff_box)

        # 3-я строка: слева — ввод + x*, справа — график
        mid = QHBoxLayout(); root.addLayout(mid)

        # левая колонка: страницы и поле x*
        left_col = QVBoxLayout()
        self.pages = QStackedWidget()
        left_col.addWidget(self.pages, 1)
        self._page_table()
        self._page_file()
        self._page_func()
        # статичное поле x*
        xstar_row = QHBoxLayout()
        xstar_row.addWidget(QLabel("x* ="))
        self.sb_xstar = QDoubleSpinBox()
        self.sb_xstar.setRange(-1e6, 1e6)
        self.sb_xstar.setDecimals(8)
        self.sb_xstar.setValue(0.0)
        xstar_row.addWidget(self.sb_xstar)
        left_col.addLayout(xstar_row)
        mid.addLayout(left_col, 2)

        # правая колонка: график matplotlib
        self.fig = Figure(figsize=(5, 4))
        self.ax  = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        mid.addWidget(self.canvas, 3)

        # 4-я строка: статус-бар и кнопка «Решить»
        bottom = QHBoxLayout(); root.addLayout(bottom)
        self.status = QStatusBar(); bottom.addWidget(self.status, 5)
        btn_solve = QPushButton("Решить"); btn_solve.clicked.connect(self._solve)
        bottom.addWidget(btn_solve, 1)

    # ----------------------- страницы ввода -----------------------------------

    def _select_all_methods(self) -> None:
        # for cb in (self.cb_lagr, self.cb_newtPP, self.cb_newtKP1, self.cb_newtKP2, self.cb_stirling, self.cb_bessel):
        for cb in (self.cb_lagr, self.cb_newtPP, self.cb_newtKP1, self.cb_stirling, self.cb_bessel):
            cb.setChecked(True)

    def _page_table(self) -> None:
        w = QWidget(); l = QVBoxLayout(w)
        self.tbl_input = QTableWidget(3, 2)
        self.tbl_input.setHorizontalHeaderLabels(["x", "y"])
        self.tbl_input.horizontalHeader().setStretchLastSection(True)
        l.addWidget(self.tbl_input)
        btns = QHBoxLayout(); btns.addStretch()
        plus  = QPushButton("+ строка");  plus.clicked.connect(self._add_row)
        minus = QPushButton("– строка"); minus.clicked.connect(self._del_row)
        btns.addWidget(plus); btns.addWidget(minus); btns.addStretch()
        l.addLayout(btns)
        self.pages.addWidget(w)

    def _page_file(self) -> None:
        w = QWidget(); l = QVBoxLayout(w)
        h = QHBoxLayout()
        self.le_path = QLineEdit(); self.le_path.setReadOnly(True)
        browse = QPushButton("Обзор…"); browse.clicked.connect(self._browse)
        h.addWidget(self.le_path); h.addWidget(browse); l.addLayout(h)
        self.pages.addWidget(w)

    def _page_func(self) -> None:
        w = QWidget(); l = QVBoxLayout(w)
        r1 = QHBoxLayout()
        self.cmb_func = QComboBox(); self.cmb_func.addItems(list(FUNCTION_MAP.keys()))
        r1.addWidget(QLabel("f(x) =")); r1.addWidget(self.cmb_func); l.addLayout(r1)
        r2 = QHBoxLayout()
        self.le_left  = QLineEdit("-3.14"); self.le_right = QLineEdit("3.14")
        for le in (self.le_left, self.le_right): le.setValidator(QDoubleValidator())
        r2.addWidget(QLabel("Левая:"));  r2.addWidget(self.le_left)
        r2.addWidget(QLabel("Правая:")); r2.addWidget(self.le_right)
        l.addLayout(r2)
        r3 = QHBoxLayout()
        self.sb_n = QSpinBox(); self.sb_n.setRange(2, MAX_POINTS); self.sb_n.setValue(10)
        r3.addWidget(QLabel("N точек:")); r3.addWidget(self.sb_n); l.addLayout(r3)
        self.pages.addWidget(w)

    # ----------------------- вспомогательные ----------------------------------

    def update_diff_table(self, diff):
        cols = len(diff)
        rows = len(diff[0]) if cols else 0

        self.tbl_diffs.clearContents()
        self.tbl_diffs.setRowCount(rows)
        self.tbl_diffs.setColumnCount(cols)

        headers = ["y"] + [f"Δ^{i}" for i in range(1, cols)]
        self.tbl_diffs.setHorizontalHeaderLabels(headers)

        for c, col in enumerate(diff):
            for r, val in enumerate(col):
                item = QTableWidgetItem(f"{float(val):.6g}")
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.tbl_diffs.setItem(r, c, item)

        self.tbl_diffs.resizeRowsToContents()
        self.tbl_diffs.resizeColumnsToContents()
        self.tbl_diffs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _switch_page(self) -> None:
        if   self.rb_table.isChecked(): self.pages.setCurrentIndex(0)
        elif self.rb_file.isChecked():  self.pages.setCurrentIndex(1)
        else:                            self.pages.setCurrentIndex(2)

    def _add_row(self) -> None:
        if self.tbl_input.rowCount() >= MAX_POINTS:
            self.err(f"Нельзя > {MAX_POINTS} строк"); return
        self.tbl_input.insertRow(self.tbl_input.rowCount())

    def _del_row(self) -> None:
        rows = {i.row() for i in self.tbl_input.selectedIndexes()}
        tgt = max(rows) if rows else self.tbl_input.rowCount() - 1
        if self.tbl_input.rowCount() == 1:
            self.err("Хотя бы одна строка должна остаться"); return
        self.tbl_input.removeRow(tgt)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Открыть .txt", "", "Text files (*.txt)")
        if path: self.le_path.setText(path)

    # ----------------------- сбор данных --------------------------------------
    def _collect_points(self):
        xs, ys = [], []
        for r in range(self.tbl_input.rowCount()):
            ix, iy = self.tbl_input.item(r, 0), self.tbl_input.item(r, 1)
            if (ix is None or not ix.text().strip()) and (iy is None or not iy.text().strip()):
                raise ValueError(f"Заполните ячейки")
            if ix is None or iy is None or not ix.text().strip() or not iy.text().strip():
                raise ValueError(f"Незаполненная ячейка в строке {r + 1}")
            xs.append(float(ix.text().replace(",", ".").strip()))
            ys.append(float(iy.text().replace(",", ".").strip()))
        if len(xs) < 2:
            raise ValueError("Нужно минимум две точки")
        return list(zip(xs, ys))

    # ----------------------- кнопка «Решить» ----------------------------------
    def _solve(self) -> None:
        self.status.clearMessage()
        # собираем payload
        try:
            if   self.rb_table.isChecked():
                kind, data = "table", self._collect_points()
            elif self.rb_file.isChecked():
                if not self.le_path.text():
                    raise ValueError("Файл не выбран")
                kind, data = "file", self.le_path.text()
            else:
                left  = float(self.le_left.text().replace(",", "."))
                right = float(self.le_right.text().replace(",", "."))
                if right <= left:
                    raise ValueError("Правая граница ≤ левой")
                kind = "func"
                data = {
                    "name":  self.cmb_func.currentText(),
                    "left":  left,
                    "right": right,
                    "n":     self.sb_n.value(),
                    "xstar": self.sb_xstar.value()
                }
        except ValueError as e:

            self.err(str(e))
            return


        methods = {
            "lagrange": self.cb_lagr.isChecked(),
            "newtonPP": self.cb_newtPP.isChecked(),
            "newtonKP1": self.cb_newtKP1.isChecked(),
            # "newtonKP2": self.cb_newtKP2.isChecked(),
            "stirling": self.cb_stirling.isChecked(),
            "bessel": self.cb_bessel.isChecked(),
        }

        # try:
        stat = process_data(kind, data, methods, self.sb_xstar.value(), self)


    # ----------------------- API для solver и статус-бар --------------------
    def clear_diff_table(self) -> None:
        self.tbl_diffs.clear(); self.tbl_diffs.setRowCount(0); self.tbl_diffs.setColumnCount(0)
    def clear_results(self) -> None:
        self.tbl_results.setRowCount(0)
    def add_result(self, method: str, value: str) -> None:
        row = self.tbl_results.rowCount(); self.tbl_results.insertRow(row)
        self.tbl_results.setItem(row, 0, QTableWidgetItem(method))
        self.tbl_results.setItem(row, 1, QTableWidgetItem(value))
    def err(self, msg: str): self.status.showMessage(f"Ошибка: {msg}", 10000)
    def ok (self, msg: str): self.status.showMessage(msg, 5000)

# --------------------------- main ----------------------------------------------
def main() -> None:
    app = QApplication(sys.argv)
    gui = InterpolatorGUI(); gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
