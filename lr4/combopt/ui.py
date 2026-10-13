"""Модуль ui — диалог с пользователем (консольное меню).

Модуль отвечает только за ввод/вывод и вызывает вычислительные модули.
Функции ввода повторяют запрос, пока пользователь не введёт верные данные.
"""

import os

from . import mst, shortest_path, tsp, visualize
from .graph import INF, Graph, GraphError

MENU = """
========== Решение комбинаторно-оптимизационных задач ==========
 1. Ввести граф вручную
 2. Сгенерировать случайный граф
 3. Загрузить граф из файла
 4. Сохранить граф в файл
 5. Показать матрицу весов
 6. Задача коммивояжёра (цикл минимальной длины)
 7. Кратчайший путь между двумя вершинами
 8. Минимальное связывающее дерево
 9. Кратчайшие расстояния между всеми парами (Флойд–Уоршелл)
10. Справка
 0. Выход
================================================================"""

HELP = """Справка.
Граф задаётся числом вершин (2..50) и списком рёбер «u v вес».
Вершины нумеруются с 1, вес — неотрицательное число.
Пункт 6 ищет кратчайший замкнутый маршрут, проходящий через все вершины
по одному разу: при n <= 15 точно (Хелд–Карп), иначе приближённо.
Пункт 7 — алгоритм Дейкстры, пункт 8 — алгоритмы Прима и Краскала.
Результат можно сохранить как рисунок PNG."""


class Console:
    """Консольный интерфейс. input_fn/print_fn подменяются в тестах."""

    def __init__(self, input_fn=input, print_fn=print):
        self.ask = input_fn
        self.say = print_fn
        self.graph = None

    # ---------- безопасный ввод ----------
    def ask_int(self, prompt, lo, hi):
        while True:
            text = self.ask(prompt).strip()
            try:
                value = int(text)
            except ValueError:
                self.say(f"  Ошибка: нужно целое число от {lo} до {hi}.")
                continue
            if lo <= value <= hi:
                return value
            self.say(f"  Ошибка: число должно быть от {lo} до {hi}.")

    def ask_yes(self, prompt):
        return self.ask(prompt + " (д/н): ").strip().lower() in ("д", "да", "y", "yes")

    def need_graph(self):
        if self.graph is None:
            self.say("  Сначала задайте граф (пункты 1–3).")
            return False
        return True

    # ---------- действия меню ----------
    def input_graph(self):
        n = self.ask_int("Число вершин (2..50): ", 2, 50)
        g = Graph(n)
        self.say("Вводите рёбра в формате «u v вес», пустая строка — конец ввода.")
        while True:
            line = self.ask("ребро> ").strip()
            if not line:
                break
            parts = line.replace(",", " ").split()
            try:
                if len(parts) != 3:
                    raise GraphError("нужно три значения: u v вес")
                u, v, wt = int(parts[0]) - 1, int(parts[1]) - 1, float(parts[2])
                g.add_edge(u, v, int(wt) if wt.is_integer() else wt)
            except (ValueError, GraphError) as exc:
                self.say(f"  Ребро не добавлено: {exc}")
        self.graph = g
        self.say(f"Граф задан: {g.n} вершин, {len(g.edges())} рёбер.")

    def random_graph(self):
        n = self.ask_int("Число вершин (2..50): ", 2, 50)
        complete = self.ask_yes("Полный граф?")
        self.graph = Graph.random(n, complete=complete)
        self.say(f"Сгенерирован граф: {n} вершин, {len(self.graph.edges())} рёбер.")

    def load_graph(self):
        path = self.ask("Имя файла: ").strip()
        try:
            self.graph = Graph.load(path)
            self.say(f"Загружено: {self.graph.n} вершин, {len(self.graph.edges())} рёбер.")
        except GraphError as exc:
            self.say(f"  Ошибка загрузки: {exc}")

    def save_graph(self):
        if not self.need_graph():
            return
        path = self.ask("Имя файла: ").strip()
        try:
            self.graph.save(path)
            self.say(f"Граф сохранён в {os.path.abspath(path)}")
        except OSError as exc:
            self.say(f"  Ошибка записи: {exc.strerror}")

    def show_matrix(self):
        if self.need_graph():
            self.say(self.graph.matrix_text())

    def run_tsp(self):
        if not self.need_graph():
            return
        g = self.graph
        start = self.ask_int(f"Начальная вершина (1..{g.n}): ", 1, g.n) - 1
        try:
            length, tour, method = tsp.solve_tsp(g, start)
        except GraphError as exc:
            self.say(f"  Решение не найдено: {exc}")
            return
        self.say(f"Метод: {method}")
        self.say("Маршрут: " + " -> ".join(g.names[v] for v in tour))
        self.say(f"Длина цикла: {length:g}")
        self.offer_picture(visualize.path_edges(tour), f"Цикл минимальной длины = {length:g}")

    def run_path(self):
        if not self.need_graph():
            return
        g = self.graph
        s = self.ask_int(f"Откуда (1..{g.n}): ", 1, g.n) - 1
        t = self.ask_int(f"Куда (1..{g.n}): ", 1, g.n) - 1
        try:
            length, path = shortest_path.shortest_path(g, s, t)
        except GraphError as exc:
            self.say(f"  {exc}")
            return
        self.say("Путь: " + " -> ".join(g.names[v] for v in path))
        self.say(f"Длина пути: {length:g}")
        self.offer_picture(visualize.path_edges(path), f"Кратчайший путь = {length:g}")

    def run_mst(self):
        if not self.need_graph():
            return
        try:
            total, edges = mst.prim(self.graph)
            total_k, _ = mst.kruskal(self.graph)
        except GraphError as exc:
            self.say(f"  {exc}")
            return
        names = self.graph.names
        self.say("Рёбра дерева (Прим): " +
                 ", ".join(f"{names[u]}-{names[v]}({wt:g})" for u, v, wt in edges))
        self.say(f"Вес дерева: Прим = {total:g}, Краскал = {total_k:g}")
        self.offer_picture(edges, f"Минимальное связывающее дерево = {total:g}")

    def run_floyd(self):
        if not self.need_graph():
            return
        g = self.graph
        d = shortest_path.floyd_warshall(g)
        self.say("Матрица кратчайших расстояний:")
        head = "     " + "".join(f"{nm:>6}" for nm in g.names)
        self.say(head)
        for i in range(g.n):
            row = "".join(f"{'-' if x == INF else f'{x:g}':>6}" for x in d[i])
            self.say(f"{g.names[i]:>5}{row}")

    def offer_picture(self, edges, title):
        if self.ask_yes("Сохранить рисунок?"):
            path = self.ask("Имя файла PNG: ").strip() or "result.png"
            visualize.draw(self.graph, edges, title, path)
            self.say(f"Рисунок сохранён: {path}")

    # ---------- главный цикл ----------
    def run(self):
        actions = {
            1: self.input_graph, 2: self.random_graph, 3: self.load_graph,
            4: self.save_graph, 5: self.show_matrix, 6: self.run_tsp,
            7: self.run_path, 8: self.run_mst, 9: self.run_floyd,
            10: lambda: self.say(HELP),
        }
        while True:
            self.say(MENU)
            choice = self.ask_int("Выберите пункт: ", 0, 10)
            if choice == 0:
                self.say("Работа завершена.")
                return
            actions[choice]()
