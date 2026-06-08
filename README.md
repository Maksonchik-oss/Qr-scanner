# Детектирование QR-кодов 
1. ЧТО ЭТО ЗА ПРОГРАММА
SMART QR SYSTEM — это программа для автоматического распознавания QR-кодов из графических файлов.

Что умеет:

•Сканировать все изображения из папки input_qr одним нажатием кнопки

•Распознавать QR-коды

•Работать с форматами: PNG, JPG, JPEG, BMP, TIFF, GIF

•Сохранять историю сканирований в базу данных

•Автоматически открывать ссылки (сайты, Telegram-каналы) в браузере

•Показывать статистику (всего, Telegram-ссылок, URL, текста)

•Искать и фильтровать результаты

2. УСТАНОВКА
   ! Требования к компьютеру !
Параметр	Минимальные требования
•Операционная система	Windows 10/11, macOS, Linux
•Процессор	Intel Core i3/или выше или аналог
•ОЗУ	4 ГБ
•Python/PyCharm	Версия 3.8 или выше

ЗАПУСК ЧЕРЕЗ JUPYTER NOTEBOOK
ШАГ 1. Установите PyCharm (если ещё не установлен)
Перейдите на сайт: https://pycharm-community-edition.softonic.ru/

•Скачайте последнюю версию PyCharm

•Запустите установщик

••ОБЯЗАТЕЛЬНО поставьте галочку "Add Python to PATH"

•Нажмите "Install Now"

ШАГ 2. Установите Jupyter и библиотеки
Откройте командную строку (нажмите Win + R, введите cmd, нажмите Enter).

•Выполните одну команду для установки всего:
pip install jupyter opencv-python pillow numpy

•Ждите окончания установки (может занять 2-3 минуты).

ШАГ 3. Запустите Jupyter Notebook
•В той же командной строке выполните:
jupyter notebook
После этого:

•Откроется окно в браузере

•Вы увидите список файлов и папок на компьютере

ШАГ 4. Создайте новый блокнот
В правой части экрана нажмите кнопку New → Python 3 (или Новый → Python 3)

Появится пустая ячейка.

ШАГ 5. Скопируйте и вставьте код
Полностью скопируйте код из файла Skaner.py  и вставьте в ячейку Jupyter

ШАГ 6. Запустите код
Нажмите Shift + Enter (или кнопку Run).

ШАГ 7. Подготовьте изображения
Важно! Папка input_qr должна быть в той же папке, где находится ваш Jupyter Notebook.

Посмотрите, где находится ваш блокнот:

В Jupyter сверху показан путь (например, C:\Users\Ваше_имя)

Создайте там папку input_qr

Положите туда картинки с QR-кодами

ШАГ 8. Пользуйтесь программой
После запуска откроется окно программы. Нажмите SCAN FOLDER.

⚠️ ВОЗМОЖНЫЕ ОШИБКИ И РЕШЕНИЯ
Ошибка	Решение
•ModuleNotFoundError: No module named 'cv2'	
•Выполнить pip install opencv-python в командной строке, перезапустить Jupyter

•ModuleNotFoundError: No module named 'PIL'	
•Выполнить pip install pillow

•ModuleNotFoundError: No module named 'numpy'	
•Выполнить pip install numpy

•Jupyter не запускается	
мВыполнить python -m pip install --upgrade pip, затем pip install jupyter

•Нет изображений в папке 'input_qr'	
•Создать папку input_qr и положить туда картинки

•Окно программы не появилось	
•Закрыть Jupyter, открыть снова и перезапустить ячейку


БЛОКИ КОДА
БЛОК 1: Импорт библиотек (строки 1-12)
import cv2          # распознавание кодов
import os           # работа с файлами
import webbrowser   # открытие ссылок
import threading    # многопоточность
import tkinter as tk # окна и кнопки
import sqlite3      # база данных
from PIL import Image # чтение GIF
import numpy as np  # преобразование картинок

БЛОК 2: Глобальные переменные (строки 15-22)
barcode_detector = cv2.barcode.BarcodeDetector()  # детектор штрихкодов
processing = False           # флаг: идёт ли сканирование
scanned_qr = set()           # множество отсканированных кодов (против дублей)
input_folder = "input_qr"    # папка с картинками

БЛОК 3: База данных (строки 25-36)
connection = sqlite3.connect("qr_database.db")  # подключение к БД
cursor.execute("CREATE TABLE IF NOT EXISTS qr_codes (...)")  # создание таблицы

БЛОК 4: Обработка ссылок (строки 38-65)
def handle_qr_data(qr_text):
    if "t.me/" in qr_text: открыть Telegram
    elif "http" in qr_text: открыть сайт
    elif "www." in qr_text: добавить https:// и открыть

БЛОК 5: Сохранение результатов (строки 67-92)
def save_scan(unique_id, qr_text):
    if unique_id in scanned_qr: return  # пропустить дубликат
    scanned_qr.add(unique_id)            # запомнить
    # сохранить в БД с датой и временем
    # добавить строку в таблицу на экране
    handle_qr_data(qr_text)              # открыть ссылку

БЛОК 6: Загрузка  (строки 94-112)
def load_image_as_cv2(filepath):
    if файл .gif:
        # PIL → RGB → NumPy → BGR (для OpenCV)
    else:
        return cv2.imread(filepath)

БЛОК 7: Главный алгоритм сканирования (строки 114-172)
def scan_images_in_folder():
    files = все картинки из input_qr
    for каждого файла:
        img = load_image_as_cv2(файл)
        
        # Распознать QR-коды
        qr_detector.detectAndDecodeMulti(img)
        
        # Распознать штрихкоды
        barcode_detector.detectAndDecode(img)
        
        # Сохранить всё, что нашли
        save_scan(...)

БЛОК 8: Таблица и фильтры (строки 174-240)
def filter_qr(type):     # ALL / TELEGRAM / URL / TEXT
def search_qr():         # поиск по всем полям
def load_all_qr():       # загрузить всё из БД

БЛОК 9: Статистика (строки 242-272)
def update_stats():
    # Считаем количество записей в БД
    total_label.config(text=f"TOTAL\n{количество}")
    # Считаем Telegram, URL, TEXT
    root.after(1000, update_stats)  # повторять каждую секунду

БЛОК 10: Создание интерфейса (строки 274-370)
root = tk.Tk()                    # главное окно
# Статистика (4 окошка)
# Левая панель (кнопки: SCAN, CLEAR, EXIT)
# Правая панель (поиск, фильтры, таблица)

БЛОК 11: Запуск (строки 372-374)
load_all_qr()      # загрузить историю
update_stats()     # запустить счётчики
root.mainloop()    # запустить окно
