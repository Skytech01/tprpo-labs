"""Тесты к ЛР 9: нормальные, экстремальные и исключительные ситуации.

Запуск:  python -m unittest test_integral -v
Таблица результатов для отчёта:  python test_integral.py --table
"""

import json
import math
import sys
import time
import unittest

import integral as I

E = math.e

# (номер, вид, описание, a, b, eps, ожидаемый результат)
# ожидаемый результат: число (точное значение) или класс исключения
CASES = [
    ("Н1", "нормальная", "типовой отрезок [1; e]", 1, E, 1e-6, 0.25),
    ("Н2", "нормальная", "отрезок [1; 10]", 1, 10, 1e-4, I.exact(1, 10)),
    ("Н3", "нормальная", "a < 1 < b, симметрично по ln x", 0.5, 2, 1e-6, 0.0),
    ("Н4", "нормальная", "a > b (обратный порядок)", 2, 1, 1e-6, I.exact(2, 1)),
    ("Н5", "нормальная", "отрезок левее 1 (функция < 0)", 0.1, 0.9, 1e-5, I.exact(0.1, 0.9)),
    ("Э1", "экстремальная", "нулевая длина a = b", 3, 3, 1e-6, 0.0),
    ("Э2", "экстремальная", "минимальная точность eps = 1e-12", 1, E, 1e-12, 0.25),
    ("Э3", "экстремальная", "грубая точность eps = 0,999", 1, E, 0.999, 0.25),
    ("Э4", "экстремальная", "очень длинный отрезок [1; 1e6]", 1, 1e6, 1e-3, I.exact(1, 1e6)),
    ("Э5", "экстремальная", "a близко к 0 (a = 0,001)", 1e-3, 1, 1e-3, I.exact(1e-3, 1)),
    ("Э6", "экстремальная", "a очень близко к 0 (a = 1e-6)", 1e-6, 1, 1e-3, I.ConvergenceError),
    ("Э7", "экстремальная", "очень короткий отрезок [1; 1+1e-9]", 1, 1 + 1e-9, 1e-6,
     I.exact(1, 1 + 1e-9)),
    ("И1", "исключительная", "a = 0", 0, 1, 1e-6, I.IntegralError),
    ("И2", "исключительная", "a < 0", -1, 2, 1e-6, I.IntegralError),
    ("И3", "исключительная", "eps = 0", 1, 2, 0, I.IntegralError),
    ("И4", "исключительная", "eps < 0", 1, 2, -0.1, I.IntegralError),
    ("И5", "исключительная", "eps = 1", 1, 2, 1, I.IntegralError),
    ("И6", "исключительная", "b = бесконечность", 1, math.inf, 1e-3, I.IntegralError),
    ("И7", "исключительная", "a = NaN", math.nan, 2, 1e-3, I.IntegralError),
    ("И8", "исключительная", "b = 1e200 (вне допустимого)", 1, 1e200, 1e-3, I.IntegralError),
    ("И9", "исключительная", "a задано строкой", "1", 2, 1e-3, I.IntegralError),
]


def run_case(case):
    """Выполнить тест; вернуть (результат-строка, пройден ли, время, n)."""
    _, _, _, a, b, eps, expected = case
    start = time.perf_counter()
    try:
        value, n, _ = I.integrate(a, b, eps)
    except (I.IntegralError, I.ConvergenceError) as exc:
        elapsed = time.perf_counter() - start
        ok = isinstance(expected, type) and isinstance(exc, expected)
        return f"{type(exc).__name__}: {exc}", ok, elapsed, None
    elapsed = time.perf_counter() - start
    if isinstance(expected, type):
        return f"{value:.10g}", False, elapsed, n
    # Требование: фактическая ошибка не больше eps
    ok = abs(value - expected) <= eps
    return f"{value:.10g}", ok, elapsed, n


class TestCases(unittest.TestCase):
    def test_all_cases(self):
        for case in CASES:
            with self.subTest(case[0]):
                result, ok, _, _ = run_case(case)
                self.assertTrue(ok, f"{case[0]} {case[2]}: {result}")


class TestUnits(unittest.TestCase):
    def test_function_values(self):
        self.assertEqual(I.f(1), 0)
        self.assertAlmostEqual(I.f(E), 1 / E)

    def test_trapezoid_exact_on_line(self):
        # формула трапеций точна для линейной функции
        self.assertAlmostEqual(I.trapezoid(lambda x: 2 * x + 1, 0, 3, 4), 12)

    def test_trapezoid_order(self):
        # ошибка убывает примерно в 4 раза при удвоении n
        e1 = abs(I.trapezoid(I.f, 1, E, 16) - 0.25)
        e2 = abs(I.trapezoid(I.f, 1, E, 32) - 0.25)
        self.assertAlmostEqual(e1 / e2, 4, delta=0.2)

    def test_parse_number(self):
        self.assertEqual(I.parse_number("2,5", "a"), 2.5)
        with self.assertRaises(I.IntegralError):
            I.parse_number("abc", "a")

    def test_main_return_codes(self):
        self.assertEqual(I.main(["p", "1", "2", "1e-6"]), 0)
        self.assertEqual(I.main(["p", "0", "2", "1e-6"]), 2)
        self.assertEqual(I.main(["p", "x", "2", "1e-6"]), 2)
        self.assertEqual(I.main(["p"]), 1)


def write_table(path="test_results.json"):
    rows = []
    for case in CASES:
        result, ok, elapsed, n = run_case(case)
        num, kind, descr, a, b, eps, expected = case
        exp_text = expected.__name__ if isinstance(expected, type) else f"{expected:.10g}"
        rows.append({"num": num, "kind": kind, "descr": descr,
                     "input": f"a={a!r}, b={b!r}, eps={eps:g}"
                              if not isinstance(eps, str) else "",
                     "expected": exp_text, "result": result, "n": n,
                     "time": round(elapsed, 3), "ok": ok})
        print(f"{num:3} {'OK ' if ok else 'FAIL'} {elapsed:7.3f}s  {result}")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    if "--table" in sys.argv:
        write_table()
    else:
        unittest.main()
