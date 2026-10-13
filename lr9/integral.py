"""ЛР 9 «Отладка и тестирование ПС», вариант 3.

Вычисление определённого интеграла  z = ∫[a; b] (ln x)^3 / x dx
методом трапеций с точностью eps. Точность контролируется правилом Рунге:
число разбиений удваивается, пока |I(2n) - I(n)| / 3 >= eps.

Аналитическое значение для проверки: ((ln b)^4 - (ln a)^4) / 4.

Запуск:  python integral.py a b eps [рисунок.png]
"""

import math
import sys

N_START = 4                 # начальное число отрезков разбиения
N_MAX = 2 ** 24             # предел числа отрезков (защита от зацикливания)
EPS_MIN = 1e-12             # минимально допустимая точность
LIMIT_MAX = 1e100           # предел модуля пределов интегрирования


class IntegralError(ValueError):
    """Неверные исходные данные."""


class ConvergenceError(ArithmeticError):
    """Требуемая точность не достигнута за допустимое число шагов."""


def f(x):
    """Подынтегральная функция (ln x)^3 / x, определена при x > 0."""
    if x <= 0:
        raise IntegralError(f"функция не определена при x = {x:g} (нужно x > 0)")
    return math.log(x) ** 3 / x


def exact(a, b):
    """Первообразная (ln x)^4 / 4 — точное значение для проверки."""
    return (math.log(b) ** 4 - math.log(a) ** 4) / 4


def trapezoid(func, a, b, n):
    """Составная формула трапеций на n равных отрезках."""
    h = (b - a) / n
    total = (func(a) + func(b)) / 2
    for i in range(1, n):
        total += func(a + i * h)
    return total * h


def check_input(a, b, eps):
    """Проверка исходных данных; возбуждает IntegralError с пояснением."""
    for name, value in (("a", a), ("b", b), ("eps", eps)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise IntegralError(f"{name} должно быть числом")
        if not math.isfinite(value):
            raise IntegralError(f"{name} должно быть конечным числом")
    if a <= 0 or b <= 0:
        raise IntegralError("пределы интегрирования должны быть > 0 "
                            "(ln x не определён при x <= 0)")
    if a > LIMIT_MAX or b > LIMIT_MAX:
        raise IntegralError(f"пределы не должны превышать {LIMIT_MAX:g}")
    if not EPS_MIN <= eps < 1:
        raise IntegralError(f"точность eps должна быть в интервале [{EPS_MIN:g}; 1)")


def integrate(a, b, eps, func=f):
    """Интеграл методом трапеций с точностью eps.

    Возвращает (значение, число отрезков, оценка погрешности по Рунге).
    Если a > b, результат берётся с обратным знаком.
    """
    check_input(a, b, eps)
    if a == b:
        return 0.0, 0, 0.0
    n = N_START
    previous = trapezoid(func, a, b, n)
    while True:
        n *= 2
        if n > N_MAX:
            raise ConvergenceError(
                f"точность {eps:g} не достигнута при {N_MAX} отрезках")
        current = trapezoid(func, a, b, n)
        error = abs(current - previous) / 3
        if error < eps:
            return current, n, error
        previous = current


def parse_number(text, name):
    try:
        return float(text.replace(",", "."))
    except ValueError:
        raise IntegralError(f"{name} = «{text}» не является числом") from None


def plot(a, b, value, n_show=8, path="integral.png"):
    """Графическая интерпретация: кривая, площадь и n_show трапеций."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    lo, hi = min(a, b), max(a, b)
    xs = [lo + (hi - lo) * i / 400 for i in range(401)]
    ys = [f(x) for x in xs]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.fill_between(xs, ys, color="#2c5d8f", alpha=0.18, label="площадь = интеграл")
    ax.plot(xs, ys, color="#2c5d8f", lw=2, label=r"$y=(\ln x)^3/x$")
    h = (hi - lo) / n_show
    for i in range(n_show):
        x0, x1 = lo + i * h, lo + (i + 1) * h
        ax.plot([x0, x0, x1, x1], [0, f(x0), f(x1), 0], color="#c0392b", lw=1)
    ax.plot([], [], color="#c0392b", lw=1, label=f"трапеции (n = {n_show})")
    ax.axhline(0, color="black", lw=0.7)
    ax.set_title(f"∫ от {a:g} до {b:g} (ln x)³/x dx ≈ {value:.6f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def main(argv):
    if len(argv) not in (4, 5):
        print(__doc__)
        return 1
    try:
        a = parse_number(argv[1], "a")
        b = parse_number(argv[2], "b")
        eps = parse_number(argv[3], "eps")
        value, n, error = integrate(a, b, eps)
    except (IntegralError, ConvergenceError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2
    print(f"Интеграл (ln x)^3/x от {a:g} до {b:g}")
    print(f"  метод трапеций : {value:.10f}")
    print(f"  отрезков n     : {n}")
    print(f"  оценка Рунге   : {error:.2e} (eps = {eps:g})")
    print(f"  точное значение: {exact(a, b):.10f}")
    print(f"  факт. ошибка   : {abs(value - exact(a, b)):.2e}")
    if len(argv) == 5 and a != b:
        print(f"  рисунок        : {plot(a, b, value, path=argv[4])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
