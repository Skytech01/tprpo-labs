"""Модуль tsp — задача коммивояжёра (цикл минимальной длины).

held_karp         — точный метод динамического программирования,
                    O(n^2 * 2^n), применяется при n <= EXACT_LIMIT;
nearest_neighbor  — жадная эвристика «ближайший сосед»;
two_opt           — улучшение маршрута перестановкой 2-opt;
solve_tsp         — выбор метода по размеру задачи.
"""

from .graph import INF, GraphError

EXACT_LIMIT = 15


def tour_length(graph, tour):
    """Длина замкнутого маршрута (последняя вершина = первая)."""
    return sum(graph.weight(tour[i], tour[i + 1]) for i in range(len(tour) - 1))


def held_karp(graph, start=0):
    """Точное решение. Возвращает (длина, маршрут) или GraphError."""
    n = graph.n
    if n > EXACT_LIMIT:
        raise GraphError(f"Точный метод допускает не более {EXACT_LIMIT} вершин")
    others = [v for v in range(n) if v != start]
    index = {v: i for i, v in enumerate(others)}
    full = 1 << len(others)
    # dp[mask][i] — длина пути start → ... → others[i] через множество mask
    dp = [[INF] * len(others) for _ in range(full)]
    parent = [[None] * len(others) for _ in range(full)]
    for v in others:
        i = index[v]
        dp[1 << i][i] = graph.weight(start, v)
    for mask in range(1, full):
        for i, v in enumerate(others):
            cur = dp[mask][i]
            if cur == INF or not mask & (1 << i):
                continue
            for j, u in enumerate(others):
                if mask & (1 << j):
                    continue
                wt = graph.weight(v, u)
                if wt == INF:
                    continue
                nmask = mask | (1 << j)
                if cur + wt < dp[nmask][j]:
                    dp[nmask][j] = cur + wt
                    parent[nmask][j] = i
    best, last = INF, None
    for i, v in enumerate(others):
        total = dp[full - 1][i] + graph.weight(v, start)
        if total < best:
            best, last = total, i
    if best == INF:
        raise GraphError("Гамильтонова цикла не существует")
    tour, mask, i = [], full - 1, last
    while i is not None:
        tour.append(others[i])
        prev_i = parent[mask][i]
        mask ^= 1 << i
        i = prev_i
    tour = [start] + tour[::-1] + [start]
    return best, tour


def nearest_neighbor(graph, start=0):
    """Жадный маршрут; может не найти цикл в неполном графе."""
    tour = [start]
    visited = {start}
    while len(tour) < graph.n:
        cur = tour[-1]
        options = [(wt, v) for v, wt in graph.neighbors(cur) if v not in visited]
        if not options:
            raise GraphError("Эвристика зашла в тупик: граф не полный")
        _, nxt = min(options)
        tour.append(nxt)
        visited.add(nxt)
    if not graph.has_edge(tour[-1], start):
        raise GraphError("Эвристика не смогла замкнуть цикл")
    tour.append(start)
    return tour_length(graph, tour), tour


def two_opt(graph, tour):
    """Улучшение маршрута 2-opt до локального минимума."""
    best = tour[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if tour_length(graph, candidate) < tour_length(graph, best):
                    best = candidate
                    improved = True
    return tour_length(graph, best), best


def solve_tsp(graph, start=0, method="auto"):
    """Решить задачу коммивояжёра.

    method: "exact" — точный, "heuristic" — эвристика + 2-opt,
            "auto" — точный при n <= EXACT_LIMIT, иначе эвристика.
    Возвращает (длина, маршрут, название метода).
    """
    if graph.directed:
        raise GraphError("Реализован симметричный вариант задачи коммивояжёра")
    graph._check_vertex(start)
    if method not in ("auto", "exact", "heuristic"):
        raise GraphError(f"Неизвестный метод: {method}")
    if method == "exact" or (method == "auto" and graph.n <= EXACT_LIMIT):
        length, tour = held_karp(graph, start)
        return length, tour, "точный (Хелд–Карп)"
    _, tour = nearest_neighbor(graph, start)
    length, tour = two_opt(graph, tour)
    return length, tour, "эвристика (ближайший сосед + 2-opt)"
