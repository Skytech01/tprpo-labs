"""Тесты к ЛР 7.  Запуск:  python -m unittest test_normal_diff_stats -v"""

import random
import unittest

import normal_diff_stats as nds


class TestStatistics(unittest.TestCase):
    def test_mean_and_variance(self):
        self.assertAlmostEqual(nds.mean_value([1, 2, 3, 4]), 2.5)
        self.assertAlmostEqual(nds.variance_value([1, 2, 3, 4]), 1.25)

    def test_differences(self):
        self.assertEqual(nds.neighbour_differences([1, 4, 9]), [3, 5])

    def test_differences_of_sorted_are_non_negative(self):
        values = sorted(nds.generate_normal(100, 1, 1, random.Random(5)))
        self.assertTrue(all(d >= 0 for d in nds.neighbour_differences(values)))

    def test_generator_parameters(self):
        values = nds.generate_normal(100_000, 1.0, 1.0, random.Random(1))
        self.assertAlmostEqual(nds.mean_value(values), 1.0, delta=0.02)
        self.assertAlmostEqual(nds.variance_value(values), 1.0, delta=0.03)

    def test_histogram_counts_everything(self):
        values = nds.generate_normal(99, 0, 1, random.Random(2))
        bins = nds.histogram(values, 10)
        self.assertEqual(len(bins), 10)
        self.assertEqual(sum(count for _, _, count in bins), 99)

    def test_histogram_constant_values(self):
        bins = nds.histogram([2.0] * 5, 10)
        self.assertEqual(sum(count for _, _, count in bins), 5)


if __name__ == "__main__":
    unittest.main()
