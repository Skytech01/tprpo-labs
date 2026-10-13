"""Модуль storage — хранение нарядов в файле JSON и операции над записями.

Единственный модуль, который работает с файлом. Остальные модули
получают и передают объекты Order через методы класса OrderBase.
"""

import json
import os

from .model import FIELDS, Order, RecordError, make_order, parse_field


class OrderBase:
    """Набор нарядов, связанный с файлом."""

    def __init__(self, path):
        self.path = path
        self.orders = []
        self.modified = False

    # ---------- файл ----------
    def load(self):
        """Прочитать файл. Отсутствующий файл = пустая база."""
        if not os.path.exists(self.path):
            self.orders = []
            return 0
        try:
            with open(self.path, encoding="utf-8") as fh:
                rows = json.load(fh)
        except json.JSONDecodeError as exc:
            raise RecordError(f"файл базы повреждён (строка {exc.lineno})") from None
        if not isinstance(rows, list):
            raise RecordError("файл базы должен содержать список записей")
        orders = []
        for number, row in enumerate(rows, 1):
            try:
                orders.append(make_order(row))
            except RecordError as exc:
                raise RecordError(f"запись {number} в файле: {exc}") from None
        self.orders = orders
        self._check_unique()
        self.modified = False
        return len(orders)

    def save(self):
        """Записать базу через временный файл (не теряем данные при сбое)."""
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump([o.to_dict() for o in self.orders], fh,
                      ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)
        self.modified = False

    def _check_unique(self):
        codes = [o.code for o in self.orders]
        doubles = {c for c in codes if codes.count(c) > 1}
        if doubles:
            raise RecordError(f"повторяются шифры нарядов: {', '.join(sorted(doubles))}")

    # ---------- операции ----------
    def find(self, code):
        code = code.strip().upper()
        for order in self.orders:
            if order.code == code:
                return order
        return None

    def add(self, order):
        if self.find(order.code):
            raise RecordError(f"наряд с шифром {order.code} уже есть")
        self.orders.append(order)
        self.modified = True

    def update(self, code, field, text):
        """Изменить одно поле наряда (корректировка)."""
        order = self.find(code)
        if order is None:
            raise RecordError(f"наряд {code} не найден")
        value = parse_field(field, text)
        if field == "code" and value != order.code and self.find(value):
            raise RecordError(f"шифр {value} уже занят")
        setattr(order, field, value)
        self.modified = True
        return order

    def delete(self, code):
        order = self.find(code)
        if order is None:
            raise RecordError(f"наряд {code} не найден")
        self.orders.remove(order)
        self.modified = True
        return order

    def search(self, **conditions):
        """Поиск по равенству полей, например search(shop=3, worker=1021)."""
        unknown = set(conditions) - set(FIELDS)
        if unknown:
            raise RecordError(f"неизвестные поля: {', '.join(unknown)}")
        return [o for o in self.orders
                if all(getattr(o, f) == v for f, v in conditions.items())]

    def period(self, first, last):
        """Наряды с датой в интервале [first; last]."""
        if first > last:
            raise RecordError("начало периода позже его окончания")
        return [o for o in self.orders if first <= o.day <= last]


__all__ = ["OrderBase", "Order"]
