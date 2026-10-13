"""ЛР 6, вариант 3. Нахождение n-го элемента последовательности Фибоначчи
1, 1, 2, 3, 5, 8, 13, ...  (F(1) = F(2) = 1, F(n) = F(n-1) + F(n-2)).

Программа демонстрирует критерии и примитивы качества ПС:
  устойчивость    — проверка любого ввода, программа не «падает»;
  точность        — длинная арифметика Python, результат точный;
  эффективность   — метод быстрого удвоения, O(log n) операций;
  защищённость    — ограничение MAX_N против исчерпания памяти/времени;
  информативность — справка, сообщения об ошибках, время счёта;
  модульность     — вычисление, проверка ввода и диалог разделены.

Запуск:  python fibonacci.py          (диалоговый режим)
         python fibonacci.py 100      (один ответ)
"""

import sys
import time

MAX_N = 1_000_000            # верхняя граница номера элемента
SHOW_DIGITS = 60             # сколько цифр длинного числа показывать

# F(MAX_N) содержит ~209 тыс. цифр; снимаем ограничение Python на
# перевод длинных чисел в строку (по умолчанию 4300 цифр).
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


class InputError(ValueError):
    """Неверные исходные данные."""


# ---------------------- вычислительная часть ----------------------
def fib_iterative(n):
    """F(n) простым циклом, O(n). Используется для проверки."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _fib_pair(n):
    """Возвращает (F(n), F(n+1)) методом быстрого удвоения.

    F(2k)   = F(k) * (2*F(k+1) - F(k))
    F(2k+1) = F(k)^2 + F(k+1)^2
    """
    a, b = 0, 1
    for bit in bin(n)[2:]:              # проход по битам n от старшего
        c = a * (2 * b - a)             # F(2k)
        d = a * a + b * b               # F(2k+1)
        if bit == "1":
            a, b = d, c + d
        else:
            a, b = c, d
    return a, b


def check_n(n):
    """Проверка допустимости номера элемента (возбуждает InputError)."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise InputError("номер элемента должен быть целым числом")
    if n < 1:
        raise InputError("номер элемента должен быть не меньше 1")
    if n > MAX_N:
        raise InputError(f"номер элемента не должен превышать {MAX_N}")


def fibonacci(n):
    """n-й элемент последовательности, n — целое от 1 до MAX_N."""
    check_n(n)
    return _fib_pair(n)[0]


# ---------------------- проверка ввода ----------------------
def parse_n(text):
    """Преобразовать строку пользователя в номер элемента."""
    text = text.strip().replace(" ", "")
    if not text:
        raise InputError("введена пустая строка")
    try:
        value = float(text.replace(",", "."))
    except ValueError:
        raise InputError(f"«{text}» не является числом") from None
    if not value.is_integer():
        raise InputError("номер элемента должен быть целым")
    if abs(value) > 10 * MAX_N:
        raise InputError(f"номер элемента не должен превышать {MAX_N}")
    n = int(value)
    check_n(n)
    return n


# ---------------------- вывод ----------------------
def format_number(value):
    """Короткая запись длинного числа: начало...конец (всего цифр)."""
    digits = str(value)
    if len(digits) <= SHOW_DIGITS:
        return digits
    half = SHOW_DIGITS // 2
    return f"{digits[:half]}...{digits[-half:]}  (всего цифр: {len(digits)})"


def describe(n):
    """Строка ответа для номера n с замером времени."""
    start = time.perf_counter()
    value = fibonacci(n)
    elapsed = (time.perf_counter() - start) * 1000
    return f"F({n}) = {format_number(value)}\nвремя вычисления: {elapsed:.3f} мс"


HELP = f"""Программа находит n-й элемент последовательности Фибоначчи
1, 1, 2, 3, 5, 8, 13, ... (каждый следующий равен сумме двух предыдущих).
Введите номер n — целое число от 1 до {MAX_N}.
Команды:  ? — справка,  0 или q — выход."""


def dialog(read=input, write=print):
    """Диалоговый режим. read/write подменяются при тестировании."""
    write(HELP)
    while True:
        try:
            text = read("\nn = ")
        except EOFError:
            text = "q"
        if text.strip().lower() in ("0", "q", "выход"):
            write("Работа завершена.")
            return
        if text.strip() == "?":
            write(HELP)
            continue
        try:
            write(describe(parse_n(text)))
        except InputError as exc:
            write(f"Ошибка ввода: {exc}. Повторите (? — справка).")


def main(argv):
    if len(argv) > 1:
        try:
            print(describe(parse_n(argv[1])))
            return 0
        except InputError as exc:
            print(f"Ошибка: {exc}", file=sys.stderr)
            return 2
    dialog()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
