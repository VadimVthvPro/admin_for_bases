import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2


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
        error_label.config(text="Ошибка подключения: " + str(e), foreground="red")
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

    # Создаем вкладки
    create_tabs()


def create_table(tab, columns, query, table_name):
    """Функция для создания таблицы на вкладке."""
    # Создаем Treeview
    tree = ttk.Treeview(tab, columns=columns, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    # Настраиваем заголовки
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))

    # Настраиваем стиль для отображения сетки
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12), rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  # Убираем границы
    style.configure("Treeview", background="#E8E8E8", fieldbackground="#E8E8E8", foreground="black")
    style.map("Treeview", background=[("selected", "#0078D7")])  # Цвет выделенной строки

    # Добавляем сетку
    style.configure("Treeview", rowheight=25, borderwidth=1, relief="solid")
    style.configure("Treeview.Heading", borderwidth=1, relief="solid")

    # Получаем данные из базы данных
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

    # Редактирование данных
    def edit_cell(event):
        region = tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = tree.identify_column(event.x)
        item = tree.identify_row(event.y)
        column_index = int(column[1:]) - 1
        value = tree.item(item, "values")[column_index]

        entry_edit = ttk.Entry(tab)
        entry_edit.insert(0, value)
        entry_edit.place(x=event.x, y=event.y, width=100)

        def save_edit(event):
            new_value = entry_edit.get()
            tree.set(item, column, new_value)
            entry_edit.destroy()

            # Обновляем данные в базе данных
            try:
                conn = psycopg2.connect(
                    dbname='propitashka',
                    user='postgres',  # Замените на ваши данные
                    password='000',  # Замените на ваши данные
                    host='localhost',
                    port="5432"
                )
                cursor = conn.cursor()
                primary_key = tree.item(item, "values")[0]  # Предполагаем, что первый столбец — это первичный ключ
                cursor.execute(
                    f"UPDATE {table_name} SET {columns[column_index]} = %s WHERE {columns[0]} = %s",
                    (new_value, primary_key)
                )
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")

        entry_edit.bind("<Return>", save_edit)
        entry_edit.bind("<FocusOut>", save_edit)

    tree.bind("<Double-1>", edit_cell)

    # Фильтрация данных
    filter_frame = ttk.Frame(tab)
    filter_frame.grid(row=1, column=0, sticky="ew", pady=5)

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

    filter_button = ttk.Button(filter_frame, text="Применить", command=apply_filter)
    filter_button.pack(side="left", padx=5)

    # Кнопка для обновления данных
    refresh_button = ttk.Button(tab, text="Обновить", command=load_data)
    refresh_button.grid(row=2, column=0, sticky="ew", pady=5)

    # Кнопка для добавления новой записи
    add_button = ttk.Button(tab, text="Добавить запись", command=lambda: add_record(tree, columns, table_name, load_data))
    add_button.grid(row=3, column=0, sticky="ew", pady=5)

    # Настройка растягивания столбцов и строк
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(0, weight=1)
    tab.rowconfigure(1, weight=0)  # Фильтр
    tab.rowconfigure(2, weight=0)  # Кнопка "Обновить"
    tab.rowconfigure(3, weight=0)  # Кнопка "Добавить запись"

def add_record(tree, columns, table_name, load_data):
    """Функция для добавления новой записи."""
    add_window = tk.Toplevel()
    add_window.title("Добавить запись")

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
            for row in tree.get_children():
                tree.delete(row)
            load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {e}")

    save_button = ttk.Button(add_window, text="Сохранить", command=save_record)
    save_button.grid(row=len(columns), column=0, columnspan=2, pady=10)


def sort_treeview(tree, col, reverse):
    """Функция для сортировки таблицы по столбцу."""
    data = [(tree.set(item, col), item) for item in tree.get_children("")]
    data.sort(reverse=reverse)

    for index, (val, item) in enumerate(data):
        tree.move(item, "", index)

    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def create_tabs():
    """Функция для создания вкладок."""
    # Вкладка "Главная"
    main_tab = ttk.Frame(notebook)
    notebook.add(main_tab, text="Главная")
    create_table(main_tab, ["user_id", "user_name", "user_sex", "date_of_birth"],
                 "SELECT user_id, user_name, user_sex, date_of_birth FROM user_main", "user_main")

    # Вкладка "Еда"
    food_tab = ttk.Frame(notebook)
    notebook.add(food_tab, text="Еда")
    create_table(food_tab, ["food_id", "user_id", "name_of_food", "b", "g", "u", "cal", "date"],
                 "SELECT food_id, user_id, name_of_food, b, g, u, cal, date FROM food", "food")

    # Вкладка "Цели"
    goals_tab = ttk.Frame(notebook)
    notebook.add(goals_tab, text="Цели")
    create_table(goals_tab, ["aim_id", "user_id", "user_aim", "daily_cal"],
                 "SELECT aim_id, user_id, user_aim, daily_cal FROM user_aims", "user_aims")

    # Вкладка "Здоровье"
    health_tab = ttk.Frame(notebook)
    notebook.add(health_tab, text="Здоровье")
    create_table(health_tab, ["health_id", "user_id", "imt", "imt_str", "cal", "date", "weight", "height"],
                 "SELECT health_id, user_id, imt, imt_str, cal, date, weight, height FROM user_health", "user_health")

    # Вкладка "Язык"
    language_tab = ttk.Frame(notebook)
    notebook.add(language_tab, text="Язык")
    create_table(language_tab, ["user_id", "lang"],
                 "SELECT user_id, lang FROM user_lang", "user_lang")

    # Вкладка "Тренировки"
    training_tab = ttk.Frame(notebook)
    notebook.add(training_tab, text="Тренировки")
    create_table(training_tab, ["training_id", "user_id", "date", "training_cal", "tren_time"],
                 "SELECT training_id, user_id, date, training_cal, tren_time FROM user_training", "user_training")

    # Вкладка "Вода"
    water_tab = ttk.Frame(notebook)
    notebook.add(water_tab, text="Вода")
    create_table(water_tab, ["water_id", "user_id", "count", "data"],
                 "SELECT water_id, user_id, count, data FROM water", "water")

def entry():
    """Функция для создания интерфейса входа."""
    global entry_name, entry_pas, error_label

    # Поле для имени пользователя
    label_name = ttk.Label(frame, text="Имя пользователя:")
    label_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_name = ttk.Entry(frame, width=30)
    entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # Поле для пароля
    label_pas = ttk.Label(frame, text="Пароль:")
    label_pas.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_pas = ttk.Entry(frame, width=30, show="*")
    entry_pas.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Кнопка отправки (меньше и справа)
    button = ttk.Button(frame, text="Ок", command=submit, width=10)  # Уменьшаем ширину кнопки
    button.grid(row=2, column=1, padx=5, pady=10, sticky="e")  # Размещаем справа

    # Метка для отображения ошибок
    error_label = ttk.Label(frame, text="", font=("Arial", 12))
    error_label.grid(row=3, column=0, columnspan=2, sticky="ew")

    # Настройка растягивания столбцов и строк
    frame.columnconfigure(1, weight=1)  # Растягиваем второй столбец
    frame.rowconfigure(0, weight=1)     # Растягиваем строки
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
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
# Инициализация интерфейса входа
entry()

# Запуск основного цикла
root.mainloop()
