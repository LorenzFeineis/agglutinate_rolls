"""Script to start the application."""
import tkinter as tk
from  tkinter import ttk
from methods import ClueRoles


def main():
    """Use this function for starting the application."""
    master = tk.Tk()

    myapp = App(master)
    myapp.master.title('Optimale Rollenverklebung')

    myapp.mainloop()
    return 0


class App(tk.Frame):
    """Use this class to start the GUI."""

    def __init__(self, master):
        """Initialize class."""
        super().__init__(master)

        tk.Label(master, text='Rolle A').grid(row=0)
        entry_role_a = tk.Entry(master)
        entry_role_a.grid(row=0, column=1)
        self.entry_role_a = entry_role_a

        tk.Label(master, text='Rolle B').grid(row=1)
        entry_role_b = tk.Entry(master)
        entry_role_b.grid(row=1, column=1)
        self.entry_role_b = entry_role_b

        tk.Label(master, text='Max Rollen').grid(row=2)
        entry_max_roles = tk.Entry(master)
        entry_max_roles.grid(row=2, column=1)
        self.entry_max_roles = entry_max_roles

        tk.Label(master, text='Max Laenge').grid(row=3)
        entry_max_length = tk.Entry(master)
        entry_max_length.grid(row=3, column=1)
        self.entry_max_length = entry_max_length

        start_button = tk.Button(master, text='Start', width=10)
        start_button.grid(row=4, column=0)
        self.start = start_button

        self.start.bind("<ButtonPress>", self.start_solve)

    def start_solve(self, event):
        """Start the mip solver."""
        role_a = get_list_from_entry(self.entry_role_a)
        role_b = get_list_from_entry(self.entry_role_b)
        roles = role_a, role_b
        max_roles = int(self.entry_max_roles.get())
        max_length = float(self.entry_max_length.get())

        self.check_input()

        problem = ClueRoles(roles,
                            max_roles=max_roles,
                            max_length=max_length)
        result = problem.solve()

        self.open_results(result, roles)

        return 0

    def check_input(self):
        """Check if the input is correct."""
        assert self.entry_role_a
        return 0

    def open_results(self, result, roles):
        """Open a new result window."""
        print(result)
        result_window = tk.Toplevel(self.master)
        table = ttk.Treeview(result_window)
        roles_a, roles_b = roles
        columns = ('Finale Rollen',)
        for idx, role in enumerate(roles_a):
            columns += (f'Rolle A{idx+1}',)
        for idx, role in enumerate(roles_b):
            columns += (f'Rolle B{idx+1}',)

        table['columns'] = columns
        table.column('#0', width=0, stretch=tk.NO)
        table.heading('#0', text='')
        for column in columns:
            table.column(column, width=100, stretch=tk.YES)
            table.heading(column, text=column)

        for role_id, role in enumerate(result):
            inserts = (role_id+1,) + tuple(role.roles_a) + tuple(role.roles_b)
            table.insert(parent='', index='end', values=inserts)

        table.pack()
        return 0


def get_list_from_entry(entry):
    """Convert string to list."""
    string = entry.get()
    return [float(length) for length in string.split(',')]


if __name__ == '__main__':
    main()
