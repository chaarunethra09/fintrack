import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --- Database Setup ---
con = sqlite3.connect("fintrack.db")
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        amount REAL,
        kind TEXT
    )
""")
con.commit()

# --- Main Window Setup ---
root = tk.Tk()
root.title("FinTrack - Personal Finance Tracker")
root.geometry("650x550")
root.config(bg="#101827")

# --- Header / Title ---
title_label = tk.Label(root, text="FINTRACK", bg="#101827", fg="#35d39a", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

subtitle_label = tk.Label(root, text="Personal Finance Tracker", bg="#101827", fg="white", font=("Arial", 11))
subtitle_label.pack()

# --- Summary Dashboard Frame ---
summary = tk.Frame(root, bg="#1c2b40")
summary.pack(pady=15, padx=20, fill="x")

income_label = tk.Label(summary, text="Income: ₹0", bg="#1c2b40", fg="#35d39a", font=("Arial", 12, "bold"))
income_label.pack(side="left", padx=15, pady=10)

expense_label = tk.Label(summary, text="Expense: ₹0", bg="#1c2b40", fg="#ff7585", font=("Arial", 12, "bold"))
expense_label.pack(side="left", padx=15)

balance_label = tk.Label(summary, text="Balance: ₹0", bg="#1c2b40", fg="white", font=("Arial", 12, "bold"))
balance_label.pack(side="left", padx=15)

# --- Input Form Section ---
form = tk.Frame(root, bg="#101827")
form.pack(pady=10)

# 1. Title Entry
title_entry = tk.Entry(form, width=15, font=("Arial", 11))
title_entry.grid(row=0, column=0, padx=5, pady=5)
title_entry.insert(0, "Transaction")

# 2. Category Entry
category_entry = tk.Entry(form, width=12, font=("Arial", 11))
category_entry.grid(row=0, column=1, padx=5, pady=5)
category_entry.insert(0, "Category")

# 3. Amount Entry
amount_entry = tk.Entry(form, width=10, font=("Arial", 11))
amount_entry.grid(row=0, column=2, padx=5, pady=5)
amount_entry.insert(0, "Amount")

# 4. Type Dropdown (Income / Expense)
type_box = ttk.Combobox(form, values=["Income", "Expense"], width=10, font=("Arial", 10))
type_box.grid(row=0, column=3, padx=5, pady=5)
type_box.set("Expense")

# --- Functions ---
def update():
    cur.execute("SELECT * FROM transactions")
    rows = cur.fetchall()

    table.delete(*table.get_children())
    income = 0
    expense = 0

    for row in rows:
        # Columns mapped to table: Title (row[1]), Category (row[2]), Amount (row[3]), Type (row[4])
        table.insert("", "end", values=(row[1], row[2], row[3], row[4]))
        
        if row[4] == "Income":
            income += float(row[3])
        else:
            expense += float(row[3])

    income_label.config(text=f"Income: ₹{income:.2f}")
    expense_label.config(text=f"Expense: ₹{expense:.2f}")
    balance_label.config(text=f"Balance: ₹{income-expense:.2f}")

def add_transaction():
    title = title_entry.get().strip()
    category = category_entry.get().strip()
    
    try:
        amount = float(amount_entry.get())
        if not title or amount <= 0 or title == "Transaction":
            raise ValueError
        
        kind = type_box.get()

        # Insert into database with all 4 values properly aligned
        cur.execute(
            "INSERT INTO transactions (title, category, amount, kind) VALUES (?, ?, ?, ?)",
            (title, category, amount, kind)
        )
        con.commit()
        
        # Clear fields
        title_entry.delete(0, 'end')
        category_entry.delete(0, 'end')
        amount_entry.delete(0, 'end')
        
        # Instantly refresh UI totals and rows
        update()
        
    except ValueError:
        messagebox.showerror("Error", "Please enter valid transaction details and a positive amount.")

# --- Add Button (Placed properly at root level) ---
add_btn = tk.Button(root, text="Add Transaction", command=add_transaction, bg="#35d39a", fg="#101827", font=("Arial", 11, "bold"))
add_btn.pack(pady=8)

# --- Table View (Treeview) ---
table_frame = tk.Frame(root)
table_frame.pack(pady=10, fill="both", expand=True, padx=20)

columns = ("Title", "Category", "Amount", "Type")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=120, anchor="center")

table.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
scrollbar.pack(side="right", fill="y")
table.configure(yscrollcommand=scrollbar.set)

# --- Initial Load & Run ---
update()
root.mainloop()