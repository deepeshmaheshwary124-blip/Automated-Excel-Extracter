"""Matplotlib chart widget for dashboard and analytics."""

from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QSizePolicy

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("QtAgg")


class ChartWidget(QFrame):
    def __init__(self, title: str = "", chart_type: str = "bar") -> None:
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(220)
        self.chart_type = chart_type

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        if title:
            title_label = QLabel(title)
            title_label.setObjectName("sectionLabel")
            layout.addWidget(title_label)

        self.figure = Figure(figsize=(5, 2.5), dpi=100)
        self.figure.patch.set_facecolor("#252640")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas, 1)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#252640")
        self.ax.spines["bottom"].set_color("#32335a")
        self.ax.spines["left"].set_color("#32335a")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.tick_params(colors="#9a9bb4", labelsize=9)
        self.ax.set_title("", color="#e8e9f0", fontsize=11)

    def update_data(self, labels: list[str], values: list[float],
                    bar_label: str = "", color: str = "#6c63ff") -> None:
        self.ax.clear()
        self.ax.set_facecolor("#252640")
        self.ax.spines["bottom"].set_color("#32335a")
        self.ax.spines["left"].set_color("#32335a")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.tick_params(colors="#9a9bb4", labelsize=9)

        if self.chart_type == "bar":
            bars = self.ax.bar(labels, values, color=color, alpha=0.8, width=0.6)
            for bar in bars:
                bar.set_edgecolor("none")
        elif self.chart_type == "line":
            self.ax.plot(labels, values, color=color, marker="o",
                        linewidth=2, markersize=4)
            self.ax.fill_between(range(len(values)), values, alpha=0.1, color=color)

        self.ax.set_xlabel("", color="#9a9bb4", fontsize=9)
        max_val = max(values) if values else 1
        self.ax.set_ylim(0, max_val * 1.2 if max_val > 0 else 1)

        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self) -> None:
        self.ax.clear()
        self.canvas.draw()
