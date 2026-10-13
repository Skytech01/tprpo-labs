"""Модуль mst — минимальное связывающее (остовное) дерево.

prim     — алгоритм Прима, O(n^2), удобен для плотных графов;
kruskal  — алгоритм Краскала с системой непересекающихся множеств
           (дополнительная функция для сравнения результатов).
"""

from .graph import INF, GraphError


def _require_undirected_connected(graph):
    if graph.directed:
        raise GraphError("Остовное дерево строится для неориентированного графа")
    if not graph.is_connected():
        raise GraphError("Граф несвязный: остовного дерева не существует")


def prim(graph, start=0):
    """Возвращает (суммарный вес, список рёбер (u, v, вес))."""
    _require_undirected_connected(graph)
    n = graph.n
    in_tree = [False] * n
    key = [INF] * n
    parent = [None] * n
    key[start] = 0
    edges = []
    for _ in range(n):
        u = min((v for v in range(n) if not in_tree[v]), key=lambda v: key[v])
        in_tree[u] = True
        if parent[u] is not None:
            edges.append((parent[u], u, graph.weight(parent[u], u)))
        for v, wt in graph.neighbors(u):
            if not in_tree[v] and wt < key[v]:
                key[v] = wt
                parent[v] = u
    return sum(e[2] for e in edges), edges


class DisjointSet:
    """Система непересекающихся множеств (union–find)."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal(graph):
    """Возвращает (суммарный вес, список рёбер (u, v, вес))."""
    _require_undirected_connected(graph)
    ds = DisjointSet(graph.n)
    edges = []
    for u, v, wt in sorted(graph.edges(), key=lambda e: e[2]):
        if ds.union(u, v):
            edges.append((u, v, wt))
            if len(edges) == graph.n - 1:
                break
    return sum(e[2] for e in edges), edges
