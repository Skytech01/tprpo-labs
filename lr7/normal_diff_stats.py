"""ЛР 7 «Стиль программирования», вариант 3.

Задание: сгенерировать последовательность 100 случайных чисел с нормальным
законом распределения (mx = 1, dx = 1); упорядочить её по возрастанию;
образовать новую последовательность из разностей соседних элементов
X(i) - X(i-1); для неё вычислить среднее значение и дисперсию и вывести
гистограмму, разбив диапазон на 10 интервалов.

Нормальные числа получаются по центральной предельной теореме из суммы
K_UNIFORM равномерных на [0, 1) чисел (формула из справочного материала):
    z = (sum(x_i) - K/2) * sqrt(dx) / sqrt(K/12) + mx,
при K = 12 знаменатель равен 1.

Запуск:  python normal_diff_stats.py [зерно_генератора]
"""

import math
import random
import sys

# ---------- параметры задания ----------
SAMPLE_SIZE = 100          # объём исходной последовательности
MEAN_X = 1.0               # математическое ожидание mx
VARIANCE_X = 1.0           # дисперсия dx
INTERVAL_COUNT = 10        # число интервалов гистограммы
K_UNIFORM = 12             # слагаемых в сумме по ЦПТ
BAR_WIDTH = 50             # длина самого высокого столбца, символов


def generate_normal(count, mean, variance, rng):
    """Вернуть список из count нормально распределённых чисел."""
    sigma = math.sqrt(variance)
    scale = sigma / math.sqrt(K_UNIFORM / 12)
    numbers = []
    for _ in range(count):
        uniform_sum = sum(rng.random() for _ in range(K_UNIFORM))
        numbers.append((uniform_sum - K_UNIFORM / 2) * scale + mean)
    return numbers


def neighbour_differences(values):
    """Разности соседних элементов: values[i] - values[i-1], i = 1..n-1."""
    return [values[i] - values[i - 1] for i in range(1, len(values))]


def mean_value(values):
    """Математическое ожидание m = (1/k) * sum(x_i)."""
    return sum(values) / len(values)


def variance_value(values):
    """Дисперсия d = (1/k) * sum(x_i^2 - m^2)."""
    mean = mean_value(values)
    return sum(x * x - mean * mean for x in values) / len(values)


def histogram(values, interval_count):
    """Разбить [min; max] на равные интервалы и посчитать попадания.

    Возвращает список кортежей (левая граница, правая граница, частота).
    Максимальное значение относится к последнему интервалу.
    """
    low, high = min(values), max(values)
    width = (high - low) / interval_count or 1.0
    counts = [0] * interval_count
    for value in values:
        index = min(int((value - low) / width), interval_count - 1)
        counts[index] += 1
    return [(low + i * width, low + (i + 1) * width, counts[i])
            for i in range(interval_count)]


def format_numbers(values, per_line=10):
    """Числа построчно по per_line штук, с выравниванием."""
    lines = []
    for start in range(0, len(values), per_line):
        chunk = values[start:start + per_line]
        lines.append(" ".join(f"{v:7.3f}" for v in chunk))
    return "\n".join(lines)


def format_histogram(bins):
    """Текстовая гистограмма: интервал, частота, столбец из символов #."""
    top = max(count for _, _, count in bins)
    lines = [f"{'интервал':^19} {'частота':>7}"]
    for left, right, count in bins:
        bar = "#" * round(count / top * BAR_WIDTH)
        lines.append(f"[{left:7.3f}; {right:7.3f}) {count:7d}  {bar}")
    return "\n".join(lines)


def print_section(title, body):
    print(f"\n{title}\n{'-' * len(title)}\n{body}")


def main(seed=None):
    rng = random.Random(seed)

    source = generate_normal(SAMPLE_SIZE, MEAN_X, VARIANCE_X, rng)
    ordered = sorted(source)
    differences = neighbour_differences(ordered)

    print_section("Исходная последовательность (N(1; 1))", format_numbers(source))
    print_section("Упорядоченная по возрастанию", format_numbers(ordered))
    print_section("Разности соседних элементов X(i) - X(i-1)",
                  format_numbers(differences))

    print_section("Контроль генератора (исходная выборка)",
                  f"среднее   = {mean_value(source):.4f}  (ожидается {MEAN_X})\n"
                  f"дисперсия = {variance_value(source):.4f}  (ожидается {VARIANCE_X})")

    print_section("Характеристики последовательности разностей",
                  f"количество элементов = {len(differences)}\n"
                  f"среднее значение     = {mean_value(differences):.5f}\n"
                  f"дисперсия            = {variance_value(differences):.6f}")

    print_section("Гистограмма разностей (10 интервалов)",
                  format_histogram(histogram(differences, INTERVAL_COUNT)))
    return differences


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
