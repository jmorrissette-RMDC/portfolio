import tkinter as tk
from tkinter import messagebox
import sqlite3
from task_manager import TaskManager

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.task_manager = TaskManager("tasks.db")

        self.frame = tk.Frame(root)
        self.frame.pack(pady=20)

        self.task_list = tk.Listbox(self.frame, width=50, height=15)
        self.task_list.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.task_list.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_list.config(yscrollcommand=self.scrollbar.set)

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=20)

        self.add_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT)

        self.load_tasks()

    def add_task(self):
        task_name = self.entry.get()
        if task_name:
            self.task_manager.add_task(task_name)
            self.load_tasks()
            self.entry.delete(0, tk.END)

    def delete_task(self):
        selected_task = self.task_list.curselection()
        if selected_task:
            task_name = self.task_list.get(selected_task)
            self.task_manager.delete_task(task_name)
            self.load_tasks()
        else:
            messagebox.showwarning("Select a task", "Please select a task to delete")

    def load_tasks(self):
        self.task_list.delete(0, tk.END)
        tasks = self.task_manager.get_tasks()
        for task in tasks:
            self.task_list.insert(tk.END, task)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()