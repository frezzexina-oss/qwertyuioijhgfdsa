import tkinter as tk
from tkinter import ttk, messagebox
from task_manager import TaskManager


class TaskTrackerApp:
    BG = "#F3F5F9"
    WHITE = "#FFFFFF"
    TEXT = "#202B3C"
    MUTED = "#778397"
    BLUE = "#4169E1"
    BLUE_DARK = "#3155C5"
    BORDER = "#E5EAF1"
    GREEN_BG = "#E5F6ED"
    GREEN = "#218653"
    ORANGE_BG = "#FFF1DC"
    ORANGE = "#B87516"
    RED_BG = "#FCE8E8"
    RED = "#C34B4B"

    def __init__(self, root):
        self.root = root
        self.manager = TaskManager()
        self.tasks = []
        self.projects = []

        self.root.title("Task Tracker")
        self.root.geometry("1120x760")
        self.root.minsize(900, 620)
        self.root.configure(bg=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup_style()
        self.build_interface()
        self.load_projects()
        self.load_tasks()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=self.WHITE,
            foreground=self.TEXT,
            fieldbackground=self.WHITE,
            rowheight=39,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#F7F9FC",
            foreground=self.MUTED,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
            padding=(10, 12)
        )
        style.map(
            "Treeview",
            background=[("selected", "#E8EEFF")],
            foreground=[("selected", self.TEXT)]
        )
        style.configure(
            "TCombobox",
            padding=7,
            fieldbackground=self.WHITE,
            background=self.WHITE,
            foreground=self.TEXT,
            arrowcolor=self.MUTED
        )

    def build_interface(self):
        outer = tk.Frame(self.root, bg=self.BG, padx=28, pady=22)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=self.BG)
        header.pack(fill="x", pady=(0, 18))

        title_area = tk.Frame(header, bg=self.BG)
        title_area.pack(side="left")
        tk.Label(
            title_area, text="Task Tracker",
            bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")
        tk.Label(
            title_area, text="Організовуй завдання та стеж за прогресом",
            bg=self.BG, fg=self.MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 0))

        tk.Label(
            header, text="ПЛАНУЙ  •  ВИКОНУЙ  •  ДОСЯГАЙ",
            bg=self.BG, fg=self.BLUE,
            font=("Segoe UI", 9, "bold")
        ).pack(side="right", anchor="center", padx=(10, 0))

        self.stats_frame = tk.Frame(outer, bg=self.BG)
        self.stats_frame.pack(fill="x", pady=(0, 17))

        self.stat_values = {}
        self.create_stat_card(self.stats_frame, "Усього завдань", "total", self.BLUE)
        self.create_stat_card(self.stats_frame, "Очікують", "waiting", self.ORANGE)
        self.create_stat_card(self.stats_frame, "Виконуються", "active", self.BLUE)
        self.create_stat_card(self.stats_frame, "Завершені", "done", self.GREEN)

        filter_card = tk.Frame(
            outer, bg=self.WHITE, highlightbackground=self.BORDER,
            highlightthickness=1, padx=15, pady=13
        )
        filter_card.pack(fill="x", pady=(0, 14))

        search_area = tk.Frame(filter_card, bg=self.WHITE)
        search_area.pack(side="left", fill="x", expand=True)
        tk.Label(
            search_area, text="ПОШУК", bg=self.WHITE, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", pady=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_table())
        search_entry = tk.Entry(
            search_area, textvariable=self.search_var,
            bg="#F7F9FC", fg=self.TEXT, relief="flat",
            font=("Segoe UI", 10), insertbackground=self.TEXT
        )
        search_entry.pack(fill="x", ipady=8, padx=(0, 14))

        status_area = tk.Frame(filter_card, bg=self.WHITE)
        status_area.pack(side="left", padx=(0, 12))
        tk.Label(
            status_area, text="СТАТУС", bg=self.WHITE, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", pady=(0, 5))
        self.status_filter = ttk.Combobox(
            status_area, state="readonly", width=17,
            values=["Усі", "Очікує", "Виконується", "Завершено", "Закінчено"]
        )
        self.status_filter.set("Усі")
        self.status_filter.pack(ipady=4)
        self.status_filter.bind("<<ComboboxSelected>>", lambda _e: self.refresh_table())

        project_area = tk.Frame(filter_card, bg=self.WHITE)
        project_area.pack(side="left")
        tk.Label(
            project_area, text="ПРОЄКТ", bg=self.WHITE, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", pady=(0, 5))
        self.project_filter = ttk.Combobox(
            project_area, state="readonly", width=19, values=["Усі"]
        )
        self.project_filter.set("Усі")
        self.project_filter.pack(ipady=4)
        self.project_filter.bind("<<ComboboxSelected>>", lambda _e: self.refresh_table())

        table_card = tk.Frame(
            outer, bg=self.WHITE, highlightbackground=self.BORDER,
            highlightthickness=1
        )
        table_card.pack(fill="both", expand=True)

        table_header = tk.Frame(table_card, bg=self.WHITE, padx=17, pady=13)
        table_header.pack(fill="x")
        tk.Label(
            table_header, text="Список завдань", bg=self.WHITE,
            fg=self.TEXT, font=("Segoe UI", 12, "bold")
        ).pack(side="left")
        self.count_label = tk.Label(
            table_header, text="0 завдань", bg=self.WHITE,
            fg=self.MUTED, font=("Segoe UI", 9)
        )
        self.count_label.pack(side="right")

        table_wrap = tk.Frame(table_card, bg=self.WHITE)
        table_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        columns = ("id", "title", "project", "status", "deadline")
        self.tree = ttk.Treeview(
            table_wrap, columns=columns, show="headings",
            selectmode="browse"
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="НАЗВА ЗАВДАННЯ")
        self.tree.heading("project", text="ПРОЄКТ")
        self.tree.heading("status", text="СТАТУС")
        self.tree.heading("deadline", text="ДЕДЛАЙН")
        self.tree.column("id", width=55, anchor="center", stretch=False)
        self.tree.column("title", width=390, anchor="w")
        self.tree.column("project", width=180, anchor="w")
        self.tree.column("status", width=150, anchor="center")
        self.tree.column("deadline", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("done", foreground=self.GREEN)
        self.tree.tag_configure("active", foreground=self.BLUE)
        self.tree.tag_configure("waiting", foreground=self.ORANGE)
        self.tree.bind("<Double-1>", lambda _e: self.edit_task())

        actions = tk.Frame(outer, bg=self.BG)
        actions.pack(fill="x", pady=(15, 0))

        self.make_button(actions, "＋ Додати завдання", self.add_task, self.BLUE, self.WHITE).pack(side="left")
        self.make_button(actions, "Редагувати", self.edit_task, "#E8EEFF", self.BLUE).pack(side="left", padx=(9, 0))
        self.make_button(actions, "Видалити", self.delete_task, self.RED_BG, self.RED).pack(side="left", padx=(9, 0))
        self.make_button(actions, "＋ Додати проєкт", self.add_project, self.WHITE, self.TEXT, outline=True).pack(side="right")
        self.make_button(actions, "Оновити", self.load_tasks, self.WHITE, self.TEXT, outline=True).pack(side="right", padx=(0, 9))

    def create_stat_card(self, parent, label, key, accent):
        card = tk.Frame(
            parent, bg=self.WHITE, highlightbackground=self.BORDER,
            highlightthickness=1, padx=16, pady=12
        )
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Frame(card, bg=accent, width=4, height=34).pack(side="left", padx=(0, 12))
        content = tk.Frame(card, bg=self.WHITE)
        content.pack(side="left")
        tk.Label(
            content, text=label, bg=self.WHITE, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        value = tk.Label(
            content, text="0", bg=self.WHITE, fg=self.TEXT,
            font=("Segoe UI", 19, "bold")
        )
        value.pack(anchor="w", pady=(2, 0))
        self.stat_values[key] = value

    def make_button(self, parent, text, command, bg, fg, outline=False):
        button = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 9, "bold"), padx=15, pady=10
        )
        if outline:
            button.configure(highlightbackground=self.BORDER, highlightthickness=1)
        return button

    def load_projects(self):
        self.projects = self.manager.get_projects()
        names = ["Усі"] + [project.name for project in self.projects]
        current = self.project_filter.get() if hasattr(self, "project_filter") else "Усі"
        self.project_filter["values"] = names
        self.project_filter.set(current if current in names else "Усі")

    def load_tasks(self):
        self.tasks = self.manager.get_tasks()
        self.refresh_table()

    def refresh_table(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_var.get().strip().lower()
        selected_status = self.status_filter.get()
        selected_project = self.project_filter.get()

        filtered = []
        for task in self.tasks:
            if search and search not in task.title.lower():
                continue
            if selected_status != "Усі" and task.status != selected_status:
                continue
            if selected_project != "Усі" and task.project_name != selected_project:
                continue
            filtered.append(task)

        for task in filtered:
            status_lower = task.status.lower()
            if status_lower in ("завершено", "закінчено", "виконано"):
                tag = "done"
            elif status_lower == "виконується":
                tag = "active"
            else:
                tag = "waiting"

            self.tree.insert(
                "", "end", iid=str(task.id),
                values=(task.id, task.title, task.project_name, task.status, task.deadline),
                tags=(tag,)
            )

        self.count_label.config(text=f"{len(filtered)} завдань")
        self.update_statistics()

    def update_statistics(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.status.lower() in ("завершено", "закінчено", "виконано"))
        active = sum(1 for t in self.tasks if t.status.lower() == "виконується")
        waiting = total - done - active
        self.stat_values["total"].config(text=str(total))
        self.stat_values["waiting"].config(text=str(waiting))
        self.stat_values["active"].config(text=str(active))
        self.stat_values["done"].config(text=str(done))

    def selected_task(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Task Tracker", "Спочатку вибери завдання зі списку.")
            return None
        task_id = int(selection[0])
        return next((task for task in self.tasks if task.id == task_id), None)

    def task_dialog(self, title, task=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("460x510")
        dialog.resizable(False, False)
        dialog.configure(bg=self.BG)
        dialog.transient(self.root)
        dialog.grab_set()

        panel = tk.Frame(dialog, bg=self.WHITE, padx=24, pady=22)
        panel.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            panel, text=title, bg=self.WHITE, fg=self.TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", pady=(0, 18))

        def field_label(text):
            tk.Label(
                panel, text=text, bg=self.WHITE, fg=self.MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(7, 5))

        field_label("Назва завдання")
        title_entry = tk.Entry(panel, font=("Segoe UI", 10), relief="solid", bd=1)
        title_entry.pack(fill="x", ipady=7)
        if task:
            title_entry.insert(0, task.title)

        field_label("Опис")
        description_text = tk.Text(panel, height=4, font=("Segoe UI", 10), relief="solid", bd=1, wrap="word")
        description_text.pack(fill="x")
        if task:
            description_text.insert("1.0", task.description)

        project_names = [p.name for p in self.projects]
        field_label("Проєкт")
        project_combo = ttk.Combobox(panel, state="readonly", values=project_names)
        project_combo.pack(fill="x", ipady=4)
        if task:
            project_combo.set(task.project_name)
        elif project_names:
            project_combo.set(project_names[0])

        field_label("Статус")
        status_combo = ttk.Combobox(
            panel, state="readonly",
            values=["Очікує", "Виконується", "Завершено", "Закінчено"]
        )
        status_combo.pack(fill="x", ipady=4)
        status_combo.set(task.status if task else "Очікує")

        field_label("Дедлайн")
        deadline_entry = tk.Entry(panel, font=("Segoe UI", 10), relief="solid", bd=1)
        deadline_entry.pack(fill="x", ipady=7)
        if task:
            deadline_entry.insert(0, task.deadline)

        def save():
            task_title = title_entry.get().strip()
            project_name = project_combo.get()
            if not task_title:
                messagebox.showwarning("Перевір дані", "Введи назву завдання.", parent=dialog)
                return
            if not project_name:
                messagebox.showwarning("Перевір дані", "Створи або вибери проєкт.", parent=dialog)
                return

            project = next((p for p in self.projects if p.name == project_name), None)
            if project is None:
                messagebox.showerror("Помилка", "Не вдалося знайти вибраний проєкт.", parent=dialog)
                return

            description = description_text.get("1.0", "end").strip()
            status = status_combo.get()
            deadline = deadline_entry.get().strip()

            try:
                if task:
                    self.manager.update_task(
                        task.id, task_title, description,
                        project.id, status, deadline
                    )
                else:
                    self.manager.add_task(
                        task_title, description,
                        project.id, status, deadline
                    )
                self.load_tasks()
                dialog.destroy()
            except Exception as error:
                messagebox.showerror("Помилка", f"Не вдалося зберегти завдання:\n{error}", parent=dialog)

        buttons = tk.Frame(panel, bg=self.WHITE)
        buttons.pack(fill="x", pady=(18, 0))
        self.make_button(buttons, "Зберегти", save, self.BLUE, self.WHITE).pack(side="left")
        self.make_button(buttons, "Скасувати", dialog.destroy, "#EEF1F6", self.TEXT).pack(side="left", padx=(9, 0))
        title_entry.focus_set()

    def add_task(self):
        self.load_projects()
        self.task_dialog("Нове завдання")

    def edit_task(self):
        task = self.selected_task()
        if task:
            self.task_dialog("Редагувати завдання", task)

    def delete_task(self):
        task = self.selected_task()
        if not task:
            return
        if messagebox.askyesno("Підтвердження", f"Видалити завдання «{task.title}»?"):
            try:
                self.manager.delete_task(task.id)
                self.load_tasks()
            except Exception as error:
                messagebox.showerror("Помилка", f"Не вдалося видалити завдання:\n{error}")

    def add_project(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Новий проєкт")
        dialog.geometry("360x190")
        dialog.resizable(False, False)
        dialog.configure(bg=self.BG)
        dialog.transient(self.root)
        dialog.grab_set()

        panel = tk.Frame(dialog, bg=self.WHITE, padx=22, pady=20)
        panel.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(
            panel, text="Створити проєкт", bg=self.WHITE,
            fg=self.TEXT, font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 12))
        tk.Label(
            panel, text="Назва проєкту", bg=self.WHITE,
            fg=self.MUTED, font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 5))
        name_entry = tk.Entry(panel, font=("Segoe UI", 10), relief="solid", bd=1)
        name_entry.pack(fill="x", ipady=7)

        def save_project():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Перевір дані", "Введи назву проєкту.", parent=dialog)
                return
            try:
                self.manager.add_project(name)
                self.load_projects()
                dialog.destroy()
            except Exception as error:
                messagebox.showerror("Помилка", f"Не вдалося створити проєкт:\n{error}", parent=dialog)

        buttons = tk.Frame(panel, bg=self.WHITE)
        buttons.pack(fill="x", pady=(15, 0))
        self.make_button(buttons, "Створити", save_project, self.BLUE, self.WHITE).pack(side="left")
        self.make_button(buttons, "Скасувати", dialog.destroy, "#EEF1F6", self.TEXT).pack(side="left", padx=(8, 0))
        name_entry.focus_set()

    def on_close(self):
        try:
            self.manager.close()
        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTrackerApp(root)
    root.mainloop()
