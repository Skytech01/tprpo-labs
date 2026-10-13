"""Тесты БД «Наряд».  Запуск:  python -m unittest test_naryad -v"""

import json
import os
import shutil
import tempfile
import unittest
from datetime import date

from naryad.model import RecordError, make_order, parse_field
from naryad.reports import REPORTS, load_plugins
from naryad.storage import OrderBase
from naryad.ui import Console

HERE = os.path.dirname(os.path.abspath(__file__))


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "base.json")
        shutil.copy(os.path.join(HERE, "naryad.json"), self.path)
        self.base = OrderBase(self.path)
        self.base.load()

    def tearDown(self):
        shutil.rmtree(self.tmp)


class TestModel(unittest.TestCase):
    def test_parse_ok(self):
        self.assertEqual(parse_field("day", "2026-09-01"), date(2026, 9, 1))
        self.assertEqual(parse_field("norm_hours", "0,5"), 0.5)
        self.assertEqual(parse_field("operation", " ток-12 "), "ТОК-12")

    def test_parse_errors(self):
        bad = [("day", "31.09.2026"), ("day", "2026-02-30"), ("shop", "0"),
               ("shop", "три"), ("quantity", "-1"), ("norm_hours", "0"),
               ("worker", ""), ("code", "X" * 21)]
        for field, text in bad:
            with self.assertRaises(RecordError, msg=(field, text)):
                parse_field(field, text)

    def test_labour(self):
        o = make_order({"code": "a", "day": "2026-01-01", "shop": 1, "worker": 1,
                        "operation": "op", "norm_hours": 0.5, "quantity": 40})
        self.assertEqual(o.labour, 20)


class TestStorage(BaseCase):
    def test_load_count(self):
        self.assertGreaterEqual(len(self.base.orders), 5)

    def test_add_update_delete_save(self):
        order = make_order({"code": "Н-0100", "day": "2026-10-05", "shop": 3,
                            "worker": 1021, "operation": "ТОК-12",
                            "norm_hours": "0.5", "quantity": "10"})
        self.base.add(order)
        with self.assertRaises(RecordError):
            self.base.add(order)                       # повтор шифра
        self.base.update("н-0100", "quantity", "12")
        self.base.delete("Н-0001")
        self.base.save()
        again = OrderBase(self.path)
        again.load()
        self.assertEqual(again.find("Н-0100").quantity, 12)
        self.assertIsNone(again.find("Н-0001"))

    def test_update_to_existing_code(self):
        with self.assertRaises(RecordError):
            self.base.update("Н-0001", "code", "Н-0002")

    def test_delete_missing(self):
        with self.assertRaises(RecordError):
            self.base.delete("НЕТ")

    def test_search_and_period(self):
        self.assertEqual(len(self.base.search(worker=1021)), 3)
        sept = self.base.period(date(2026, 9, 1), date(2026, 9, 30))
        self.assertEqual(len(sept), 8)
        with self.assertRaises(RecordError):
            self.base.period(date(2026, 10, 1), date(2026, 9, 1))

    def test_broken_files(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("{не json")
        with self.assertRaises(RecordError):
            OrderBase(self.path).load()
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump([{"code": "A"}], fh)
        with self.assertRaises(RecordError):
            OrderBase(self.path).load()

    def test_missing_file_is_empty_base(self):
        self.assertEqual(OrderBase(os.path.join(self.tmp, "new.json")).load(), 0)


class TestReports(BaseCase):
    def test_form1_totals(self):
        orders = self.base.period(date(2026, 9, 1), date(2026, 9, 30))
        text = REPORTS["1"][2](orders, {"first": "2026-09-01", "last": "2026-09-30"})
        self.assertIn("Итого", text)
        self.assertIn("351", text)                      # деталей за сентябрь

    def test_form2_worker(self):
        params = {"first": date(2026, 9, 1), "last": date(2026, 10, 31),
                  "worker": 1021}
        text = REPORTS["2"][2](self.base.orders, params)
        self.assertEqual(text.count("Н-000"), 3)

    def test_plugin_form3(self):
        load_plugins()
        self.assertIn("3", REPORTS)
        text = REPORTS["3"][2](self.base.orders, {"first": "-", "last": "-"})
        self.assertIn("ТОК-12", text)


class TestConsole(BaseCase):
    def test_dialog(self):
        answers = iter([
            "9",                                           # нет пункта
            "2", "Н-0200", "2026-13-01", "2026-10-10", "3", "1021",
            "ТОК-12", "abc", "0.5", "8",                    # добавление
            "4", "Н-0002", "д",                            # удаление
            "6", "1", "2026-10-01", "2026-10-31",            # отчёт 1
            "0", "д"])
        out = []
        Console(self.base, lambda _: next(answers), out.append).run()
        text = "\n".join(out)
        self.assertIn("Нет такого пункта", text)
        self.assertIn("Наряд Н-0200 добавлен", text)
        self.assertIn("Запись удалена", text)
        self.assertIn("ФОРМА 1", text)
        again = OrderBase(self.path)
        again.load()
        self.assertIsNotNone(again.find("Н-0200"))


if __name__ == "__main__":
    unittest.main()
