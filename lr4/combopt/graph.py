"""Модуль graph — представление взвешенного графа.

Граф хранится в виде матрицы весов. Отсутствие ребра обозначается
значением INF. Модуль не зависит от остальных модулей пакета.
"""

import json
import math
import random

INF = math.inf
MAX_VERTICES = 50          # ограничение на размер графа
MAX_WEIGHT = 1_000_000     # ограничение на вес ребра


class GraphError(ValueError):
    """Ошибка в исходных данных графа."""


class Graph:
    """Взвешенный граф на матрице весов.

    Вершины нумеруются с 0; пользователю показываются с 1.
    """

    def __init__(self, n, directed=False, names=None):
        if not isinstance(n, int) or not 2 <= n <= MAX_VERTICES:
            raise GraphError(
                f"Число вершин должно быть целым от 2 до {MAX_VERTICES}")
        self.n = n
        self.directed = directed
        self.names = list(names) if names else [str(i + 1) for i in range(n)]
        if len(self.names) != n:
            raise GraphError("Количество имён вершин не совпадает с n")
        self.w = [[0 if i == j else INF for j in range(n)] for i in range(n)]

    # ---------- изменение и чтение ----------
    def _check_vertex(self, v):
        if not isinstance(v, int) or not 0 <= v < self.n:
            raise GraphError(f"Нет вершины с номером {v + 1 if isinstance(v, int) else v}")

    def add_edge(self, u, v, weight):
        """Добавить (или заменить) ребро u–v с весом weight."""
        self._check_vertex(u)
        self._check_vertex(v)
        if u == v:
            raise GraphError("Петли не допускаются")
        if not isinstance(weight, (int, float)) or math.isnan(weight):
            raise GraphError("Вес ребра должен быть числом")
        if weight < 0:
            raise GraphError("Вес ребра не может быть отрицательным")
        if weight > MAX_WEIGHT:
            raise GraphError(f"Вес ребра не должен превышать {MAX_WEIGHT}")
        self.w[u][v] = weight
        if not self.directed:
            self.w[v][u] = weight

    def remove_edge(self, u, v):
        """Удалить ребро u–v."""
        self._check_vertex(u)
        self._check_vertex(v)
        self.w[u][v] = INF
        if not self.directed:
            self.w[v][u] = INF

    def weight(self, u, v):
        return self.w[u][v]

    def has_edge(self, u, v):
        return u != v and self.w[u][v] != INF

    def neighbors(self, u):
        """Список пар (v, вес) для соседей вершины u."""
        return [(v, self.w[u][v]) for v in range(self.n) if self.has_edge(u, v)]

    def edges(self):
        """Список рёбер (u, v, вес); для неориентированного — без повторов."""
        result = []
        for u in range(self.n):
            start = 0 if self.directed else u + 1
            for v in range(start, self.n):
                if self.has_edge(u, v):
                    result.append((u, v, self.w[u][v]))
        return result

    def is_connected(self):
        """Проверка связности (для орграфа — слабой связности)."""
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v in range(self.n):
                linked = self.has_edge(u, v) or self.has_edge(v, u)
                if linked and v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen) == self.n

    # ---------- создание ----------
    @classmethod
    def from_matrix(cls, matrix, directed=False, names=None):
        """Создать граф по матрице; 0 или None вне диагонали — нет ребра."""
        n = len(matrix)
        if any(len(row) != n for row in matrix):
            raise GraphError("Матрица весов должна быть квадратной")
        g = cls(n, directed, names)
        for i in range(n):
            for j in range(n):
                value = matrix[i][j]
                if i != j and value not in (0, None) and value != INF:
                    if not directed and j < i:
                        if matrix[j][i] != value:
                            raise GraphError(
                                f"Матрица несимметрична: ({j+1},{i+1}) и ({i+1},{j+1})")
                        continue
                    g.add_edge(i, j, value)
        return g

    @classmethod
    def random(cls, n, density=0.6, w_min=1, w_max=100, seed=None, complete=False):
        """Случайный связный граф (дополнительная функция)."""
        if not 0 < density <= 1:
            raise GraphError("Плотность должна быть в интервале (0; 1]")
        if not 0 <= w_min <= w_max <= MAX_WEIGHT:
            raise GraphError("Неверный диапазон весов")
        rnd = random.Random(seed)
        g = cls(n)
        order = list(range(n))
        rnd.shuffle(order)
        for i in range(1, n):                       # остов — гарантия связности
            g.add_edge(order[i], order[rnd.randrange(i)], rnd.randint(w_min, w_max))
        for u in range(n):
            for v in range(u + 1, n):
                if not g.has_edge(u, v) and (complete or rnd.random() < density):
                    g.add_edge(u, v, rnd.randint(w_min, w_max))
        return g

    # ---------- файлы ----------
    def to_dict(self):
        return {
            "n": self.n,
            "directed": self.directed,
            "names": self.names,
            "edges": [[u + 1, v + 1, wt] for u, v, wt in self.edges()],
        }

    @classmethod
    def from_dict(cls, data):
        try:
            g = cls(int(data["n"]), bool(data.get("directed", False)), data.get("names"))
            for u, v, wt in data["edges"]:
                g.add_edge(int(u) - 1, int(v) - 1, float(wt) if "." in str(wt) else int(wt))
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, GraphError):
                raise
            raise GraphError(f"Неверный формат файла графа: {exc}") from exc
        return g

    def save(self, path):
        """Сохранить граф в файл JSON."""
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path):
        """Загрузить граф из файла JSON."""
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except OSError as exc:
            raise GraphError(f"Не удалось открыть файл: {exc.strerror}") from exc
        except json.JSONDecodeError as exc:
            raise GraphError("Файл повреждён: это не JSON") from exc
        return cls.from_dict(data)

    def matrix_text(self):
        """Матрица весов в текстовом виде для вывода на экран."""
        width = max(4, max(len(n) for n in self.names) + 1)
        lines = [" " * width + "".join(f"{nm:>{width}}" for nm in self.names)]
        for i in range(self.n):
            cells = []
            for j in range(self.n):
                value = self.w[i][j]
                cells.append(f"{'-' if value == INF else _fmt(value):>{width}}")
            lines.append(f"{self.names[i]:>{width}}" + "".join(cells))
        return "\n".join(lines)


def _fmt(value):
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}"
