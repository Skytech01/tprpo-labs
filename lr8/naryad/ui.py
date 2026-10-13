"""Модуль ui — консольный диалог с пользователем БД «Наряд»."""

from .model import FIELDS, RecordError, make_order, parse_field
from .reports import REPORTS, table

MENU = """
=============== БД «НАРЯД» ===============
 1. Просмотр всех нарядов
 2. Добавить наряд
 3. Корректировать наряд
 4. Удалить наряд
 5. Поиск нарядов
 6. Отчёты
 7. Сохранить
 0. Выход
=========================================="""


class Console:
    def __init__(self, base, read=input, write=print):
        self.base = base
        self.ask = read
        self.say = write

    # ---------- вспомогательные ----------
    def ask_field(self, name, default=None):
        """Запрашивать поле, пока значение не пройдёт проверку."""
        hint = f" [{default}]" if default is not None else ""
        while True:
            text = self.ask(f"{FIELDS[name]}{hint}: ").strip()
            if not text and default is not None:
                text = str(default)
            try:
                return parse_field(name, text)
            except RecordError as exc:
                self.say(f"  Ошибка: {exc}")

    def ask_period(self):
        while True:
            first = self.ask_field_date("Начало периода")
            last = self.ask_field_date("Конец периода")
            if first <= last:
                return first, last
            self.say("  Ошибка: начало периода позже окончания.")

    def ask_field_date(self, title):
        while True:
            text = self.ask(f"{title} (ГГГГ-ММ-ДД): ").strip()
            try:
                return parse_field("day", text)
            except RecordError as exc:
                self.say(f"  Ошибка: {exc}")

    def show(self, orders):
        if not orders:
            self.say("Записей нет.")
            return
        rows = [[o.code, o.day, o.shop, o.worker, o.operation,
                 f"{o.norm_hours:g}", o.quantity, f"{o.labour:.2f}"] for o in orders]
        self.say(table(["Шифр", "Дата", "Цех", "Таб.№", "Операция",
                        "Норма, ч", "Деталей", "Нормо-ч"], rows))
        self.say(f"Всего записей: {len(orders)}")

    # ---------- пункты меню ----------
    def list_all(self):
        self.show(sorted(self.base.orders, key=lambda o: (o.day, o.code)))

    def add(self):
        raw = {}
        for name in FIELDS:
            while True:
                raw[name] = self.ask(f"{FIELDS[name]}: ")
                try:
                    parse_field(name, raw[name])
                    break
                except RecordError as exc:
                    self.say(f"  Ошибка: {exc}")
        try:
            order = make_order(raw)
            self.base.add(order)
            self.say(f"Наряд {order.code} добавлен.")
        except RecordError as exc:
            self.say(f"  Наряд не добавлен: {exc}")

    def edit(self):
        order = self.base.find(self.ask("Шифр наряда: "))
        if order is None:
            self.say("  Наряд не найден.")
            return
        self.show([order])
        self.say("Введите новые значения (Enter — оставить прежнее).")
        for name in FIELDS:
            old = getattr(order, name)
            old_text = old.isoformat() if name == "day" else old
            value = self.ask_field(name, old_text)
            if value != old:
                try:
                    self.base.update(order.code, name, str(value) if name != "day"
                                     else value.isoformat())
                except RecordError as exc:
                    self.say(f"  Ошибка: {exc}")
        self.say("Корректировка выполнена.")

    def remove(self):
        code = self.ask("Шифр наряда для удаления: ")
        order = self.base.find(code)
        if order is None:
            self.say("  Наряд не найден.")
            return
        self.show([order])
        if self.ask("Удалить эту запись? (д/н): ").strip().lower() == "д":
            self.base.delete(order.code)
            self.say("Запись удалена.")
        else:
            self.say("Удаление отменено.")

    def search(self):
        self.say("Искать по: 1 — цеху, 2 — табельному номеру, "
                 "3 — коду операции, 4 — периоду")
        choice = self.ask("Ваш выбор: ").strip()
        try:
            if choice == "1":
                found = self.base.search(shop=self.ask_field("shop"))
            elif choice == "2":
                found = self.base.search(worker=self.ask_field("worker"))
            elif choice == "3":
                found = self.base.search(operation=self.ask_field("operation"))
            elif choice == "4":
                found = self.base.period(*self.ask_period())
            else:
                self.say("  Нет такого варианта поиска.")
                return
        except RecordError as exc:
            self.say(f"  Ошибка: {exc}")
            return
        self.show(found)

    def reports(self):
        for key, (title, _, _) in sorted(REPORTS.items()):
            self.say(f" {key}. {title}")
        key = self.ask("Номер формы: ").strip()
        if key not in REPORTS:
            self.say("  Нет такой формы.")
            return
        _, needs_period, func = REPORTS[key]
        params = {}
        orders = self.base.orders
        if needs_period:
            params["first"], params["last"] = self.ask_period()
            orders = self.base.period(params["first"], params["last"])
        if func.__name__ == "worker_card":
            params["worker"] = self.ask_field("worker")
        self.say(func(orders, params))

    def save(self):
        try:
            self.base.save()
            self.say(f"База сохранена в {self.base.path}")
        except OSError as exc:
            self.say(f"  Ошибка записи файла: {exc.strerror}")

    def run(self):
        actions = {"1": self.list_all, "2": self.add, "3": self.edit,
                   "4": self.remove, "5": self.search, "6": self.reports,
                   "7": self.save}
        while True:
            self.say(MENU)
            choice = self.ask("Выберите пункт: ").strip()
            if choice == "0":
                if self.base.modified and self.ask(
                        "Есть несохранённые изменения. Сохранить? (д/н): "
                        ).strip().lower() == "д":
                    self.save()
                self.say("Работа завершена.")
                return
            action = actions.get(choice)
            if action is None:
                self.say("  Нет такого пункта меню.")
            else:
                action()

