"""Запуск БД «Наряд».

    python main.py [файл_базы.json] [--no-plugins]
"""

import sys

from naryad.model import RecordError
from naryad.reports import load_plugins
from naryad.storage import OrderBase
from naryad.ui import Console

DEFAULT_FILE = "naryad.json"


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    base = OrderBase(args[0] if args else DEFAULT_FILE)
    try:
        count = base.load()
    except RecordError as exc:
        print(f"Не удалось открыть базу: {exc}")
        return 1
    print(f"Загружено нарядов: {count} (файл {base.path})")
    if "--no-plugins" not in argv:
        names = load_plugins()
        if names:
            print("Подключены формы отчётов:", ", ".join(names))
    try:
        Console(base).run()
    except (KeyboardInterrupt, EOFError):
        print("\nРабота прервана. Несохранённые изменения потеряны.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
