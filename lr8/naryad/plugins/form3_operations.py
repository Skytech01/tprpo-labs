"""Подключаемая форма 3: сводка по кодам операций за период.

Пример того, как добавляется третья форма отчётности без изменения
остальных модулей программы.
"""

from collections import defaultdict

from naryad.reports import report, table


@report("3", "Сводка по операциям за период (подключаемая форма)")
def operations_summary(orders, params):
    groups = defaultdict(list)
    for o in orders:
        groups[o.operation].append(o)
    head = f"ФОРМА 3. Сводка по операциям за {params['first']} – {params['last']}"
    if not groups:
        return head + "\nЗа период нарядов нет."
    rows = []
    for op in sorted(groups):
        items = groups[op]
        qty = sum(o.quantity for o in items)
        hours = sum(o.labour for o in items)
        rows.append([op, len({o.worker for o in items}), qty, f"{hours:.2f}",
                     f"{hours / qty:.3f}" if qty else "-"])
    return head + "\n" + table(
        ["Операция", "Рабочих", "Деталей", "Нормо-ч", "Ср. норма"], rows)
