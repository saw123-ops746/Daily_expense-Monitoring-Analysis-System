
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import date

# Dataset file
FILE = "daily_expense_dataset.csv"

COLUMNS = [
    "Date",
    "Expense_Category",
    "Description",
    "Payment_Method",
    "Amount"
]

CATEGORIES = [
    "Food",
    "Travel",
    "Education",
    "Shopping",
    "Bills",
    "Other"
]

PAYMENT_METHODS = [
    "UPI",
    "Cash",
    "Debit Card",
    "Credit Card"
]

# Load your own dataset or create an empty one
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
    df = df.reindex(columns=COLUMNS)
    df["Amount"] = pd.to_numeric(
        df["Amount"], errors="coerce"
    ).fillna(0)
else:
    df = pd.DataFrame(columns=COLUMNS)


# Main application window
root = tk.Tk()
root.title("Daily Expense Monitoring and Analysis System")
root.geometry("1000x650")
root.configure(bg="#f2f5f7")

heading = tk.Label(
    root,
    text="DAILY EXPENSE MONITORING AND ANALYSIS SYSTEM",
    font=("Arial", 17, "bold"),
    bg="darkgreen",
    fg="white",
    pady=12
)
heading.pack(fill="x")


# Input form
form = tk.Frame(root, bg="#f2f5f7")
form.pack(pady=12)

labels = [
    "Date (YYYY-MM-DD)",
    "Expense Category",
    "Description",
    "Payment Method",
    "Amount (Rs.)"
]

entries = []

for i, label in enumerate(labels):
    tk.Label(
        form,
        text=label,
        font=("Arial", 10),
        bg="#f2f5f7"
    ).grid(row=i, column=0, padx=8, pady=5, sticky="w")

    if label == "Expense Category":
        entry = ttk.Combobox(
            form,
            values=CATEGORIES,
            state="readonly",
            width=27
        )
    elif label == "Payment Method":
        entry = ttk.Combobox(
            form,
            values=PAYMENT_METHODS,
            state="readonly",
            width=27
        )
    else:
        entry = tk.Entry(form, width=30)

    entry.grid(row=i, column=1, padx=8, pady=5)
    entries.append(entry)

entries[0].insert(0, date.today().isoformat())
entries[1].set("Food")
entries[3].set("UPI")


# Expense table
table = ttk.Treeview(
    root,
    columns=COLUMNS,
    show="headings",
    height=10
)

for col in COLUMNS:
    table.heading(col, text=col)
    table.column(col, width=175, anchor="center")

table.pack(fill="x", padx=12, pady=10)


# Summary information
summary = tk.Label(
    root,
    text="Total: Rs. 0.00 | Average: Rs. 0.00 | Records: 0",
    font=("Arial", 11, "bold"),
    bg="#f2f5f7"
)
summary.pack(pady=5)


# Refresh table and calculate statistics
def refresh():
    table.delete(*table.get_children())

    for index, row in df.iterrows():
        table.insert(
            "",
            "end",
            iid=str(index),
            values=list(row)
        )

    amounts = pd.to_numeric(
        df["Amount"], errors="coerce"
    ).dropna().to_numpy()

    total = np.sum(amounts)
    average = np.mean(amounts) if len(amounts) else 0
    count = len(amounts)

    summary.config(
        text=(
            f"Total: Rs. {total:.2f} | "
            f"Average: Rs. {average:.2f} | "
            f"Records: {count}"
        )
    )


# Add an expense
def add_expense():
    global df

    try:
        expense_date = entries[0].get().strip()
        category = entries[1].get().strip()
        description = entries[2].get().strip()
        payment_method = entries[3].get().strip()
        amount = float(entries[4].get())

        # Validate inputs
        date.fromisoformat(expense_date)

        if not category:
            raise ValueError("Select an expense category.")

        if not description:
            raise ValueError("Enter an expense description.")

        if not payment_method:
            raise ValueError("Select a payment method.")

        if not np.isfinite(amount) or amount <= 0:
            raise ValueError("Amount must be a positive number.")

        new_row = pd.DataFrame([{
            "Date": expense_date,
            "Expense_Category": category,
            "Description": description,
            "Payment_Method": payment_method,
            "Amount": amount
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILE, index=False)

        entries[2].delete(0, tk.END)
        entries[4].delete(0, tk.END)

        refresh()
        messagebox.showinfo("Success", "Expense added successfully.")

    except ValueError as error:
        messagebox.showerror(
            "Invalid Input",
            str(error) or "Enter a valid date and amount."
        )


# Filter records by category
def filter_expenses():
    category = entries[1].get().strip()

    if not category:
        messagebox.showwarning(
            "Notice", "Please select a category first."
        )
        return

    table.delete(*table.get_children())

    filtered = df[df["Expense_Category"] == category]

    for index, row in filtered.iterrows():
        table.insert(
            "",
            "end",
            iid=str(index),
            values=list(row)
        )


# Display all records
def show_all():
    refresh()


# Delete the selected expense
def delete_expense():
    global df

    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning", "Select an expense to delete."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm",
        "Do you want to delete the selected expense?"
    )

    if not confirm:
        return

    indexes = [int(item) for item in selected]
    df = df.drop(indexes).reset_index(drop=True)
    df.to_csv(FILE, index=False)

    refresh()

    messagebox.showinfo(
        "Success", "Expense deleted successfully."
    )


# Show bar graph
def show_graph():
    if df.empty:
        messagebox.showinfo(
            "Notice", "Add expenses before creating a graph."
        )
        return

    category_totals = df.groupby(
        "Expense_Category"
    )["Amount"].sum()

    category_totals.plot(kind="bar")

    plt.title("Daily Expense Analysis by Category")
    plt.xlabel("Expense Category")
    plt.ylabel("Total Amount (Rs.)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


# Show daily spending line graph
def show_daily_graph():
    if df.empty:
        messagebox.showinfo(
            "Notice", "Add expenses before creating a graph."
        )
        return

    daily_totals = df.copy()
    daily_totals["Date"] = pd.to_datetime(
        daily_totals["Date"], errors="coerce"
    )

    daily_totals = daily_totals.groupby(
        "Date"
    )["Amount"].sum().sort_index()

    daily_totals.plot(kind="line", marker="o")

    plt.title("Daily Spending Trend")
    plt.xlabel("Date")
    plt.ylabel("Total Amount (Rs.)")
    plt.tight_layout()
    plt.show()


# Application buttons
buttons = tk.Frame(root, bg="#f2f5f7")
buttons.pack(pady=10)

tk.Button(
    buttons, text="Add Expense",
    command=add_expense, width=15
).grid(row=0, column=0, padx=5, pady=5)

tk.Button(
    buttons, text="Show All",
    command=show_all, width=15
).grid(row=0, column=1, padx=5, pady=5)

tk.Button(
    buttons, text="Filter Category",
    command=filter_expenses, width=15
).grid(row=0, column=2, padx=5, pady=5)

tk.Button(
    buttons, text="Delete Expense",
    command=delete_expense, width=15
).grid(row=0, column=3, padx=5, pady=5)

tk.Button(
    buttons, text="Category Bar Graph",
    command=show_graph, width=18
).grid(row=1, column=1, padx=5, pady=5)

tk.Button(
    buttons, text="Daily Spending Graph",
    command=show_daily_graph, width=18
).grid(row=1, column=2, padx=5, pady=5)

refresh()
root.mainloop()
