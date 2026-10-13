"""Модуль shortest_path — поиск кратчайших путей.

dijkstra        — алгоритм Дейкстры (от одной вершины);
restore_path    — восстановление пути по массиву предков;
floyd_warshall  — алгоритм Флойда–Уоршелла (все пары, доп. функция).
"""

import heapq

from .graph import INF, GraphError


def dijkstra(graph, source):
    """Кратчайшие расстояния от source до всех вершин.

    Возвращает (dist, prev): dist[v] — длина пути, prev[v] — предок v.
    """
    graph._check_vertex(source)
    dist = [INF] * graph.n
    prev = [None] * graph.n
    dist[source] = 0
    heap = [(0, source)]
    done = [False] * graph.n
    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:
            continue
        done[u] = True
        for v, wt in graph.neighbors(u):
            if d + wt < dist[v]:
                dist[v] = d + wt
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, prev


def restore_path(prev, source, target):
    """Список вершин пути source → target или [] если пути нет."""
    if source == target:
        return [source]
    if prev[target] is None:
        return []
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return path


def shortest_path(graph, source, target):
    """Кратчайший путь между двумя вершинами: (длина, список вершин)."""
    graph._check_vertex(target)
    dist, prev = dijkstra(graph, source)
    if dist[target] == INF:
        raise GraphError(
            f"Вершина {graph.names[target]} недостижима из {graph.names[source]}")
    return dist[target], restore_path(prev, source, target)


def floyd_warshall(graph):
    """Матрица кратчайших расстояний между всеми парами вершин."""
    n = graph.n
    d = [row[:] for row in graph.w]
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF:
                continue
            di = d[i]
            for j in range(n):
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return d
