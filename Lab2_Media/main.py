from datetime import datetime
from pathlib import Path
import stat
from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError
ROOT = Path(__file__).resolve().parent
FILTERS = 'Повышение резкости (Unsharp Masking) + Автоконтраст'

def write_log(filename, status):
    try:
        with (ROOT / 'logs' / 'history.txt').open('a', encoding='UTF-8') as log:
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log.write(f'[{time}] Файл: {filename} | Фильтр: {FILTERS} | Статус: {status}\n')
    except OSError as error:
        print(f'Ошибка записи журнала: {error}')

def main():
    filename = input('Введите имя изображения (image1.jpg или image2.png): ').strip()
    if not filename or Path(filename).name != filename or '/' in filename or ('\\' in filename):
        print('Ошибка: Введите только имя файла без пути')
        write_log(filename, 'Некорректное имя файла')
        return
    source = ROOT / 'data' / 'input' / filename
    status = 'Успешно'
    try:
        file_stat = source.stat()
        if getattr(file_stat, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_READONLY:
            raise PermissionError('Учебное ограничение для ReadOnly')
        with Image.open(source) as image:
            original = ImageOps.exif_transpose(image).convert('RGB')
            sharpened = original.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            result = ImageOps.autocontrast(sharpened, cutoff=0)
            result.save(ROOT / 'data' / 'output' / 'result.jpg', quality=95)
        print('Готово: data/output/result.jpg')
    except FileNotFoundError:
        status = 'Файл не найден'
        print('Ошибка: Файл не найден')
    except PermissionError:
        status = 'Ошибка доступа'
        print(f'Ошибка: Нет прав на чтение файла {filename}. Обратитесь к администратору')
    except UnidentifiedImageError:
        status = 'Неверный формат изображения'
        print('Ошибка: Файл не является поддерживаемым изображением')
    except OSError as error:
        status = 'Ошибка обработки или сохранения'
        print(f'Ошибка обработки или сохранения: {error}')
    write_log(filename, status)
if __name__ == '__main__':
    main()

