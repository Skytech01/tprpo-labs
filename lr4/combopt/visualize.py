"""Модуль visualize — рисунок графа с выделенным решением (доп. функция)."""

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def draw(graph, highlight=(), title="", path="graph.png"):
    """Сохранить изображение графа в файл PNG.

    highlight — последовательность рёбер (u, v), которые выделяются цветом.
    """
    n = graph.n
    pos = [(math.cos(2 * math.pi * i / n + math.pi / 2),
            math.sin(2 * math.pi * i / n + math.pi / 2)) for i in range(n)]
    marked = {frozenset(e[:2]) for e in highlight}
    fig, ax = plt.subplots(figsize=(6, 6))
    for u, v, wt in graph.edges():
        on = frozenset((u, v)) in marked
        (x1, y1), (x2, y2) = pos[u], pos[v]
        ax.plot([x1, x2], [y1, y2], color="#c0392b" if on else "#b0b0b0",
                lw=3 if on else 1, zorder=1)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"{wt:g}", fontsize=9,
                ha="center", va="center", zorder=3,
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec="#c0392b" if on else "none", lw=0.8))
    for i, (x, y) in enumerate(pos):
        ax.scatter([x], [y], s=520, color="#2c5d8f", zorder=2)
        ax.text(x, y, graph.names[i], color="white", ha="center", va="center",
                fontsize=11, fontweight="bold", zorder=4)
    ax.set_title(title, fontsize=12)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def path_edges(vertices):
    """Преобразовать последовательность вершин в список рёбер."""
    return [(vertices[i], vertices[i + 1]) for i in range(len(vertices) - 1)]
