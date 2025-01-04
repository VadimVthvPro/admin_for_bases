import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime


def update_row(tree, item_id, new_values):
    """Функция для обновления строки в таблице."""
    try:
        # Обновляем данные в таблице
        tree.item(item_id, values=new_values)

        # Добавляем тег для выделения строки
        tree.tag_configure("updated", background="#d4f8d4")  # Светло-зелёный цвет
        tree.item(item_id, tags=("updated",))

        # Убираем выделение через 20 секунд
        def reset_style():
            tree.item(item_id, tags=())  # Убираем тег
        tree.after(20000, reset_style)  # 20000 миллисекунд = 20 секунд

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось обновить строку: {e}")


def center_window(window, width, height):
    """Функция для центрирования окна на экране."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def submit():
    """Функция для обработки входа пользователя."""
    name = entry_name.get()
    pas = entry_pas.get()
    print(f"Имя: {name}")
    print(f"Пароль: {pas}")

    try:
        # Подключение к базе данных
        conn = psycopg2.connect(
            dbname='propitashka',
            user=name,
            password=pas,
            host='localhost',
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_main")
        data = cursor.fetchall()

        if data:
            # Переходим ко второму окну
            show_main_window()
        else:
            error_label.config(text="Неверное имя пользователя или пароль", foreground="red")

        cursor.close()
        conn.close()

    except Exception as e:
        error_label.config(text="Неверное имя пользователя или пароль", foreground="red")
        print(f"Ошибка: {str(e)}")


def show_main_window():
    """Функция для отображения главного окна с вкладками."""
    # Скрываем фрейм входа
    frame.pack_forget()

    # Отображаем фрейм с вкладками
    notebook.pack(fill="both", expand=True)

    # Настраиваем новое окно
    window_width = 1200
    window_height = 800
    center_window(root, window_width, window_height)
    root.title("Меню")

    # Устанавливаем минимальный размер окна
    root.minsize(800, 600)  # Минимальный размер окна

    # Создаем вкладки
    create_tabs()


def sort_treeview(tree, col, reverse):
    """Функция для сортировки таблицы по столбцу с учетом типа данных."""
    # Получаем все данные из столбца
    data = [(tree.set(item, col), item) for item in tree.get_children("")]

    # Определяем тип данных в столбце
    try:
        # Пробуем преобразовать данные в числа
        data = [(float(tree.set(item, col)), item) for item in tree.get_children("")]
    except ValueError:
        try:
            # Пробуем преобразовать данные в даты (если это даты)
            data = [(datetime.strptime(tree.set(item, col), "%Y-%m-%d"), item) for item in tree.get_children("")]
        except ValueError:
            # Если не получается, сортируем как строки
            data = [(tree.set(item, col), item) for item in tree.get_children("")]

    # Сортируем данные
    data.sort(reverse=reverse)

    # Перемещаем элементы в отсортированном порядке
    for index, (val, item) in enumerate(data):
        tree.move(item, "", index)

    # Устанавливаем обратный порядок сортировки для следующего клика
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def create_table(tab, columns, query, table_name, column_mapping):
    """Функция для создания таблицы на вкладке."""
    # Контейнер для таблицы и скроллбаров
    container = ttk.Frame(tab)
    container.grid(row=2, column=0, sticky="nsew")  # Таблица теперь в строке 2

    # Создаем Treeview (используем tk.Treeview вместо ttk.Treeview)
    tree = tk.ttk.Treeview(container, columns=columns, show="headings")

    # Настраиваем заголовки
    for col in columns:
        tree.heading(col, text=column_mapping[col], command=lambda c=col: sort_treeview(tree, c, False))

    # Горизонтальный скроллбар
    h_scroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=h_scroll.set)
    h_scroll.grid(row=1, column=0, sticky="ew")

    # Вертикальный скроллбар
    v_scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scroll.set)
    v_scroll.grid(row=0, column=1, sticky="ns")

    # Размещение таблицы
    tree.grid(row=0, column=0, sticky="nsew")

    # Настройка растягивания внутри контейнера
    container.rowconfigure(0, weight=1)  # Растягиваем первую строку
    container.columnconfigure(0, weight=1)  # Растягиваем первый столбец

    # Настройка растягивания вкладки
    tab.rowconfigure(2, weight=1)  # Таблица теперь в строке 2
    tab.columnconfigure(0, weight=1)

    # Загрузка данных в таблицу
    def load_data():
        try:
            conn = psycopg2.connect(
                dbname='propitashka',
                user='postgres',  # Замените на ваши данные
                password='000',  # Замените на ваши данные
                host='localhost',
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            # Очищаем таблицу перед загрузкой новых данных
            for row in tree.get_children():
                tree.delete(row)

            # Заполняем таблицу данными
            for row in rows:
                tree.insert("", "end", values=row)

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    # Загружаем данные при создании таблицы
    load_data()

    # Фильтрация данных
    filter_frame = ttk.Frame(tab)
    filter_frame.grid(row=0, column=0, sticky="ew", pady=5)  # Фильтр теперь в строке 0

    filter_label = ttk.Label(filter_frame, text="Фильтр:")
    filter_label.pack(side="left", padx=5)

    filter_entry = ttk.Entry(filter_frame)
    filter_entry.pack(side="left", padx=5, fill="x", expand=True)

    def apply_filter():
        filter_text = filter_entry.get().lower()
        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = psycopg2.connect(
                dbname='propitashka',
                user='postgres',  # Замените на ваши данные
                password='000',  # Замените на ваши данные
                host='localhost',
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                if any(filter_text in str(cell).lower() for cell in row):
                    tree.insert("", "end", values=row)

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить фильтр: {e}")

    filter_button = ttk.Button(filter_frame, text="Искать", command=apply_filter)
    filter_button.pack(side="left", padx=5)

    # Кнопки "Обновить" и "Добавить запись" в одной строке
    button_frame = ttk.Frame(tab)
    button_frame.grid(row=1, column=0, sticky="ew", pady=5)  # Кнопки теперь в строке 1

    # Кнопка "Обновить"
    refresh_button = ttk.Button(button_frame, text="Обновить", command=load_data)
    refresh_button.pack(side="left", padx=5)

    # Кнопка "Добавить запись"
    add_button = ttk.Button(button_frame, text="Добавить запись", command=lambda: add_record(tree, columns, table_name, load_data))
    add_button.pack(side="left", padx=5)

    # Настройка растягивания столбцов и строк
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(2, weight=1)  # Таблица теперь в строке 2

def adjust_window_size(tree, columns):
    """Функция для автоматического подбора размера окна под таблицу."""
    # Рассчитываем ширину окна на основе количества столбцов
    column_width = 100  # Ширина одного столбца
    min_width = len(columns) * column_width + 50  # Минимальная ширина окна

    # Устанавливаем минимальный размер окна
    root.minsize(min_width, 600)  # Минимальная ширина и высота окна

    # Обновляем геометрию окна
    root.update_idletasks()


def add_record(tree, columns, table_name, load_data):
    """Функция для добавления новой записи."""
    add_window = tk.Toplevel()
    add_window.title("Добавить запись")
    window_width = 400
    window_height = 150
    center_window(add_window, window_width, window_height)

    entries = []
    for i, col in enumerate(columns):
        label = ttk.Label(add_window, text=col)
        label.grid(row=i, column=0, padx=5, pady=5)
        entry = ttk.Entry(add_window)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    def save_record():
        values = [entry.get() for entry in entries]
        try:
            conn = psycopg2.connect(
                dbname='propitashka',
                user='postgres',  # Замените на ваши данные
                password='000',  # Замените на ваши данные
                host='localhost',
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                values
            )
            conn.commit()
            cursor.close()
            conn.close()
            add_window.destroy()
            # Обновляем таблицу
            load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {e}")

    save_button = ttk.Button(add_window, text="Сохранить", command=save_record)
    save_button.grid(row=len(columns), column=0, columnspan=2, pady=10)


def create_tabs():
    """Функция для создания вкладок."""
    # Словарь для сопоставления русских и оригинальных названий колонок
    column_mapping = {
        "user_id": "Id пользователя",
        "user_name": "Имя пользователя",
        "user_sex": "Пол",
        "date_of_birth": "Возраст",
        "food_id": "Номер записи",
        "name_of_food": "Название блюда",
        "b": "Белки",
        "g": "Жиры",
        "u": "Углеводы",
        "cal": "Калорийность",
        "date": "Дата",
        "aim_id": "Номер записи",
        "user_aim": "Цель пользователя",
        "daily_cal": "Дневное количество калорий",
        "health_id": "Номер записи",
        "imt": "ИМТ",
        "imt_str": "Расшифровка ИМТ",
        "weight": "Вес",
        "height": "Рост",
        "lang": "Язык пользователя",
        "training_id": "Номер записи",
        "training_cal": "Сожжённые калории",
        "tren_time": "Продолжительность тренировки",
        "water_id": "Номер записи",
        "count": "Количество",
        "data": "Дата"
    }

    # Вкладка "Главная"
    main_tab = ttk.Frame(notebook)
    notebook.add(main_tab, text="Главная")
    create_table(main_tab, ["user_id", "user_name", "user_sex", "date_of_birth"],
                 "SELECT user_id, user_name, user_sex, date_of_birth FROM user_main", "user_main", column_mapping)

    # Вкладка "Еда"
    food_tab = ttk.Frame(notebook)
    notebook.add(food_tab, text="Еда")
    create_table(food_tab, ["food_id", "user_id", "name_of_food", "b", "g", "u", "cal", "date"],
                 "SELECT food_id, user_id, name_of_food, b, g, u, cal, date FROM food", "food", column_mapping)

    # Вкладка "Цели"
    goals_tab = ttk.Frame(notebook)
    notebook.add(goals_tab, text="Цели")
    create_table(goals_tab, ["aim_id", "user_id", "user_aim", "daily_cal"],
                 "SELECT aim_id, user_id, user_aim, daily_cal FROM user_aims", "user_aims", column_mapping)

    # Вкладка "Здоровье"
    health_tab = ttk.Frame(notebook)
    notebook.add(health_tab, text="Здоровье")
    create_table(health_tab, ["health_id", "user_id", "imt", "imt_str", "cal", "date", "weight", "height"],
                 "SELECT health_id, user_id, imt, imt_str, cal, date, weight, height FROM user_health", "user_health", column_mapping)

    # Вкладка "Язык"
    language_tab = ttk.Frame(notebook)
    notebook.add(language_tab, text="Язык")
    create_table(language_tab, ["user_id", "lang"],
                 "SELECT user_id, lang FROM user_lang", "user_lang", column_mapping)

    # Вкладка "Тренировки"
    training_tab = ttk.Frame(notebook)
    notebook.add(training_tab, text="Тренировки")
    create_table(training_tab, ["training_id", "user_id", "date", "training_cal", "tren_time"],
                 "SELECT training_id, user_id, date, training_cal, tren_time FROM user_training", "user_training", column_mapping)

    # Вкладка "Вода"
    water_tab = ttk.Frame(notebook)
    notebook.add(water_tab, text="Вода")
    create_table(water_tab, ["water_id", "user_id", "count", "data"],
                 "SELECT water_id, user_id, count, data FROM water", "water", column_mapping)


def close_window():
    """Функция для закрытия окна."""
    root.destroy()


def entry():
    """Функция для создания интерфейса входа."""
    global entry_name, entry_pas, error_label

    # Поле для имени пользователя
    label_name = ttk.Label(frame, text="Имя пользователя:")
    label_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_name = ttk.Entry(frame, width=20)  # Уменьшаем ширину поля ввода
    entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # Поле для пароля
    label_pas = ttk.Label(frame, text="Пароль:")
    label_pas.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_pas = ttk.Entry(frame, width=20, show="*")  # Уменьшаем ширину поля ввода
    entry_pas.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Фрейм для кнопок (располагается на уровне второй строки)
    button_frame = ttk.Frame(frame)
    button_frame.grid(row=2, column=0, columnspan=2, sticky="e", padx=5, pady=5)

    # Кнопка "Ок"
    button = ttk.Button(button_frame, text="Ок", command=submit, width=10)
    button.pack(side="left", padx=5)

    # Кнопка "Отмена"
    cancel_button = ttk.Button(button_frame, text="Отмена", command=close_window, width=10)
    cancel_button.pack(side="left", padx=5)

    # Метка для отображения ошибок
    error_label = ttk.Label(frame, text="", font=("Arial", 12))
    error_label.grid(row=3, column=0, columnspan=2, sticky="ew")  # Растягиваем на два столбца

    # Настройка растягивания столбцов и строк
    frame.columnconfigure(1, weight=1)  # Растягиваем второй столбец (поле ввода)
    frame.rowconfigure(0, weight=1)  # Растягиваем строки
    frame.rowconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)
    frame.rowconfigure(3, weight=1)


# Главное окно
root = tk.Tk()
root.title("Вход в систему")
window_width = 400
window_height = 150
center_window(root, window_width, window_height)

# Устанавливаем минимальный размер окна
root.minsize(300, 120)  # Минимальная ширина и высота окна

# Фрейм для входа
frame = ttk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Создаем виджет Notebook для вкладок
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)
notebook.pack_forget()  # Скрываем вкладки до успешного входа

# Инициализация интерфейса входа
entry()

# Запуск основного цикла
root.mainloop()
