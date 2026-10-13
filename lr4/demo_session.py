"""Демонстрационный сеанс: прогоняет программу на заранее заданных ответах
и записывает протокол экрана в session.txt (для отчёта)."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from combopt.graph import Graph  # noqa: E402
from combopt.ui import Console  # noqa: E402

SAMPLE = [[0, 12, 10, 19, 8], [12, 0, 3, 7, 2], [10, 3, 0, 6, 20],
          [19, 7, 6, 0, 4], [8, 2, 20, 4, 0]]

os.makedirs("out", exist_ok=True)
Graph.from_matrix(SAMPLE).save("out/cities5.json")

answers = [
    "3", "out/cities5.json",
    "5",
    "6", "1", "д", "out/tsp.png",
    "7", "1", "4", "д", "out/path.png",
    "8", "д", "out/mst.png",
    "9",
    "7", "ноль", "1", "77", "3", "н",
    "2", "20", "д", "6", "1", "н",
    "0",
]
it = iter(answers)
log = []


def fake_input(prompt):
    value = next(it)
    log.append(prompt + value)
    return value


Console(fake_input, log.append).run()
with open("out/session.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(log))
print("\n".join(log))
