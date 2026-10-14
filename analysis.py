
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Dataset path
FILE = Path(__file__).with_name("daily_expense_dataset.csv")

# Load dataset
df = pd.read_csv(FILE)

# Clean and validate data
required_columns = [
    "Date",
    "Expense_Category",
    "Description",
    "Payment_Method",
    "Amount"
]

missing = set(required_columns) - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

df = df.dropna(subset=["Date", "Amount"])
df = df[df["Amount"] > 0]

if df.empty:
    raise ValueError("No valid expense records found.")

# Basic analysis
total_expense = np.sum(df["Amount"])
average_expense = np.mean(df["Amount"])
highest_expense = np.max(df["Amount"])
lowest_expense = np.min(df["Amount"])
transaction_count = len(df)

print("\nDAILY EXPENSE MONITORING AND ANALYSIS")
print("-" * 42)
print(f"Total expense: Rs. {total_expense:.2f}")
print(f"Average expense: Rs. {average_expense:.2f}")
print(f"Highest expense: Rs. {highest_expense:.2f}")
print(f"Lowest expense: Rs. {lowest_expense:.2f}")
print(f"Total transactions: {transaction_count}")

# Expenses by category
category_totals = df.groupby(
    "Expense_Category"
)["Amount"].sum().sort_values(ascending=False)

print("\nEXPENSES BY CATEGORY")
print(category_totals.to_string())

# Daily expenses
daily_totals = df.groupby(
    df["Date"].dt.date
)["Amount"].sum()

print("\nDAILY EXPENSES")
print(daily_totals.to_string())

# Bar chart
category_totals.plot(kind="bar")
plt.title("Total Expenses by Category")
plt.xlabel("Expense Category")
plt.ylabel("Amount (Rs.)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("category_expense_bar.png")
plt.show()

# Pie chart
category_totals.plot(kind="pie", autopct="%1.1f%%")
plt.title("Expense Distribution by Category")
plt.ylabel("")
plt.tight_layout()
plt.savefig("category_expense_pie.png")
plt.show()

# Line chart
daily_totals.plot(kind="line", marker="o")
plt.title("Daily Expense Trend")
plt.xlabel("Date")
plt.ylabel("Amount (Rs.)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("daily_expense_line.png")
plt.show()

# Export category analysis
category_totals.rename("Total_Amount").to_csv(
    "category_analysis.csv"
)

print("\nAnalysis completed successfully.")
print("Charts and category_analysis.csv have been saved.")
