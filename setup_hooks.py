
import os
import subprocess
import sys


def setup_pre_commit():
    try:

        subprocess.run([sys.executable, "-m", "pre_commit", "install"], check=True)
        print("✅ Pre-commit hooks установлены")

        subprocess.run(
            [sys.executable, "-m", "pre_commit", "install", "--hook-type", "pre-push"],
            check=True,
        )
        print("✅ Pre-push hooks установлены")

    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке hooks: {e}")
        sys.exit(1)


def install_dev_dependencies():
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"],
            check=True,
        )
        print("✅ Dev зависимости установлены")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🚀 Настройка инструментов качества кода...")

    if not os.path.exists("requirements-dev.txt"):
        print("❌ Файл requirements-dev.txt не найден")
        sys.exit(1)

    install_dev_dependencies()
    setup_pre_commit()

    print("\n🎉 Настройка завершена!")
    print("📋 Доступные команды:")
    print("   black .          - форматирование кода")
    print("   isort .          - сортировка импортов")
    print("   flake8           - проверка стиля")
    print("   mypy .           - проверка типов")
    print("   pre-commit run --all-files - запуск всех проверок")