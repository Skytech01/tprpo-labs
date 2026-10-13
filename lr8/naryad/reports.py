"""Модуль reports — формы отчётности и механизм их подключения.

Каждая форма — функция (orders, params) -> str, зарегистрированная
декоратором @report. Меню строится по реестру REPORTS, поэтому новая
форма подключается без изменения других модулей: достаточно положить
модуль с формой в каталог plugins (см. load_plugins).
"""

import importlib
import os
import pkgutil
from collections import defaultdict

REPORTS = {}        # ключ -> (название, нужен ли период, функция)


def report(key, title, needs_period=True):
    """Декоратор регистрации формы отчётности."""
    def register(func):
        REPORTS[key] = (title, needs_period, func)
        return func
    return register


def table(headers, rows, total=None):
    """Текстовая таблица с рамкой."""
    cells = [headers] + [[str(c) for c in r] for r in rows]
    if total:
        cells.append([str(c) for c in total])
    widths = [max(len(row[i]) for row in cells) for i in range(len(headers))]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt(row):
        return "| " + " | ".join(c.rjust(w) for c, w in zip(row, widths)) + " |"

    out = [line, fmt(headers), line] + [fmt(r) for r in cells[1:len(rows) + 1]]
    out.append(line)
    if total:
        out += [fmt(cells[-1]), line]
    return "\n".join(out)


@report("1", "Выработка цехов за период")
def shop_output(orders, params):
    """Форма 1: по каждому цеху — число нарядов, деталей, нормо-часов."""
    groups = defaultdict(list)
    for o in orders:
        groups[o.shop].append(o)
    rows = []
    for shop in sorted(groups):
        items = groups[shop]
        rows.append([shop, len(items), sum(o.quantity for o in items),
                     f"{sum(o.labour for o in items):.2f}"])
    total = ["Итого", len(orders), sum(o.quantity for o in orders),
             f"{sum(o.labour for o in orders):.2f}"]
    head = f"ФОРМА 1. Выработка цехов за {params['first']} – {params['last']}"
    if not orders:
        return head + "\nЗа период нарядов нет."
    return head + "\n" + table(["Цех", "Нарядов", "Деталей", "Нормо-часов"], rows, total)


@report("2", "Наряды рабочего за период")
def worker_card(orders, params):
    """Форма 2: перечень нарядов одного рабочего с итогом."""
    worker = params["worker"]
    own = sorted((o for o in orders if o.worker == worker), key=lambda o: o.day)
    head = (f"ФОРМА 2. Наряды рабочего, табельный № {worker}, "
            f"период {params['first']} – {params['last']}")
    if not own:
        return head + "\nНарядов не найдено."
    rows = [[o.code, o.day, o.shop, o.operation, f"{o.norm_hours:g}",
             o.quantity, f"{o.labour:.2f}"] for o in own]
    total = ["Итого", "", "", "", "", sum(o.quantity for o in own),
             f"{sum(o.labour for o in own):.2f}"]
    return head + "\n" + table(
        ["Шифр", "Дата", "Цех", "Операция", "Норма, ч", "Деталей", "Нормо-ч"],
        rows, total)


def load_plugins():
    """Подключить дополнительные формы из пакета naryad.plugins."""
    from . import plugins
    loaded = []
    for info in pkgutil.iter_modules([os.path.dirname(plugins.__file__)]):
        importlib.import_module(f"{plugins.__name__}.{info.name}")
        loaded.append(info.name)
    return loaded
