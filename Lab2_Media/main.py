"""Лабораторная №2, вариант 36: Unsharp Masking и автоконтраст."""

from datetime import datetime
from pathlib import Path
import stat

from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError


ROOT = Path(__file__).resolve().parent
FILTERS = "Повышение резкости (Unsharp Masking) + Автоконтраст"


def write_log(filename, status):
    """Режим a сохраняет старые записи; UTF-8 сохраняет русский текст."""
    try:
        with (ROOT / "logs" / "history.txt").open("a", encoding="UTF-8") as log:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"[{time}] Файл: {filename} | Фильтр: {FILTERS} | Статус: {status}\n")
    except OSError as error:
        print(f"Ошибка записи журнала: {error}")


def main():
    filename = input("Введите имя изображения (image1.jpg или image2.png): ").strip()
    # Принимаем только имя, чтобы поиск оставался внутри data/input.
    if not filename or Path(filename).name != filename or "/" in filename or "\\" in filename:
        print("Ошибка: Введите только имя файла без пути")
        write_log(filename, "Некорректное имя файла")
        return

    source = ROOT / "data" / "input" / filename
    status = "Успешно"
    try:
        file_stat = source.stat()
        # В методичке есть противоречие: только чтение НЕ запрещает чтение.
        # Для требуемой демонстрации вводим явное учебное правило:
        # файлы с атрибутом ReadOnly не допускаются к обработке.
        # Это осознанно созданное исключение, а не отказ ОС в чтении.
        if getattr(file_stat, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_READONLY:
            raise PermissionError("Учебное ограничение для ReadOnly")

        with Image.open(source) as image:
            original = ImageOps.exif_transpose(image).convert("RGB")
            # Размытая копия вычитается из исходника; детали усиливаются.
            sharpened = original.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            # Диапазон яркостей каждого RGB-канала растягивается до 0..255.
            result = ImageOps.autocontrast(sharpened, cutoff=0)
            result.save(ROOT / "data" / "output" / "result.jpg", quality=95)
        print("Готово: data/output/result.jpg")
    except FileNotFoundError:
        status = "Файл не найден"
        print("Ошибка: Файл не найден")
    except PermissionError:
        status = "Ошибка доступа"
        # Формулировка сохранена по требованию методички, см. комментарий выше.
        print(f"Ошибка: Нет прав на чтение файла {filename}. Обратитесь к администратору")
    except UnidentifiedImageError:
        status = "Неверный формат изображения"
        print("Ошибка: Файл не является поддерживаемым изображением")
    except OSError as error:
        status = "Ошибка обработки или сохранения"
        print(f"Ошибка обработки или сохранения: {error}")

    write_log(filename, status)


if __name__ == "__main__":
    main()
