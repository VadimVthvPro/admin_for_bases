import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime


def center_window(window, width, height):
    """Функция для центрирования окна на экране."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def get_db_connection():
    """Функция для подключения к базе данных."""
    return psycopg2.connect(
        dbname='propitashka',
        user='postgres',  # Замените на ваши данные
        password='000',  # Замените на ваши данные
        host='localhost',
        port="5432"
    )


def submit():
    """Функция для обработки входа пользователя."""
    name = entry_name.get()
    pas = entry_pas.get()
    print(f"Имя: {name}")
    print(f"Пароль: {pas}")

    try:
        # Подключение к базе данных
        conn = get_db_connection()
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
    root.title("PROпиташка")

    # Устанавливаем минимальный размер окна
    root.minsize(800, 600)  # Минимальный размер окна

    # Создаем вкладки
    create_tabs()


def delete_related_records(cursor, user_id):
    """Функция для удаления связанных записей из всех таблиц по user_id."""
    related_tables = ["food", "user_aims", "user_health", "user_lang", "user_training", "water"]
    for table in related_tables:
        cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))


def delete_record(tree, table_name, load_data):
    """Функция для удаления выбранных строк."""
    selected_items = tree.selection()  # Получаем выбранные строки
    if not selected_items:
        messagebox.showwarning("Предупреждение", "Выберите строки для удаления.")
        return

    # Подтверждение удаления
    confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранные строки?")
    if not confirm:
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for item in selected_items:
            # Получаем значения выбранной строки
            values = tree.item(item, "values")
            primary_key_value = values[0]  # Первичный ключ находится в первом столбце

            # Если удаляем из таблицы user_main, удаляем связанные записи
            if table_name == "user_main":
                delete_related_records(cursor, primary_key_value)

            # Удаляем строку из текущей таблицы
            primary_key_column = "user_id" if table_name == "user_main" or table_name=="user_lang" else f"{table_name.split('_')[-1]}_id"
            cursor.execute(f"DELETE FROM {table_name} WHERE {primary_key_column} = %s", (primary_key_value,))

        conn.commit()
        cursor.close()
        conn.close()

        # Обновляем таблицу
        load_data()
        messagebox.showinfo("Успех", "Строки успешно удалены.")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить строки: {e}")


def add_record(tree, columns, table_name, load_data):
    """Функция для добавления новой записи."""
    add_window = tk.Toplevel()
    add_window.title("Добавить запись")
    window_width = 400
    window_height = len(columns) * 40 + 100  # Учитываем высоту для всех полей ввода
    center_window(add_window, window_width, window_height)

    # Устанавливаем минимальный размер окна
    add_window.minsize(400, 200)  # Минимальная ширина и высота окна

    entries = []
    user_names = []
    user_ids = []

    for i, col in enumerate(columns):
        label = ttk.Label(add_window, text=col)
        label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

        # Если это поле water_id и таблица "water", создаем Spinbox для целых чисел
        if col == "water_id" and table_name == "water":
            entry = tk.Spinbox(add_window, from_=0, to=99999999999999999, increment=1)  # Числовой бокс для water_id
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле count и таблица "water", создаем Spinbox для целых чисел
        elif col == "count" and table_name == "water":
            entry = tk.Spinbox(add_window, from_=0, to=99999999999999999, increment=1)  # Числовой бокс для count
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле training_id и таблица "user_training", создаем Spinbox для целых чисел
        elif col == "training_id" and table_name == "user_training":
            entry = tk.Spinbox(add_window, from_=1, to=99999999999, increment=1)  # Числовой бокс для training_id
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле tren_time и таблица "user_training", создаем Spinbox для целых чисел
        elif col == "tren_time" and table_name == "user_training":
            entry = tk.Spinbox(add_window, from_=1, to=99999999999, increment=1)  # Числовой бокс для tren_time
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле training_cal и таблица "user_training", создаем Spinbox для чисел с плавающей точкой
        elif col == "training_cal" and table_name == "user_training":
            entry = tk.Spinbox(add_window, from_=1.0, to=9999999999999.0, increment=0.1, format="%.1f")  # Числовой бокс для float
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле health_id и таблица "user_health", создаем Spinbox для целых чисел
        elif col == "health_id" and table_name == "user_health":
            entry = tk.Spinbox(add_window, from_=1, to=999999999999999999, increment=1)  # Числовой бокс для health_id
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поля imt, cal, weight, height и таблица "user_health", создаем Spinbox для чисел с плавающей точкой
        elif col in ["imt", "cal", "weight", "height"] and table_name == "user_health":
            entry = tk.Spinbox(add_window, from_=1.0, to=9999999999.0, increment=0.1, format="%.1f")  # Числовой бокс для float
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле aim_id и таблица "user_aims", создаем Spinbox для целых чисел
        elif col == "aim_id" and table_name == "user_aims":
            entry = tk.Spinbox(add_window, from_=0, to=999999999999, increment=1)  # Числовой бокс для aim_id
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле daily_cal и таблица "user_aims", создаем Spinbox для целых чисел
        elif col == "daily_cal" and table_name == "user_aims":
            entry = tk.Spinbox(add_window, from_=0, to=999999999999, increment=1)  # Числовой бокс для daily_cal
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле food_id и таблица "food", создаем Spinbox для целых чисел
        elif col == "food_id" and table_name == "food":
            entry = tk.Spinbox(add_window, from_=1, to=999999999, increment=1)  # Числовой бокс для food_id
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поля b, g, u, cal и таблица "food", создаем Spinbox для чисел с плавающей точкой
        elif col in ["b", "g", "u", "cal"] and table_name == "food":
            entry = tk.Spinbox(add_window, from_=0.0, to=999999999.0, increment=0.1, format="%.1f")  # Числовой бокс для float
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле user_id и таблица "user_main", создаем Spinbox для целых чисел
        elif col == "user_id" and table_name == "user_main":
            entry = tk.Spinbox(add_window, from_=1, to=999999, increment=1)  # Числовой бокс для user_id
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле date_of_birth и таблица "user_main", создаем Spinbox для целых чисел
        elif col == "date_of_birth" and table_name == "user_main":
            entry = tk.Spinbox(add_window, from_=0, to=130, increment=1)  # Числовой бокс для возраста
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        # Если это поле user_id и таблица не "user_main", создаем combobox с user_name
        elif col == "user_id" and table_name != "user_main":
            # Получаем список user_id и user_name из таблицы user_main
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, user_name FROM user_main")
                user_data = cursor.fetchall()
                user_ids = [str(row[0]) for row in user_data]
                user_names = [row[1] for row in user_data]
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить user_id и user_name: {e}")
                user_ids = []
                user_names = []

            # Создаем combobox для выбора user_name
            entry = ttk.Combobox(add_window, values=user_names)
            if user_names:
                entry.current(0)  # Устанавливаем первый элемент по умолчанию
        # Если это поле user_sex и таблица "user_main", создаем combobox с выбором пола
        elif col == "user_sex" and table_name == "user_main":
            entry = ttk.Combobox(add_window, values=["Мужчина", "Женщина"])
            entry.current(0)  # Устанавливаем первый элемент по умолчанию
        # Если это поле даты, заполняем его автоматически
        elif col == "date" or col == "data":
            entry = ttk.Entry(add_window)
            entry.insert(0, datetime.now().strftime("%d-%m-%Y"))  # Вставляем сегодняшнюю дату
            entry.config(state="readonly")  # Делаем поле только для чтения
        else:
            entry = ttk.Entry(add_window)

        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        entries.append(entry)

    def save_record():
        values = []
        for i, entry in enumerate(entries):
            if columns[i] == "user_id" and table_name != "user_main":
                # Получаем выбранное user_name и находим соответствующий user_id
                selected_user_name = entry.get().strip()
                if selected_user_name in user_names:
                    user_id = user_ids[user_names.index(selected_user_name)]
                    values.append(user_id)
                else:
                    messagebox.showwarning("Предупреждение", "Выберите корректное имя пользователя!")
                    return
            else:
                if isinstance(entry, tk.Spinbox) or isinstance(entry, ttk.Combobox):
                    values.append(entry.get().strip())  # Получаем значение из Spinbox или Combobox
                else:
                    values.append(entry.get().strip())  # Получаем значение из текстового поля

        if any(not value for value in values):
            messagebox.showwarning("Предупреждение", "Заполните все поля!")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            add_window.destroy()

            # Обновляем данные таблицы
            load_data()

            # Находим добавленную строку (последнюю в таблице)
            last_item = tree.get_children()[-1]

            # Подсвечиваем строку зелёным цветом
            tree.tag_configure("highlight", background="#d4edda")  # Лёгкий зелёный цвет
            tree.item(last_item, tags=("highlight",))

            # Сбрасываем подсветку через 20 секунд
            def reset_highlight():
                if tree.exists(last_item):  # Проверяем, существует ли строка
                    tree.item(last_item, tags=())

            tree.after(20000, reset_highlight)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {e}")

    # Фрейм для кнопок (располагается на уровне последней строки)
    button_frame = ttk.Frame(add_window)
    button_frame.grid(row=len(columns), column=0, columnspan=2, sticky="e", padx=5, pady=5)

    # Кнопка "Ок"
    add_button = ttk.Button(button_frame, text="Ок", command=save_record, width=10)
    add_button.pack(side="left", padx=5)

    # Кнопка "Отмена"
    cancel_button = ttk.Button(button_frame, text="Отмена", command=add_window.destroy, width=10)
    cancel_button.pack(side="left", padx=5)
def edit_cell(event, tree, columns, table_name, load_data):
    """Функция для редактирования ячейки при двойном клике."""
    region = tree.identify_region(event.x, event.y)
    if region != "cell":
        return

    item = tree.selection()[0]
    column = tree.identify_column(event.x)
    column_index = int(column.replace("#", "")) - 1
    column_name = columns[column_index]

    # Получаем текущее значение ячейки
    current_value = tree.set(item, column)

    # Создаем поле для редактирования
    entry_edit = ttk.Entry(tree, font=("Arial", 16))  # Увеличиваем шрифт в 2 раза
    entry_edit.insert(0, current_value)
    entry_edit.select_range(0, tk.END)
    entry_edit.focus()

    def save_edit(event):
        new_value = entry_edit.get().strip()
        if new_value != current_value:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                primary_key_value = tree.item(item, "values")[0]  # Первичный ключ
                primary_key_column = columns[0]
                update_query = f"UPDATE {table_name} SET {column_name} = %s WHERE {primary_key_column} = %s"
                cursor.execute(update_query, (new_value, primary_key_value))
                conn.commit()
                cursor.close()
                conn.close()

                # Сохраняем идентификатор строки перед обновлением данных
                item_id = tree.item(item, "values")[0]

                # Обновляем данные таблицы
                load_data()

                # Находим строку с обновлёнными данными
                for child in tree.get_children():
                    if tree.item(child, "values")[0] == item_id:
                        # Подсвечиваем строку зелёным цветом
                        tree.tag_configure("highlight", background="#d4edda")  # Лёгкий зелёный цвет
                        tree.item(child, tags=("highlight",))

                        # Сбрасываем подсветку через 20 секунд
                        def reset_highlight():
                            if tree.exists(child):  # Проверяем, существует ли строка
                                tree.item(child, tags=())

                        tree.after(20000, reset_highlight)
                        break

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить запись: {e}")
        entry_edit.destroy()

    entry_edit.bind("<Return>", save_edit)
    entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

    # Размещаем поле для редактирования
    x, y, width, height = tree.bbox(item, column)
    entry_edit.place(x=x, y=y, width=width, height=height * 2)  # Увеличиваем высоту в 2 раза
def sort_treeview(tree, col, reverse):
    """Сортировка данных в Treeview по выбранному столбцу."""
    data = [(tree.set(item, col), item) for item in tree.get_children("")]
    data.sort(reverse=reverse)

    for index, (val, item) in enumerate(data):
        tree.move(item, "", index)

    # Изменяем направление сортировки для следующего нажатия
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def create_table(tab, columns, query, table_name, column_mapping):
    """Функция для создания таблицы на вкладке."""
    # Контейнер для таблицы и скроллбаров
    container = ttk.Frame(tab)
    container.grid(row=2, column=0, sticky="nsew")

    # Создаем Treeview
    tree = ttk.Treeview(container, columns=columns, show="headings")

    # Настраиваем заголовки (жирный шрифт)
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))  # Жирный шрифт для заголовков

    for col in columns:
        tree.heading(col, text=column_mapping[col], command=lambda c=col: sort_treeview(tree, c, False))

    # Горизонтальный и вертикальный скроллбары
    h_scroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=h_scroll.set)
    h_scroll.grid(row=1, column=0, sticky="ew")

    v_scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scroll.set)
    v_scroll.grid(row=0, column=1, sticky="ns")

    # Размещение таблицы
    tree.grid(row=0, column=0, sticky="nsew")

    # Настройка растягивания
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)
    tab.rowconfigure(2, weight=1)
    tab.columnconfigure(0, weight=1)

    # Загрузка данных в таблицу
    def load_data():
        try:
            conn = get_db_connection()
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

    load_data()

    # Фильтрация данных
    filter_frame = ttk.Frame(tab)
    filter_frame.grid(row=0, column=0, sticky="ew", pady=5)

    filter_label = ttk.Label(filter_frame, text="Фильтр:")
    filter_label.pack(side="left", padx=5)

    filter_entry = ttk.Entry(filter_frame)
    filter_entry.pack(side="left", padx=5, fill="x", expand=True)

    def apply_filter():
        filter_text = filter_entry.get().lower()
        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = get_db_connection()
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

    # Кнопки управления
    button_frame = ttk.Frame(tab)
    button_frame.grid(row=1, column=0, sticky="ew", pady=5)

    refresh_button = ttk.Button(button_frame, text="Обновить", command=load_data)
    refresh_button.pack(side="left", padx=5)

    add_button = ttk.Button(button_frame, text="Добавить запись", command=lambda: add_record(tree, columns, table_name, load_data))
    add_button.pack(side="left", padx=5)

    delete_button = ttk.Button(button_frame, text="Удалить строку", command=lambda: delete_record(tree, table_name, load_data))
    delete_button.pack(side="left", padx=5)

    # Привязываем двойной клик для редактирования ячейки
    tree.bind("<Double-1>", lambda event: edit_cell(event, tree, columns, table_name, load_data))


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
                 "SELECT health_id, user_id, imt, imt_str, cal, date, weight, height FROM user_health", "user_health",
                 column_mapping)

    # Вкладка "Язык"
    language_tab = ttk.Frame(notebook)
    notebook.add(language_tab, text="Язык")
    create_table(language_tab, ["user_id", "lang"],
                 "SELECT user_id, lang FROM user_lang", "user_lang", column_mapping)

    # Вкладка "Тренировки"
    training_tab = ttk.Frame(notebook)
    notebook.add(training_tab, text="Тренировки")
    create_table(training_tab, ["training_id", "user_id", "date", "training_cal", "tren_time"],
                 "SELECT training_id, user_id, date, training_cal, tren_time FROM user_training", "user_training",
                 column_mapping)

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
root.title("Вход в систему PROпиташка")
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
