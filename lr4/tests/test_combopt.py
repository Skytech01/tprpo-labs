"""Тесты пакета combopt.  Запуск:  python -m unittest discover -s tests"""

import itertools
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from combopt import mst, shortest_path, tsp  # noqa: E402
from combopt.graph import INF, Graph, GraphError  # noqa: E402

# Пример из пояснительной записки: 5 городов
SAMPLE = [
    [0, 12, 10, 19, 8],
    [12, 0, 3, 7, 2],
    [10, 3, 0, 6, 20],
    [19, 7, 6, 0, 4],
    [8, 2, 20, 4, 0],
]


def brute_force_tsp(g):
    best = INF
    for perm in itertools.permutations(range(1, g.n)):
        tour = (0,) + perm + (0,)
        best = min(best, tsp.tour_length(g, tour))
    return best


class TestGraph(unittest.TestCase):
    def test_bad_size(self):
        for n in (0, 1, 51, "5"):
            with self.assertRaises(GraphError):
                Graph(n)

    def test_bad_edges(self):
        g = Graph(3)
        with self.assertRaises(GraphError):
            g.add_edge(0, 0, 1)          # петля
        with self.assertRaises(GraphError):
            g.add_edge(0, 1, -5)         # отрицательный вес
        with self.assertRaises(GraphError):
            g.add_edge(0, 7, 1)          # нет вершины

    def test_asymmetric_matrix(self):
        with self.assertRaises(GraphError):
            Graph.from_matrix([[0, 1], [2, 0]])

    def test_save_load(self):
        g = Graph.from_matrix(SAMPLE)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "g.json")
            g.save(path)
            h = Graph.load(path)
        self.assertEqual(g.w, h.w)

    def test_load_broken_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("это не json")
        try:
            with self.assertRaises(GraphError):
                Graph.load(fh.name)
        finally:
            os.remove(fh.name)
        with self.assertRaises(GraphError):
            Graph.load("нет_такого_файла.json")


class TestTSP(unittest.TestCase):
    def test_sample(self):
        length, tour, _ = tsp.solve_tsp(Graph.from_matrix(SAMPLE))
        self.assertEqual(length, 32)   # проверено полным перебором
        self.assertEqual(tour[0], tour[-1])
        self.assertEqual(sorted(tour[:-1]), list(range(5)))

    def test_against_brute_force(self):
        for seed in range(20):
            g = Graph.random(7, complete=True, seed=seed)
            length, _ = tsp.held_karp(g)
            self.assertEqual(length, brute_force_tsp(g), f"seed={seed}")

    def test_heuristic_not_better_than_exact(self):
        for seed in range(10):
            g = Graph.random(9, complete=True, seed=seed)
            exact, _, _ = tsp.solve_tsp(g, method="exact")
            approx, tour, _ = tsp.solve_tsp(g, method="heuristic")
            self.assertGreaterEqual(approx, exact)
            self.assertEqual(approx, tsp.tour_length(g, tour))

    def test_no_cycle(self):
        g = Graph.from_matrix([[0, 1, 0, 0], [1, 0, 1, 0],
                               [0, 1, 0, 1], [0, 0, 1, 0]])   # цепь
        with self.assertRaises(GraphError):
            tsp.held_karp(g)

    def test_large_uses_heuristic(self):
        g = Graph.random(20, complete=True, seed=1)
        _, tour, method = tsp.solve_tsp(g)
        self.assertIn("эвристика", method)
        self.assertEqual(len(tour), 21)


class TestShortestPath(unittest.TestCase):
    def test_sample(self):
        g = Graph.from_matrix(SAMPLE)
        length, path = shortest_path.shortest_path(g, 0, 3)
        self.assertEqual(length, 12)
        self.assertEqual(path, [0, 4, 3])

    def test_dijkstra_equals_floyd(self):
        for seed in range(10):
            g = Graph.random(12, density=0.3, seed=seed)
            fw = shortest_path.floyd_warshall(g)
            for s in range(g.n):
                dist, _ = shortest_path.dijkstra(g, s)
                self.assertEqual(dist, fw[s])

    def test_unreachable(self):
        g = Graph(3)
        g.add_edge(0, 1, 5)
        with self.assertRaises(GraphError):
            shortest_path.shortest_path(g, 0, 2)

    def test_same_vertex(self):
        g = Graph.from_matrix(SAMPLE)
        self.assertEqual(shortest_path.shortest_path(g, 2, 2), (0, [2]))


class TestMST(unittest.TestCase):
    def test_sample(self):
        total, edges = mst.prim(Graph.from_matrix(SAMPLE))
        self.assertEqual(total, 17)
        self.assertEqual(len(edges), 4)

    def test_prim_equals_kruskal(self):
        for seed in range(20):
            g = Graph.random(15, density=0.4, seed=seed)
            self.assertEqual(mst.prim(g)[0], mst.kruskal(g)[0])

    def test_disconnected(self):
        g = Graph(4)
        g.add_edge(0, 1, 1)
        g.add_edge(2, 3, 1)
        with self.assertRaises(GraphError):
            mst.prim(g)


class TestConsole(unittest.TestCase):
    def test_dialog_with_wrong_input(self):
        from combopt.ui import Console
        answers = iter(["abc", "1", "5", "1 2 12", "1 2", "1 9 4", "",
                        "8", "н", "0"])
        out = []
        Console(lambda _: next(answers), out.append).run()
        text = "\n".join(out)
        self.assertIn("Ошибка: нужно целое число", text)
        self.assertIn("Ребро не добавлено", text)
        self.assertIn("Граф несвязный", text)
        self.assertIn("Работа завершена", text)


if __name__ == "__main__":
    unittest.main()
