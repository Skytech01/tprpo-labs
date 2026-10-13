"""Тесты к ЛР 6.  Запуск:  python -m unittest test_fibonacci -v"""

import unittest

from fibonacci import (MAX_N, InputError, dialog, fib_iterative, fibonacci,
                       format_number, parse_n)


class TestFibonacci(unittest.TestCase):
    def test_first_elements(self):
        self.assertEqual([fibonacci(n) for n in range(1, 11)],
                         [1, 1, 2, 3, 5, 8, 13, 21, 34, 55])

    def test_fast_equals_iterative(self):            # точность
        for n in list(range(1, 500)) + [1000, 4321, 10000]:
            self.assertEqual(fibonacci(n), fib_iterative(n))

    def test_known_big_value(self):
        self.assertEqual(fibonacci(100), 354224848179261915075)

    def test_bounds(self):                           # защищённость
        self.assertEqual(len(str(fibonacci(MAX_N))), 208988)
        for bad in (0, -5, MAX_N + 1, 2.5, "10", True):
            with self.assertRaises(InputError):
                fibonacci(bad)

    def test_parse(self):                            # устойчивость
        self.assertEqual(parse_n(" 12 "), 12)
        self.assertEqual(parse_n("1e3"), 1000)
        self.assertEqual(parse_n("7,0"), 7)
        for bad in ("", "abc", "3.5", "-1", "0", "1e100"):
            with self.assertRaises(InputError):
                parse_n(bad)

    def test_format(self):
        self.assertEqual(format_number(55), "55")
        self.assertIn("всего цифр: 2090", format_number(fibonacci(10000)))

    def test_dialog_survives_bad_input(self):
        answers = iter(["abc", "-3", "?", "10", "q"])
        out = []
        dialog(lambda _: next(answers), out.append)
        text = "\n".join(out)
        self.assertEqual(text.count("Ошибка ввода"), 2)
        self.assertIn("F(10) = 55", text)
        self.assertIn("Работа завершена", text)


if __name__ == "__main__":
    unittest.main()
