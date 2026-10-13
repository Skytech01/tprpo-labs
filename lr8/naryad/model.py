"""Модуль model — запись «Наряд» и проверка её полей.

Наряд — документ на выполнение работы рабочим цеха: какая операция,
сколько деталей изготовлено и какова норма времени на одну деталь.
"""

from dataclasses import asdict, dataclass
from datetime import date

FIELDS = {                       # имя поля -> заголовок для пользователя
    "code": "Шифр наряда",
    "day": "Дата (ГГГГ-ММ-ДД)",
    "shop": "Номер цеха",
    "worker": "Табельный номер",
    "operation": "Код операции",
    "norm_hours": "Норма времени на деталь, ч",
    "quantity": "Изготовлено деталей",
}


class RecordError(ValueError):
    """Неверное значение поля записи."""


@dataclass
class Order:
    code: str            # шифр наряда, уникальный, например Н-0001
    day: date            # дата выдачи наряда
    shop: int            # номер цеха
    worker: int          # табельный номер рабочего
    operation: str       # код операции, например ТОК-12
    norm_hours: float    # норма времени на одну деталь, часов
    quantity: int        # количество изготовленных деталей

    @property
    def labour(self):
        """Нормированная трудоёмкость наряда, нормо-часов."""
        return round(self.norm_hours * self.quantity, 3)

    def to_dict(self):
        data = asdict(self)
        data["day"] = self.day.isoformat()
        return data


def parse_field(name, text):
    """Преобразовать строку в значение поля name с проверкой."""
    text = str(text).strip()
    if not text:
        raise RecordError(f"поле «{FIELDS[name]}» не заполнено")
    try:
        if name in ("code", "operation"):
            if len(text) > 20:
                raise RecordError(f"поле «{FIELDS[name]}» длиннее 20 символов")
            return text.upper()
        if name == "day":
            value = date.fromisoformat(text)
            if not date(2000, 1, 1) <= value <= date(2100, 12, 31):
                raise RecordError("дата вне диапазона 2000–2100")
            return value
        if name in ("shop", "worker", "quantity"):
            value = int(text)
            low = 0 if name == "quantity" else 1
            high = {"shop": 99, "worker": 999999, "quantity": 100000}[name]
            if not low <= value <= high:
                raise RecordError(f"«{FIELDS[name]}» должно быть от {low} до {high}")
            return value
        if name == "norm_hours":
            value = float(text.replace(",", "."))
            if not 0 < value <= 1000:
                raise RecordError("норма времени должна быть от 0 до 1000 ч")
            return value
    except ValueError as exc:
        if isinstance(exc, RecordError):
            raise
        raise RecordError(f"недопустимое значение поля «{FIELDS[name]}»: {text}") from None
    raise RecordError(f"неизвестное поле {name}")


def make_order(raw):
    """Создать Order из словаря строк (ввод пользователя или файл)."""
    try:
        return Order(**{name: parse_field(name, raw[name]) for name in FIELDS})
    except KeyError as exc:
        raise RecordError(f"нет поля {exc}") from None
