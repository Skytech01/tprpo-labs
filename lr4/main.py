"""Точка входа программы «Решение комбинаторно-оптимизационных задач».

Запуск:  python main.py
"""

from combopt.ui import Console


def main():
    try:
        Console().run()
    except (KeyboardInterrupt, EOFError):
        print("\nРабота прервана пользователем.")


if __name__ == "__main__":
    main()
