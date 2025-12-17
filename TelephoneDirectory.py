import sys
import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

# Настройки подключения к базе данных
DB_HOST = "127.0.0.1"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "111111111"


class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=40,
                 color="#3498db", hover_color="#2980b9", text_color="white",
                 font=("Inter", 10, "bold"), corner_radius=10):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=1, bg=parent.cget("bg"))
        self.command = command
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.corner_radius = corner_radius
        self.text = text

        # Создаем прямоугольник с закругленными углами
        self.rect = self.create_rounded_rect(0, 0, width, height, corner_radius, fill=color)
        self.text_id = self.create_text(width / 2, height / 2, text=text,
                                        fill=text_color, font=font)

        # Привязываем события
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
                  x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)

    def on_click(self, event):
        self.move(self.text_id, 1, 1)

    def on_release(self, event):
        self.move(self.text_id, -1, -1)
        if self.command:
            self.command()


class SearchDialog:
    """Диалоговое окно для расширенного поиска"""

    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Расширенный поиск")
        self.top.geometry("500x770")
        self.top.configure(bg='#f8f9fa')
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.result = None
        self.setup_ui()

    def setup_ui(self):
        """Создание интерфейса диалогового окна поиска"""
        # Заголовок
        header = tk.Frame(self.top, bg='#6f42c1', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)

        title = tk.Label(header, text="🔍 Расширенный поиск",
                         font=('Segoe UI', 16, 'bold'),
                         bg='#6f42c1', fg='white')
        title.pack(pady=22)

        # Основной контейнер
        main_container = tk.Frame(self.top, bg='#f8f9fa', padx=25, pady=25)
        main_container.pack(fill='both', expand=True)

        # Стили для элементов
        label_style = {'font': ('Segoe UI', 11), 'bg': '#f8f9fa', 'fg': '#2c3e50', 'anchor': 'w'}
        entry_style = {'font': ('Segoe UI', 11), 'bg': 'white', 'relief': 'solid', 'bd': 1,
                       'highlightthickness': 1, 'highlightcolor': '#3498db', 'highlightbackground': '#ced4da'}

        # Поля для ФИО
        tk.Label(main_container, text="Фамилия:", **label_style).grid(row=0, column=0, sticky='w', pady=8)
        self.fam_entry = tk.Entry(main_container, **entry_style, width=25)
        self.fam_entry.grid(row=0, column=1, sticky='ew', pady=8, padx=(15, 0))

        tk.Label(main_container, text="Имя:", **label_style).grid(row=1, column=0, sticky='w', pady=8)
        self.name_entry = tk.Entry(main_container, **entry_style, width=25)
        self.name_entry.grid(row=1, column=1, sticky='ew', pady=8, padx=(15, 0))

        tk.Label(main_container, text="Отчество:", **label_style).grid(row=2, column=0, sticky='w', pady=8)
        self.otc_entry = tk.Entry(main_container, **entry_style, width=25)
        self.otc_entry.grid(row=2, column=1, sticky='ew', pady=8, padx=(15, 0))

        # Разделитель
        separator1 = tk.Frame(main_container, bg='#dee2e6', height=1)
        separator1.grid(row=3, column=0, columnspan=2, sticky='ew', pady=15)

        # Поля для адреса
        tk.Label(main_container, text="Улица:", **label_style).grid(row=4, column=0, sticky='w', pady=8)
        self.street_entry = tk.Entry(main_container, **entry_style, width=25)
        self.street_entry.grid(row=4, column=1, sticky='ew', pady=8, padx=(15, 0))

        tk.Label(main_container, text="Дом:", **label_style).grid(row=5, column=0, sticky='w', pady=8)
        self.bldn_entry = tk.Entry(main_container, **entry_style, width=25)
        self.bldn_entry.grid(row=5, column=1, sticky='ew', pady=8, padx=(15, 0))

        tk.Label(main_container, text="Корпус:", **label_style).grid(row=6, column=0, sticky='w', pady=8)
        self.bild_k_entry = tk.Entry(main_container, **entry_style, width=25)
        self.bild_k_entry.grid(row=6, column=1, sticky='ew', pady=8, padx=(15, 0))

        tk.Label(main_container, text="Квартира:", **label_style).grid(row=7, column=0, sticky='w', pady=8)
        self.ap_entry = tk.Entry(main_container, **entry_style, width=25)
        self.ap_entry.grid(row=7, column=1, sticky='ew', pady=8, padx=(15, 0))

        # Разделитель
        separator2 = tk.Frame(main_container, bg='#dee2e6', height=1)
        separator2.grid(row=8, column=0, columnspan=2, sticky='ew', pady=15)

        # Поле для телефона
        tk.Label(main_container, text="Телефон:", **label_style).grid(row=9, column=0, sticky='w', pady=8)
        self.teleph_entry = tk.Entry(main_container, **entry_style, width=25)
        self.teleph_entry.grid(row=9, column=1, sticky='ew', pady=8, padx=(15, 0))

        # Подсказка
        hint_label = tk.Label(main_container,
                              text="💡 Подсказка: Введите данные для поиска",
                              font=('Segoe UI', 9), bg='#f8f9fa', fg='#6c757d', justify='left')
        hint_label.grid(row=10, column=0, columnspan=2, sticky='w', pady=(15, 0))

        # Настройка веса колонок для растягивания
        main_container.columnconfigure(1, weight=1)

        # Кнопки
        button_frame = tk.Frame(main_container, bg='#f8f9fa')
        button_frame.grid(row=11, column=0, columnspan=2, sticky='e', pady=(20, 0))

        search_btn = ModernButton(
            button_frame,
            "🔍 Найти",
            command=self.search,
            width=120,
            color="#6f42c1",
            hover_color="#5a2d91"
        )
        search_btn.pack(side='right', padx=(10, 0))

        cancel_btn = ModernButton(
            button_frame,
            "❌ Отмена",
            command=self.cancel,
            width=120,
            color="#6c757d",
            hover_color="#5a6268"
        )
        cancel_btn.pack(side='right')

        # Фокус на первое поле
        self.fam_entry.focus()

    def search(self):
        """Обработка нажатия кнопки поиска"""
        # Собираем все введенные данные
        search_data = {
            'fam': self.fam_entry.get().strip(),
            'name': self.name_entry.get().strip(),
            'otc': self.otc_entry.get().strip(),
            'street': self.street_entry.get().strip(),
            'bldn': self.bldn_entry.get().strip(),
            'bild_k': self.bild_k_entry.get().strip(),
            'ap': self.ap_entry.get().strip(),
            'teleph': self.teleph_entry.get().strip()
        }

        # Проверяем, что хотя бы одно поле заполнено
        if not any(search_data.values()):
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, заполните хотя бы одно поле для поиска")
            return

        self.result = search_data
        self.top.destroy()

    def cancel(self):
        """Отмена поиска"""
        self.result = None
        self.top.destroy()


class DatabaseViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("База данных жильцов - Расширенный интерфейс")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f8f9fa')
        self.center_window()
        self.setup_styles()
        self.setup_ui()
        self.load_data()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def setup_styles(self):
        """Настройка стилей"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Стиль для заголовка
        self.style.configure('Title.TLabel',
                             font=('Inter', 32, 'bold'),
                             background='#1a237e',
                             foreground='white',
                             padding=20)

        # Стиль для информационных меток
        self.style.configure('Info.TLabel',
                             font=('Segoe UI', 10),
                             foreground='#6c757d')

        # Стиль для таблицы
        self.style.configure('Treeview',
                             font=('Segoe UI', 10),
                             rowheight=30,
                             background='white',
                             fieldbackground='white')

        self.style.configure('Treeview.Heading',
                             font=('Segoe UI', 11, 'bold'),
                             background='#34495e',
                             foreground='white',
                             relief='flat')

        self.style.map('Treeview.Heading',
                       background=[('active', '#2c3e50')])

        # Стиль для статусной строки
        self.style.configure('Status.TLabel',
                             font=('Segoe UI', 9),
                             background='#e9ecef',
                             foreground='#495057',
                             relief='sunken',
                             padding=5)

    def setup_ui(self):
        """Создание расширенного интерфейса с кнопкой для управления справочными таблицами"""
        main_container = tk.Frame(self.root, bg='#f8f9fa', padx=20, pady=20)
        main_container.pack(fill='both', expand=True)

        # Заголовок приложения
        header_frame = tk.Frame(main_container, bg='#1a237e', height=120)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = ttk.Label(header_frame, text="🏠 ТЕЛЕФОННЫЙ СПРАВОЧНИК 🌍", style='Title.TLabel')
        title_label.pack(fill='both', expand=True)

        # Панель инструментов с кнопками
        toolbar_frame = tk.Frame(main_container, bg='#ffffff', relief='raised', bd=1)
        toolbar_frame.pack(fill='x', pady=(0, 20))

        button_container = tk.Frame(toolbar_frame, bg='#ffffff', padx=15, pady=15)
        button_container.pack(fill='x')

        # Основные кнопки операций
        self.add_button = ModernButton(button_container, "➕ Добавить", command=self.add_record, color="#28a745",
                                       hover_color="#218838", width=140)
        self.add_button.pack(side='left', padx=(0, 10))

        self.edit_button = ModernButton(button_container, "✏️ Изменить", command=self.edit_record, color="#17a2b8",
                                        hover_color="#138496", width=140)
        self.edit_button.pack(side='left', padx=(0, 10))

        self.delete_button = ModernButton(button_container, "🗑️ Удалить", command=self.delete_record, color="#dc3545",
                                          hover_color="#c82333", width=140)
        self.delete_button.pack(side='left', padx=(0, 10))

        separator1 = tk.Frame(button_container, bg='#dee2e6', width=1, height=30)
        separator1.pack(side='left', padx=20)

        self.search_button = ModernButton(button_container, "🔍 Поиск", command=self.search_record, color="#6f42c1",
                                          hover_color="#5a2d91", width=140)
        self.search_button.pack(side='left', padx=(0, 10))

        separator2 = tk.Frame(button_container, bg='#dee2e6', width=1, height=30)
        separator2.pack(side='left', padx=20)

        self.refresh_button = ModernButton(button_container, "🔄 Обновить", command=self.load_data, color="#fd7e14",
                                           hover_color="#e36209", width=140)
        self.refresh_button.pack(side='left', padx=(0, 10))

        # Кнопка для управления справочными таблицами
        separator3 = tk.Frame(button_container, bg='#dee2e6', width=1, height=30)
        separator3.pack(side='left', padx=20)

        self.reference_button = ModernButton(
            button_container,
            "📚 Справочники",
            command=self.manage_reference_tables,
            color="#20c997",
            hover_color="#1ba87e",
            width=140
        )
        self.reference_button.pack(side='left')

        # Остальная часть UI
        table_container = tk.Frame(main_container, bg='#ffffff', relief='raised', bd=1)
        table_container.pack(fill='both', expand=True, pady=(0, 15))

        table_header = tk.Frame(table_container, bg='#495057', height=40)
        table_header.pack(fill='x')
        table_header.pack_propagate(False)

        table_title = tk.Label(table_header, text="СПИСОК ЖИЛЬЦОВ",
                               font=('Segoe UI', 12, 'bold'),
                               bg='#495057', fg='white')
        table_title.pack(pady=10)

        table_frame = tk.Frame(table_container, bg='#ffffff')
        table_frame.pack(fill='both', expand=True, padx=15, pady=15)

        scrollbar_y = ttk.Scrollbar(table_frame)
        scrollbar_y.pack(side='right', fill='y')

        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')

        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            selectmode='browse',
            show='headings'
        )

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', self.on_double_click)

        bottom_frame = tk.Frame(main_container, bg='#f8f9fa')
        bottom_frame.pack(fill='x')

        self.info_label = ttk.Label(bottom_frame, text="", style='Info.TLabel')
        self.info_label.pack(fill='x', pady=(0, 10))

        status_frame = tk.Frame(bottom_frame, bg='#e9ecef', relief='sunken', bd=1)
        status_frame.pack(fill='x')

        self.status_var = tk.StringVar()
        self.status_var.set("🔄 Подключение к базе данных...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.pack(fill='x', padx=10, pady=5)

    def execute_query(self, cmd, params=None, fetch=False):
        """Безопасное выполнение SQL-запросов"""
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            cur = conn.cursor()

            if params:
                cur.execute(cmd, params)
            else:
                cur.execute(cmd)

            if fetch or cur.description:
                rows = cur.fetchall()
                conn.commit()
                return rows
            else:
                conn.commit()
                return True

        except Exception as e:
            error_msg = f"Ошибка базы данных:\n{str(e)}"
            messagebox.showerror("Ошибка подключения", error_msg)
            print(f"Database error: {e}")
            return None
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    def load_data(self):
        """Загрузка данных из базы и отображение в таблице"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
        SELECT main.uniq_id, fam.f_val, name.n_val, otc.o_val, street.s_val, 
               main.bldn, main.bild_k, main.ap, main.teleph
        FROM main
        JOIN fam ON main.fam = fam.f_id
        JOIN name ON main.name = name.n_id
        JOIN otc ON main.otc = otc.o_id
        JOIN street ON main.street = street.s_id
        ORDER BY main.uniq_id
        """

        data = self.execute_query(query)

        if data is None:
            self.status_var.set("❌ Ошибка загрузки данных! Проверьте соединение с базой.")
            return

        if not data:
            self.status_var.set("ℹ️ Нет данных в базе")
            self.info_label.config(text="База данных пуста. Добавьте записи через интерфейс.")
            return

        columns = ["ID", "Фамилия", "Имя", "Отчество", "Улица", "Дом", "Корп.", "Кв.", "Телефон"]
        self.tree['columns'] = columns

        column_widths = {
            "ID": 60, "Фамилия": 150, "Имя": 150, "Отчество": 150, "Улица": 200,
            "Дом": 80, "Корп.": 80, "Кв.": 80, "Телефон": 150
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')

        for row in data:
            formatted_row = [str(item) if item is not None else "" for item in row]
            self.tree.insert("", "end", values=formatted_row)

        current_time = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        self.info_label.config(
            text=f"📊 Загружено записей: {len(data)} | ⏰ Последнее обновление: {current_time}"
        )
        self.status_var.set(f"✅ Успешно загружено {len(data)} записей | Двойной клик по строке для просмотра деталей")

    def get_or_create_id(self, table, value_column, id_column, value):
        """Универсальный метод для получения или создания ID в справочных таблицах"""
        if not value:
            return None

        # Ищем существующую запись
        query = f"SELECT {id_column} FROM {table} WHERE {value_column} = %s"
        result = self.execute_query(query, (value,), fetch=True)

        if result and len(result) > 0:
            return result[0][0]  # Возвращаем существующий ID
        else:
            # Создаем новую запись только если значения нет
            insert_query = f"INSERT INTO {table} ({value_column}) VALUES (%s) RETURNING {id_column}"
            insert_result = self.execute_query(insert_query, (value,), fetch=True)
            if insert_result and len(insert_result) > 0:
                return insert_result[0][0]
        return None

    def update_reference_record(self, table, value_column, id_column, old_id, new_value):
        #  ИЗМЕНЕНИЕ  """Обновляет запись в справочной таблице или создает новую"""
        if not new_value:
            return None

        # Если old_id не передан, просто создаем/получаем новую запись
        if old_id is None:
            return self.get_or_create_id(table, value_column, id_column, new_value)

        # Получаем старое значение
        old_value_query = f"SELECT {value_column} FROM {table} WHERE {id_column} = %s"
        old_value_result = self.execute_query(old_value_query, (old_id,), fetch=True)

        if not old_value_result:
            return self.get_or_create_id(table, value_column, id_column, new_value)

        old_value = old_value_result[0][0]

        # Если значение не изменилось, возвращаем старый ID
        if old_value == new_value:
            return old_id

        # Ищем, есть ли уже такое значение в таблице
        existing_query = f"SELECT {id_column} FROM {table} WHERE {value_column} = %s"
        existing_result = self.execute_query(existing_query, (new_value,), fetch=True)

        if existing_result and len(existing_result) > 0:
            new_id = existing_result[0][0]
            # Возвращаем существующий ID, не трогаем старую запись
            return new_id
        else:
            # Создаем новую запись для нового значения
            return self.get_or_create_id(table, value_column, id_column, new_value)

    def cleanup_unused_reference(self, table, id_column, record_id):
        """Удаляет запись из справочной таблицы, если она больше не используется в основной таблице"""
        if record_id is None:
            return

        # Проверяем, используется ли еще эта запись в основной таблице
        column_map = {
            'fam': 'fam',
            'name': 'name',
            'otc': 'otc',
            'street': 'street'
        }

        main_column = column_map.get(table)
        if not main_column:
            return

        check_query = f"SELECT COUNT(*) FROM main WHERE {main_column} = %s"
        count_result = self.execute_query(check_query, (record_id,), fetch=True)

        if count_result and count_result[0][0] == 0:
            # Если больше не используется, удаляем из справочной таблицы
            delete_query = f"DELETE FROM {table} WHERE {id_column} = %s"
            self.execute_query(delete_query, (record_id,))
            print(f"Удалена неиспользуемая запись из {table} с ID: {record_id}")

    def get_next_id(self):
        """Получаем следующий доступный ID"""
        query = "SELECT COALESCE(MAX(uniq_id), 0) + 1 FROM main"
        result = self.execute_query(query, fetch=True)
        return result[0][0] if result else 1

    def add_record(self):
        """Добавление новой записи в базу данных"""
        dialog = ModernAddEditDialog(self.root, "Добавление записи")
        self.root.wait_window(dialog.top)

        if dialog.result:
            try:
                data = dialog.result

                # Получаем или создаем ID для справочных таблиц
                fam_id = self.get_or_create_id("fam", "f_val", "f_id", data['fam'])
                name_id = self.get_or_create_id("name", "n_val", "n_id", data['name'])
                otc_id = self.get_or_create_id("otc", "o_val", "o_id", data['otc'])
                street_id = self.get_or_create_id("street", "s_val", "s_id", data['street'])

                # Преобразуем числовые значения
                bldn = int(data['bldn']) if data['bldn'] else None
                bild_k = int(data['bild_k']) if data['bild_k'] else None
                ap = int(data['ap']) if data['ap'] else None

                # Получаем следующий ID
                new_id = self.get_next_id()

                # Вставляем запись в основную таблицу
                query = """
                INSERT INTO main (uniq_id, fam, name, otc, street, bldn, bild_k, ap, teleph)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (new_id, fam_id, name_id, otc_id, street_id, bldn, bild_k, ap, data['teleph'])

                result = self.execute_query(query, params)
                if result:
                    messagebox.showinfo("Успех", f"✅ Запись успешно добавлена в базу данных с ID: {new_id}!")
                    self.load_data()
                else:
                    messagebox.showerror("Ошибка", "❌ Не удалось добавить запись в базу данных")

            except Exception as e:
                messagebox.showerror("Ошибка", f"❌ Ошибка при добавлении записи: {str(e)}")

    def edit_record(self):
        """Редактирование выбранной записи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, выберите запись для редактирования")
            return

        # Получаем данные выбранной записи
        item = self.tree.item(selection[0])
        values = item['values']

        # Получаем текущие ID из справочных таблиц для этой записи
        current_refs_query = "SELECT fam, name, otc, street FROM main WHERE uniq_id = %s"
        current_refs_result = self.execute_query(current_refs_query, (values[0],), fetch=True)

        if not current_refs_result:
            messagebox.showerror("Ошибка", "❌ Не удалось найти запись для редактирования")
            return

        current_fam_id, current_name_id, current_otc_id, current_street_id = current_refs_result[0]

        # Создаем диалоговое окно для редактирования
        dialog = ModernAddEditDialog(self.root, "Редактирование записи", values)
        self.root.wait_window(dialog.top)

        if dialog.result:
            try:
                data = dialog.result

                # ВАЖНО: Всегда создаем/получаем новые ID для измененных значений
                # Это гарантирует, что изменение одной записи не затронет другие
                fam_id = self.get_or_create_id("fam", "f_val", "f_id", data['fam'])
                name_id = self.get_or_create_id("name", "n_val", "n_id", data['name'])
                otc_id = self.get_or_create_id("otc", "o_val", "o_id", data['otc'])
                street_id = self.get_or_create_id("street", "s_val", "s_id", data['street'])

                # Преобразуем числовые значения
                bldn = int(data['bldn']) if data['bldn'] else None
                bild_k = int(data['bild_k']) if data['bild_k'] else None
                ap = int(data['ap']) if data['ap'] else None

                # Обновляем запись в основной таблице
                query = """
                UPDATE main 
                SET fam = %s, name = %s, otc = %s, street = %s, 
                    bldn = %s, bild_k = %s, ap = %s, teleph = %s
                WHERE uniq_id = %s
                """
                params = (fam_id, name_id, otc_id, street_id, bldn,
                          bild_k, ap, data['teleph'], values[0])

                result = self.execute_query(query, params)
                if result:
                    # Очищаем неиспользуемые старые значения из справочных таблиц
                    # Только если они действительно больше нигде не используются
                    self.cleanup_unused_reference('fam', 'f_id', current_fam_id)
                    self.cleanup_unused_reference('name', 'n_id', current_name_id)
                    self.cleanup_unused_reference('otc', 'o_id', current_otc_id)
                    self.cleanup_unused_reference('street', 's_id', current_street_id)

                    messagebox.showinfo("Успех", "✅ Запись успешно обновлена в базе данных!")
                    self.load_data()
                else:
                    messagebox.showerror("Ошибка", "❌ Не удалось обновить запись в базе данных")

            except Exception as e:
                messagebox.showerror("Ошибка", f"❌ Ошибка при обновлении записи: {str(e)}")

    def delete_record(self):
        """Удаление выбранной записи из базы данных с каскадным удалением неиспользуемых значений"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, выберите запись для удаления")
            return

        item = self.tree.item(selection[0])
        values = item['values']

        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("Подтверждение удаления")
        confirm_window.geometry("700x450")
        confirm_window.configure(bg='#f8f9fa')
        confirm_window.resizable(False, False)
        confirm_window.transient(self.root)
        confirm_window.grab_set()

        header = tk.Frame(confirm_window, bg='#dc3545', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        title = tk.Label(header, text="🗑️ Подтверждение удаления",
                         font=('Segoe UI', 16, 'bold'),
                         bg='#dc3545', fg='white')
        title.pack(pady=18)

        info_frame = tk.Frame(confirm_window, bg='#f8f9fa', padx=20, pady=20)
        info_frame.pack(fill='both', expand=True)

        confirm_text = f"""
Вы уверены, что хотите удалить запись с ID: {values[0]}?

👤 ФИО: {values[1]} {values[2]} {values[3]}

🏠 Адрес: ул. {values[4]}, д. {values[5]}, кв. {values[7]}

Это действие нельзя отменить!
        """

        info_label = tk.Label(info_frame, text=confirm_text,
                              font=('Segoe UI', 11),
                              bg='#f8f9fa', fg='#2c3e50',
                              justify='left')
        info_label.pack(anchor='w', pady=(0, 20))

        button_frame = tk.Frame(info_frame, bg='#f8f9fa')
        button_frame.pack(fill='x')

        def confirm_delete():
            try:
                # Сначала получаем ID связанных записей из справочных таблиц
                query_get_refs = """
                SELECT fam, name, otc, street FROM main WHERE uniq_id = %s
                """
                refs_result = self.execute_query(query_get_refs, (values[0],), fetch=True)

                if not refs_result:
                    messagebox.showerror("Ошибка", "❌ Не удалось найти запись для удаления")
                    confirm_window.destroy()
                    return

                fam_id, name_id, otc_id, street_id = refs_result[0]

                # Удаляем запись из основной таблицы
                query = "DELETE FROM main WHERE uniq_id = %s"
                delete_result = self.execute_query(query, (values[0],))

                if delete_result:
                    # КАСКАДНОЕ УДАЛЕНИЕ: проверяем и удаляем неиспользуемые значения из справочных таблиц
                    self.cleanup_unused_reference('fam', 'f_id', fam_id)
                    self.cleanup_unused_reference('name', 'n_id', name_id)
                    self.cleanup_unused_reference('otc', 'o_id', otc_id)
                    self.cleanup_unused_reference('street', 's_id', street_id)

                    messagebox.showinfo("Успех", "✅ Запись успешно удалена из базы данных!")
                    confirm_window.destroy()
                    self.load_data()
                else:
                    messagebox.showerror("Ошибка", "❌ Не удалось удалить запись из базы данных")
                    confirm_window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"❌ Ошибка при удалении записи: {str(e)}")
                confirm_window.destroy()

        delete_btn = ModernButton(
            button_frame,
            "🗑️ Удалить",
            command=confirm_delete,
            width=120,
            color="#dc3545",
            hover_color="#c82333"
        )
        delete_btn.pack(side='right', padx=(10, 0))

        cancel_btn = ModernButton(
            button_frame,
            "Отмена",
            command=confirm_window.destroy,
            width=120,
            color="#6c757d",
            hover_color="#5a6268"
        )
        cancel_btn.pack(side='right')

    def search_record(self):
        """Поиск записей по заданным критериям"""
        search_dialog = SearchDialog(self.root)
        self.root.wait_window(search_dialog.top)

        if search_dialog.result:
            self._perform_advanced_search(search_dialog.result)

    def _perform_advanced_search(self, search_data):
        """Выполняет расширенный поиск по заданным критериям"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Базовый запрос
        query = """
        SELECT main.uniq_id, fam.f_val, name.n_val, otc.o_val, street.s_val, 
               main.bldn, main.bild_k, main.ap, main.teleph
        FROM main
        JOIN fam ON main.fam = fam.f_id
        JOIN name ON main.name = name.n_id
        JOIN otc ON main.otc = otc.o_id
        JOIN street ON main.street = street.s_id
        WHERE 1=1
        """

        params = []

        # Добавляем условия для каждого заполненного поля
        conditions = []

        if search_data['fam']:
            conditions.append("fam.f_val ILIKE %s")
            params.append(f"%{search_data['fam']}%")

        if search_data['name']:
            conditions.append("name.n_val ILIKE %s")
            params.append(f"%{search_data['name']}%")

        if search_data['otc']:
            conditions.append("otc.o_val ILIKE %s")
            params.append(f"%{search_data['otc']}%")

        if search_data['street']:
            conditions.append("street.s_val ILIKE %s")
            params.append(f"%{search_data['street']}%")

        if search_data['bldn']:
            conditions.append("CAST(main.bldn AS TEXT) ILIKE %s")
            params.append(f"%{search_data['bldn']}%")

        if search_data['bild_k']:
            conditions.append("CAST(main.bild_k AS TEXT) ILIKE %s")
            params.append(f"%{search_data['bild_k']}%")

        if search_data['ap']:
            conditions.append("CAST(main.ap AS TEXT) ILIKE %s")
            params.append(f"%{search_data['ap']}%")

        if search_data['teleph']:
            conditions.append("main.teleph ILIKE %s")
            params.append(f"%{search_data['teleph']}%")

        # Если есть условия, добавляем их к запросу
        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += " ORDER BY main.uniq_id"

        data = self.execute_query(query, params)

        if data is None:
            self.status_var.set("❌ Ошибка поиска!")
            return

        if not data:
            self.status_var.set("🔍 По вашему запросу ничего не найдено")

            # Формируем текст поискового запроса
            search_terms = []
            for field, value in search_data.items():
                if value:
                    field_names = {
                        'fam': 'Фамилия', 'name': 'Имя', 'otc': 'Отчество',
                        'street': 'Улица', 'bldn': 'Дом', 'bild_k': 'Корпус',
                        'ap': 'Квартира', 'teleph': 'Телефон'
                    }
                    search_terms.append(f"{field_names[field]}: '{value}'")

            search_text = " | ".join(search_terms)
            self.info_label.config(text=f"🔍 По запросу ({search_text}) ничего не найдено")
            return

        columns = ["ID", "Фамилия", "Имя", "Отчество", "Улица", "Дом", "Корп.", "Кв.", "Телефон"]
        self.tree['columns'] = columns

        column_widths = {
            "ID": 60, "Фамилия": 150, "Имя": 150, "Отчество": 150, "Улица": 200,
            "Дом": 80, "Корп.": 80, "Кв.": 80, "Телефон": 150
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')

        for row in data:
            formatted_row = [str(item) if item is not None else "" for item in row]
            self.tree.insert("", "end", values=formatted_row)

        # Формируем текст поискового запроса для отображения
        search_terms = []
        for field, value in search_data.items():
            if value:
                field_names = {
                    'fam': 'Фамилия', 'name': 'Имя', 'otc': 'Отчество',
                    'street': 'Улица', 'bldn': 'Дом', 'bild_k': 'Корпус',
                    'ap': 'Квартира', 'teleph': 'Телефон'
                }
                search_terms.append(f"{field_names[field]}: '{value}'")

        search_text = " | ".join(search_terms)
        current_time = datetime.now().strftime("%H:%M:%S %d.%m.%Y")

        self.info_label.config(
            text=f"🔍 Найдено записей: {len(data)} | Критерии: {search_text} | Обновлено: {current_time}"
        )
        self.status_var.set(f"🔍 Найдено {len(data)} записей по заданным критериям")

    def manage_reference_tables(self):
        """Управление справочными таблицами (fam, name, otc, street)"""
        ReferenceTablesManager(self.root)

    def on_double_click(self, event):
        """Обработка двойного клика по строке таблицы"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']

            if values:
                detail_window = tk.Toplevel(self.root)
                detail_window.title("Детали записи")
                detail_window.geometry("400x300")
                detail_window.configure(bg='#f8f9fa')
                detail_window.resizable(False, False)
                detail_window.transient(self.root)
                detail_window.grab_set()

                header = tk.Frame(detail_window, bg='#3498db', height=60)
                header.pack(fill='x')
                header.pack_propagate(False)

                title = tk.Label(header, text="👤 Детали записи",
                                 font=('Segoe UI', 16, 'bold'),
                                 bg='#3498db', fg='white')
                title.pack(pady=18)

                info_frame = tk.Frame(detail_window, bg='#f8f9fa', padx=20, pady=20)
                info_frame.pack(fill='both', expand=True)

                info_text = f"""
📋 ID записи: {values[0]}

👤 ФИО: {values[1]} {values[2]} {values[3]}

🏠 Адрес: ул. {values[4]}, д. {values[5]}, корп. {values[6]}, кв. {values[7]}

📞 Телефон: {values[8]}
                """

                info_label = tk.Label(info_frame, text=info_text,
                                      font=('Segoe UI', 11),
                                      bg='#f8f9fa', fg='#2c3e50',
                                      justify='left')
                info_label.pack(anchor='w')

                close_btn = ModernButton(
                    info_frame,
                    "Закрыть",
                    command=detail_window.destroy,
                    width=120,
                    color="#6c757d",
                    hover_color="#5a6268"
                )
                close_btn.pack(pady=(20, 0))

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


