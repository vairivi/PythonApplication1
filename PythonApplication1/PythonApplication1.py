import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")

        self.movies = []  # список словарей: {"title":..., "genre":..., "year":..., "rating":...}

        self._build_ui()

    def _build_ui(self):
        # Вводная часть: поля
        form_frame = ttk.LabelFrame(self.root, text="Добавить фильм")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Название
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.title_var, width=40).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Жанр
        ttk.Label(form_frame, text="Жанр:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.genre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.genre_var, width=40).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Год выпуска
        ttk.Label(form_frame, text="Год выпуска:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.year_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.year_var, width=20).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Рейтинг
        ttk.Label(form_frame, text="Рейтинг (0-10):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.rating_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.rating_var, width=20).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Кнопка добавления
        add_btn = ttk.Button(form_frame, text="Добавить фильм", command=self.add_movie)
        add_btn.grid(row=4, column=0, columnspan=2, pady=8)

        # Фильтры
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры")
        filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Фильтр по жанру
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.filter_genre_var = tk.StringVar()
        self.filter_genre_var.set("")
        self.genre_filter = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, state="readonly")
        self.genre_filter.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.genre_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Фильтр по году
        ttk.Label(filter_frame, text="Год выпуска:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.filter_year_var = tk.StringVar()
        self.year_filter = ttk.Entry(filter_frame, textvariable=self.filter_year_var, width=10)
        self.year_filter.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.year_filter.bind("<KeyRelease>", lambda e: self.refresh_table())

        # кнопки загрузки/сохранения
        io_frame = ttk.Frame(self.root)
        io_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        save_btn = ttk.Button(io_frame, text="Сохранить в JSON", command=self.save_json)
        save_btn.grid(row=0, column=0, padx=5, pady=5)

        load_btn = ttk.Button(io_frame, text="Загрузить из JSON", command=self.load_json)
        load_btn.grid(row=0, column=1, padx=5, pady=5)

        # Таблица
        table_frame = ttk.LabelFrame(self.root, text="Список фильмов")
        table_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(table_frame, columns=("title", "genre", "year", "rating"), show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")
        self.tree.column("title", width=250)
        self.tree.column("genre", width=120)
        self.tree.column("year", width=60, anchor="center")
        self.tree.column("rating", width=60, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Пример заполнения списка (по желанию оставить пустым)
        self._update_genre_filter_options()

        # Размещение по сетке
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _validate_inputs(self, title, genre, year, rating):
        if not title.strip():
            messagebox.showerror("Ошибка ввода", "Название обязательно.")
            return False
        if not genre.strip():
            messagebox.showerror("Ошибка ввода", "Жанр обязателен.")
            return False
        if not year.isdigit():
            messagebox.showerror("Ошибка ввода", "Год должен быть числом.")
            return False
        try:
            r = float(rating)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Рейтинг должен быть числом от 0 до 10.")
            return False
        if not (0.0 <= r <= 10.0):
            messagebox.showerror("Ошибка ввода", "Рейтинг должен быть в диапазоне 0-10.")
            return False
        return True

    def add_movie(self):
        title = self.title_var.get()
        genre = self.genre_var.get()
        year = self.year_var.get()
        rating = self.rating_var.get()

        if not self._validate_inputs(title, genre, year, rating):
            return

        movie = {
            "title": title.strip(),
            "genre": genre.strip(),
            "year": int(year),
            "rating": float(rating)
        }
        self.movies.append(movie)
        self._clear_input_fields()
        self._update_genre_filter_options()
        self.refresh_table()

    def _clear_input_fields(self):
        self.title_var.set("")
        self.genre_var.set("")
        self.year_var.set("")
        self.rating_var.set("")

    def _update_genre_filter_options(self):
        genres = sorted(set(m["genre"] for m in self.movies))
        # включаем пустой вариант
        options = [""] + genres
        self.genre_filter['values'] = options
        self.filter_genre_var.set("")

    def refresh_table(self):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Фильтрация
        genre_f = self.filter_genre_var.get()
        year_f = self.filter_year_var.get()

        def matches(m):
            if genre_f and m["genre"] != genre_f:
                return False
            if year_f:
                try:
                    if m["year"] != int(year_f):
                        return False
                except ValueError:
                    return False
            return True

        for m in self.movies:
            if matches(m):
                self.tree.insert("", "end", values=(m["title"], m["genre"], m["year"], m["rating"]))

    def save_json(self):
        if not self.movies:
            messagebox.showinfo("Сохранение", "Нет данных для сохранения.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить как"
        )
        if not file_path:
            return
        data = self.movies
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", "Данные сохранены.")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_json(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить из файла"
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # простая проверка структуры
            if isinstance(data, list) and all(isinstance(it, dict) for it in data):
                self.movies = data
                self._update_genre_filter_options()
                self.refresh_table()
                messagebox.showinfo("Загрузка", "Данные успешно загружены.")
            else:
                raise ValueError("Неправильная структура данных.")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

def main():
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
