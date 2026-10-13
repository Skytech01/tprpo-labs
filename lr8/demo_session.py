"""Протокол демонстрационного сеанса (ввод пользователя виден в протоколе)."""
import os
import shutil
import sys

from naryad.reports import load_plugins
from naryad.storage import OrderBase
from naryad.ui import Console

os.makedirs("demo", exist_ok=True)
shutil.copy("naryad.json", "demo/naryad.json")
base = OrderBase("demo/naryad.json")
print(f"Загружено нарядов: {base.load()}")
load_plugins()
answers = iter(sys.stdin.read().split("\n"))
log = []


def read(prompt):
    value = next(answers)
    log.append(prompt + value)
    return value


Console(base, read, log.append).run()
print("\n".join(log))