class ReferenceTablesManager:
    """Класс для управления справочными таблицами (fam, name, otc, street)"""

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Управление справочными таблицами")
        self.window.geometry("1000x750")
        self.window.configure(bg='#f8f9fa')
        self.window.transient(parent)
        self.window.grab_set()

        self.center_window()
        self.setup_ui()
        self.load_reference_data()

    def center_window(self):
        """Центрирует окно на экране"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def setup_ui(self):
        """Создает интерфейс для управления справочными таблицами"""
        main_container = tk.Frame(self.window, bg='#f8f9fa', padx=20, pady=20)
        main_container.pack(fill='both', expand=True)

        # Заголовок
        header_frame = tk.Frame(main_container, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="📚 УПРАВЛЕНИЕ СПРАВОЧНЫМИ ТАБЛИЦАМИ",
                               font=('Segoe UI', 18, 'bold'),
                               bg='#2c3e50', fg='white')
        title_label.pack(pady=25)

        # Панель инструментов с кнопкой обновить
        toolbar_frame = tk.Frame(main_container, bg='#ffffff', relief='raised', bd=1)
        toolbar_frame.pack(fill='x', pady=(0, 10))

        button_container = tk.Frame(toolbar_frame, bg='#ffffff', padx=10, pady=10)
        button_container.pack(fill='x')

        refresh_btn = ModernButton(
            button_container,
            "🔄 Обновить все",
            command=self.load_reference_data,
            width=140,
            color="#fd7e14",
            hover_color="#e36209"
        )
        refresh_btn.pack(side='left')

        # Создаем вкладки для каждой таблицы
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill='both', expand=True)

        # Создаем фреймы для каждой таблицы
        self.fam_frame = self.create_tab(notebook, "Фамилии", "fam")
        self.name_frame = self.create_tab(notebook, "Имена", "name")
        self.otc_frame = self.create_tab(notebook, "Отчества", "otc")
        self.street_frame = self.create_tab(notebook, "Улицы", "street")

        notebook.add(self.fam_frame, text="Фамилии")
        notebook.add(self.name_frame, text="Имена")
        notebook.add(self.otc_frame, text="Отчества")
        notebook.add(self.street_frame, text="Улицы")

    def create_tab(self, notebook, title, table_name):
        """Создает вкладку для указанной таблицы"""
        frame = tk.Frame(notebook, bg='#f8f9fa')

        # Заголовок вкладки
        tab_header = tk.Frame(frame, bg='#495057', height=40)
        tab_header.pack(fill='x', pady=(0, 10))
        tab_header.pack_propagate(False)

        tab_title = tk.Label(tab_header, text=title,
                             font=('Segoe UI', 12, 'bold'),
                             bg='#495057', fg='white')
        tab_title.pack(pady=10)

        # Фрейм для таблицы
        table_container = tk.Frame(frame, bg='#ffffff', relief='raised', bd=1)
        table_container.pack(fill='both', expand=True, pady=(0, 10))

        # Создаем Treeview
        table_frame = tk.Frame(table_container, bg='#ffffff')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        scrollbar_y = ttk.Scrollbar(table_frame)
        scrollbar_y.pack(side='right', fill='y')

        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')

        # Определяем колонки в зависимости от таблицы
        if table_name == "fam":
            columns = ["ID", "Фамилия"]
            column_widths = {"ID": 80, "Фамилия": 300}
        elif table_name == "name":
            columns = ["ID", "Имя"]
            column_widths = {"ID": 80, "Имя": 300}
        elif table_name == "otc":
            columns = ["ID", "Отчество"]
            column_widths = {"ID": 80, "Отчество": 300}
        else:  # street
            columns = ["ID", "Улица"]
            column_widths = {"ID": 80, "Улица": 400}

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            selectmode='browse',
            show='headings'
        )

        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)

        for col in columns:
            tree.heading(col, text=col, anchor='center')
            tree.column(col, width=column_widths.get(col, 200), anchor='center')

        tree.pack(fill='both', expand=True)

        # Сохраняем ссылку на treeview
        setattr(self, f"{table_name}_tree", tree)

        # Кнопки управления
        button_frame = tk.Frame(frame, bg='#f8f9fa')
        button_frame.pack(fill='x')

        add_btn = ModernButton(
            button_frame,
            "➕ Добавить",
            command=lambda: self.add_reference_record(table_name),
            width=120,
            color="#28a745",
            hover_color="#218838"
        )
        add_btn.pack(side='left', padx=(0, 10))

        edit_btn = ModernButton(
            button_frame,
            "✏️ Изменить",
            command=lambda: self.edit_reference_record(table_name),
            width=120,
            color="#17a2b8",
            hover_color="#138496"
        )
        edit_btn.pack(side='left', padx=(0, 10))

        delete_btn = ModernButton(
            button_frame,
            "🗑️ Удалить",
            command=lambda: self.delete_reference_record(table_name),
            width=120,
            color="#dc3545",
            hover_color="#c82333"
        )
        delete_btn.pack(side='left', padx=(0, 10))

        refresh_btn = ModernButton(
            button_frame,
            "🔄 Обновить",
            command=lambda: self.refresh_single_table(table_name),
            width=120,
            color="#fd7e14",
            hover_color="#e36209"
        )
        refresh_btn.pack(side='left')

        return frame

    def execute_query(self, cmd, params=None, fetch=False):
        """Безопасное выполнение SQL-запросов (аналогично методу в DatabaseViewer)"""
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            cur = conn.cursor()

            if params:
                cur.execute(cmd, params)
            else:
                cur.execute(cmd)

            if fetch or cur.description:
                rows = cur.fetchall()
                conn.commit()
                return rows
            else:
                conn.commit()
                return True

        except Exception as e:
            error_msg = f"Ошибка базы данных:\n{str(e)}"
            messagebox.showerror("Ошибка подключения", error_msg)
            print(f"Database error: {e}")
            return None
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    def load_reference_data(self):
        """Загружает данные из всех справочных таблиц"""
        tables = {
            "fam": ("f_id", "f_val"),
            "name": ("n_id", "n_val"),
            "otc": ("o_id", "o_val"),
            "street": ("s_id", "s_val")
        }

        for table_name, (id_col, val_col) in tables.items():
            tree = getattr(self, f"{table_name}_tree")

            # Очищаем существующие данные
            for item in tree.get_children():
                tree.delete(item)

            # Загружаем данные
            query = f"SELECT {id_col}, {val_col} FROM {table_name} ORDER BY {id_col}"
            data = self.execute_query(query, fetch=True)

            if data:
                for row in data:
                    tree.insert("", "end", values=row)

    def refresh_single_table(self, table_name):
        """Обновляет данные только в одной таблице"""
        tables = {
            "fam": ("f_id", "f_val"),
            "name": ("n_id", "n_val"),
            "otc": ("o_id", "o_val"),
            "street": ("s_id", "s_val")
        }

        if table_name in tables:
            id_col, val_col = tables[table_name]
            tree = getattr(self, f"{table_name}_tree")

            # Очищаем существующие данные
            for item in tree.get_children():
                tree.delete(item)

            # Загружаем данные
            query = f"SELECT {id_col}, {val_col} FROM {table_name} ORDER BY {id_col}"
            data = self.execute_query(query, fetch=True)

            if data:
                for row in data:
                    tree.insert("", "end", values=row)
            messagebox.showinfo("Успех", f"✅ Таблица {self.get_table_name_russian(table_name)} успешно обновлена!")
        else:
            messagebox.showerror("Ошибка", f"❌ Неизвестная таблица: {table_name}")

    def add_reference_record(self, table_name):
        """Добавляет новую запись в справочную таблицу"""
        # Определяем название поля в зависимости от таблицы
        field_names = {
            "fam": "фамилию",
            "name": "имя",
            "otc": "отчество",
            "street": "название улицы"
        }

        value = simpledialog.askstring("Добавление", f"Введите {field_names[table_name]}:")
        if value:
            # Определяем структуру таблицы
            tables = {
                "fam": ("f_val",),
                "name": ("n_val",),
                "otc": ("o_val",),
                "street": ("s_val",)
            }

            column = tables[table_name][0]
            query = f"INSERT INTO {table_name} ({column}) VALUES (%s)"
            result = self.execute_query(query, (value,))

            if result:
                messagebox.showinfo("Успех", "✅ Запись успешно добавлена!")
                self.refresh_single_table(table_name)
            else:
                messagebox.showerror("Ошибка", "❌ Не удалось добавить запись")

    def edit_reference_record(self, table_name):
        """Редактирует выбранную запись в справочной таблице"""
        tree = getattr(self, f"{table_name}_tree")
        selection = tree.selection()

        if not selection:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, выберите запись для редактирования")
            return

        item = tree.item(selection[0])
        record_id, old_value = item['values']

        field_names = {
            "fam": "фамилию",
            "name": "имя",
            "otc": "отчество",
            "street": "название улицы"
        }

        new_value = simpledialog.askstring("Редактирование",
                                           f"Введите новое значение для {field_names[table_name]}:",
                                           initialvalue=old_value)
        if new_value and new_value != old_value:
            tables = {
                "fam": ("f_val", "f_id"),
                "name": ("n_val", "n_id"),
                "otc": ("o_val", "o_id"),
                "street": ("s_val", "s_id")
            }

            val_col, id_col = tables[table_name]
            query = f"UPDATE {table_name} SET {val_col} = %s WHERE {id_col} = %s"
            result = self.execute_query(query, (new_value, record_id))

            if result:
                messagebox.showinfo("Успех", "✅ Запись успешно обновлена!")
                self.refresh_single_table(table_name)
            else:
                messagebox.showerror("Ошибка", "❌ Не удалось обновить запись")

    def delete_reference_record(self, table_name):
        """Удаляет выбранную запись из справочной таблицы"""
        tree = getattr(self, f"{table_name}_tree")
        selection = tree.selection()

        if not selection:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, выберите запись для удаления")
            return

        item = tree.item(selection[0])
        record_id, value = item['values']

        # Проверяем, используется ли запись в основной таблице
        field_map = {
            "fam": "fam",
            "name": "name",
            "otc": "otc",
            "street": "street"
        }

        main_field = field_map[table_name]
        check_query = f"SELECT COUNT(*) FROM main WHERE {main_field} = %s"
        count_result = self.execute_query(check_query, (record_id,), fetch=True)

        if count_result and count_result[0][0] > 0:
            messagebox.showerror("Ошибка",
                                 f"❌ Нельзя удалить запись! Эта {self.get_table_name_russian(table_name)} используется в основной таблице.")
            return

        # Подтверждение удаления
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить {self.get_table_name_russian(table_name).lower()} '{value}'?"
        )

        if confirm:
            tables = {
                "fam": "f_id",
                "name": "n_id",
                "otc": "o_id",
                "street": "s_id"
            }

            id_col = tables[table_name]
            query = f"DELETE FROM {table_name} WHERE {id_col} = %s"
            result = self.execute_query(query, (record_id,))

            if result:
                messagebox.showinfo("Успех", "✅ Запись успешно удалена!")
                self.refresh_single_table(table_name)
            else:
                messagebox.showerror("Ошибка", "❌ Не удалось удалить запись")

    def get_table_name_russian(self, table_name):
        """Возвращает русское название таблицы"""
        names = {
            "fam": "Фамилию",
            "name": "Имя",
            "otc": "Отчество",
            "street": "Улицу"
        }
        return names.get(table_name, "Запись")


class ModernAddEditDialog:
    """Современное диалоговое окно для добавления/редактирования записей"""

    def __init__(self, parent, title, values=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x650")
        self.top.configure(bg='#f8f9fa')
        self.top.resizable(False, False)

        # Центрируем окно
        self.top.transient(parent)
        self.top.grab_set()

        self.result = None

        # Заголовок
        header = tk.Frame(self.top, bg='#3498db', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=title, font=('Segoe UI', 18, 'bold'),
                               bg='#3498db', fg='white')
        title_label.pack(pady=25)

        # Основной контейнер
        main_container = tk.Frame(self.top, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True)

        # Фрейм для полей ввода
        form_frame = tk.Frame(main_container, bg='#f8f9fa', padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)

        # Стиль для полей ввода
        entry_style = {'font': ('Segoe UI', 11), 'bg': 'white', 'relief': 'solid',
                       'bd': 1, 'highlightthickness': 1, 'highlightcolor': '#3498db',
                       'highlightbackground': '#ced4da'}

        label_style = {'font': ('Segoe UI', 11, 'bold'), 'bg': '#f8f9fa', 'fg': '#2c3e50'}

        # Поля ввода
        tk.Label(form_frame, text="Фамилия:*", **label_style).grid(row=0, column=0, sticky='w', pady=12)
        self.fam_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.fam_entry.grid(row=0, column=1, sticky='ew', pady=12, padx=(15, 0))

        tk.Label(form_frame, text="Имя:*", **label_style).grid(row=1, column=0, sticky='w', pady=12)
        self.name_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.name_entry.grid(row=1, column=1, sticky='ew', pady=12, padx=(15, 0))

        tk.Label(form_frame, text="Отчество:", **label_style).grid(row=2, column=0, sticky='w', pady=12)
        self.otc_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.otc_entry.grid(row=2, column=1, sticky='ew', pady=12, padx=(15, 0))

        tk.Label(form_frame, text="Улица:*", **label_style).grid(row=3, column=0, sticky='w', pady=12)
        self.street_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.street_entry.grid(row=3, column=1, sticky='ew', pady=12, padx=(15, 0))

        tk.Label(form_frame, text="Дом:*", **label_style).grid(row=4, column=0, sticky='w', pady=12)
        self.bldn_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.bldn_entry.grid(row=4, column=1, sticky='ew', pady=12, padx=(15, 0))

        tk.Label(form_frame, text="Корпус:", **label_style).grid(row=5, column=0, sticky='w', pady=12)
        self.bild_k_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.bild_k_entry.grid(row=5, column=1, sticky='ew', pady=12, padx=(15, 0))

        tk.Label(form_frame, text="Квартира:", **label_style).grid(row=6, column=0, sticky='w', pady=12)
        self.ap_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.ap_entry.grid(row=6, column=1, sticky='ew', pady=12, padx=(15, 0))

        tk.Label(form_frame, text="Телефон:", **label_style).grid(row=7, column=0, sticky='w', pady=12)
        self.teleph_entry = tk.Entry(form_frame, **entry_style, width=30)
        self.teleph_entry.grid(row=7, column=1, sticky='ew', pady=12, padx=(15, 0))

        # Если переданы значения (режим редактирования), заполняем поля
        if values:
            self.fam_entry.insert(0, values[1] if len(values) > 1 else "")
            self.name_entry.insert(0, values[2] if len(values) > 2 else "")
            self.otc_entry.insert(0, values[3] if len(values) > 3 else "")
            self.street_entry.insert(0, values[4] if len(values) > 4 else "")
            self.bldn_entry.insert(0, values[5] if len(values) > 5 else "")
            self.bild_k_entry.insert(0, values[6] if len(values) > 6 else "")
            self.ap_entry.insert(0, values[7] if len(values) > 7 else "")
            self.teleph_entry.insert(0, values[8] if len(values) > 8 else "")

        # Подсказка об обязательных полях
        hint_label = tk.Label(form_frame, text="* - обязательные поля",
                              font=('Segoe UI', 9), bg='#f8f9fa', fg='#6c757d')
        hint_label.grid(row=8, column=0, columnspan=2, sticky='w', pady=(20, 0))

        # Настройка веса колонок для растягивания
        form_frame.columnconfigure(1, weight=1)

        # Кнопки в отдельном фрейме внизу
        button_frame = tk.Frame(self.top, bg='#f8f9fa', padx=30, pady=20)
        button_frame.pack(fill='x', side='bottom')

        save_btn = ModernButton(
            button_frame,
            "💾 Сохранить",
            command=self.save,
            width=140,
            color="#28a745",
            hover_color="#218838"
        )
        save_btn.pack(side='right', padx=(10, 0))

        cancel_btn = ModernButton(
            button_frame,
            "❌ Отмена",
            command=self.cancel,
            width=140,
            color="#6c757d",
            hover_color="#5a6268"
        )
        cancel_btn.pack(side='right')

        # Фокус на первое поле
        self.fam_entry.focus()

    def save(self):
        """Сохранение данных"""
        # Получаем значения из полей ввода
        fam = self.fam_entry.get().strip()
        name = self.name_entry.get().strip()
        otc = self.otc_entry.get().strip()
        street = self.street_entry.get().strip()
        bldn = self.bldn_entry.get().strip()
        bild_k = self.bild_k_entry.get().strip()
        ap = self.ap_entry.get().strip()
        teleph = self.teleph_entry.get().strip()

        # Проверяем обязательные поля
        if not fam:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, введите фамилию")
            self.fam_entry.focus()
            return

        if not name:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, введите имя")
            self.name_entry.focus()
            return

        if not street:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, введите улицу")
            self.street_entry.focus()
            return

        if not bldn:
            messagebox.showwarning("Предупреждение", "⚠️ Пожалуйста, введите номер дома")
            self.bldn_entry.focus()
            return

        # Проверяем числовые поля
        try:
            if bldn and not bldn.isdigit():
                messagebox.showwarning("Предупреждение", "❌ Номер дома должен быть числом")
                self.bldn_entry.focus()
                return

            if bild_k and not bild_k.isdigit():
                messagebox.showwarning("Предупреждение", "❌ Корпус должен быть числом")
                self.bild_k_entry.focus()
                return

            if ap and not ap.isdigit():
                messagebox.showwarning("Предупреждение", "❌ Номер квартиры должен быть числом")
                self.ap_entry.focus()
                return

        except ValueError:
            messagebox.showwarning("Предупреждение", "❌ Проверьте правильность ввода числовых полей")
            return

        # Формируем результат
        self.result = {
            'fam': fam,
            'name': name,
            'otc': otc,
            'street': street,
            'bldn': bldn,
            'bild_k': bild_k,
            'ap': ap,
            'teleph': teleph
        }

        self.top.destroy()

    def cancel(self):
        """Отмена операции"""
        self.result = None
        self.top.destroy()


if __name__ == "__main__":
    app = DatabaseViewer()
    app.run()
