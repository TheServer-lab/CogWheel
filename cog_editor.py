# cog_editor.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from cogwheel import CogWheel

class CogEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CogWheel Editor")
        self.geometry("600x400")

        self.config_data = None
        self.current_file = None

        # UI Elements
        self.tree = ttk.Treeview(self)
        self.tree.heading("#0", text="Settings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.value_label = tk.Label(self, text="Value:")
        self.value_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.value_entry = tk.Entry(self)
        self.value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.save_button = tk.Button(self, text="Save Value", command=self.save_value)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CogWheel Files", "*.cog")])
        if not filepath:
            return
        self.current_file = filepath
        self.config_data = CogWheel(filepath)
        self.populate_tree()

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        for section in self.config_data.section_order:
            sec_node = self.tree.insert("", "end", text=f"[{section}]", open=True)
            for key, value in self.config_data.data[section].items():
                self.tree.insert(sec_node, "end", text=key, values=(value, section))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        parent = self.tree.parent(item)
        if parent:  # it's a key
            key = self.tree.item(item, "text")
            section = self.tree.item(parent, "text")[1:-1]  # remove brackets
            value = self.config_data.get(key, section)
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, str(value))

    def save_value(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        parent = self.tree.parent(item)
        if parent:
            key = self.tree.item(item, "text")
            section = self.tree.item(parent, "text")[1:-1]
            new_value = self.value_entry.get().strip()

            # Convert to proper type
            if new_value.lower() == "true":
                new_value = True
            elif new_value.lower() == "false":
                new_value = False
            else:
                try:
                    if "." in new_value:
                        new_value = float(new_value)
                    else:
                        new_value = int(new_value)
                except ValueError:
                    pass  # keep as string

            self.config_data.set(key, new_value, section)
            self.populate_tree()

    def save_file(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file loaded")
            return
        self.config_data.save(self.current_file)
        messagebox.showinfo("Saved", f"File saved: {self.current_file}")

if __name__ == "__main__":
    app = CogEditor()
    app.mainloop()
