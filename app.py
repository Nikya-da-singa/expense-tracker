import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Expense Tracker", layout="wide")
FILE_PATH = "expenses.csv"

# =========================
# FUNCTIONS
# =========================
def load_data():
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
        df.to_csv(FILE_PATH, index=False)
    df = pd.read_csv(FILE_PATH)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
    return df

def save_data(df):
    df.to_csv(FILE_PATH, index=False)

# Load data
df = load_data()

st.title("💰 Smart Expense Tracker")
st.markdown("---")

# =========================
# SIDEBAR
# =========================
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Expense", "Manage Expenses", "Analytics"]
)

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.subheader("📊 Overview")

    total = df["Amount"].sum() if not df.empty else 0
    count = len(df)

    col1, col2 = st.columns(2)
    col1.metric("Total Expenses", f"₹{total}")
    col2.metric("Total Entries", count)

    st.write("🕒 Recent Expenses")
    st.dataframe(df.tail(5))

# =========================
# ADD EXPENSE
# =========================
elif menu == "Add Expense":
    st.subheader("➕ Add New Expense")

    col1, col2 = st.columns(2)

    date = col1.date_input("Date")
    amount = col2.number_input("Amount", min_value=0.0)

    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Bills", "Other"]
    )

    description = st.text_input("Description")

    if st.button("Add Expense"):
        new_data = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Amount": [amount],
            "Description": [description]
        })

        new_data.to_csv(FILE_PATH, mode='a', header=False, index=False)

        st.success("✅ Expense Added!")
        st.rerun()
# =========================
# MANAGE EXPENSES
# =========================
elif menu == "Manage Expenses":
    st.subheader("🛠 Manage Expenses")

    if df.empty:
        st.warning("No expenses found")
    else:
        st.dataframe(df)

        # Filter
        st.subheader("🔍 Filter by Category")
        category_filter = st.selectbox(
            "Choose Category",
            ["All"] + list(df["Category"].unique())
        )

        if category_filter != "All":
            filtered = df[df["Category"] == category_filter]
            st.dataframe(filtered)

        # Delete
        st.subheader("🗑 Delete Expense")
        selected = st.selectbox("Select index", df.index)

        if st.button("Delete"):
            df = df.drop(selected)
            save_data(df)
            st.success("Deleted!")
            st.rerun()

        # Download
        st.download_button(
            "⬇ Download Data",
            df.to_csv(index=False),
            file_name="expenses.csv"
        )

# =========================
# ANALYTICS
# =========================
elif menu == "Analytics":
    st.subheader("📈 Analytics")

    if df.empty:
        st.warning("No data available")
    else:
        # Category-wise
        category_total = df.groupby("Category")["Amount"].sum()

        st.write("📊 Category-wise Spending")
        st.bar_chart(category_total)

        # Pie Chart
        st.write("🥧 Distribution")
        st.pyplot(category_total.plot.pie(autopct='%1.1f%%').figure)

        # Monthly trend
        df["Month"] = df["Date"].dt.to_period("M")
        monthly = df.groupby("Month")["Amount"].sum()

        st.write("📅 Monthly Spending Trend")
        st.line_chart(monthly)

        # Top category
        top_category = category_total.idxmax()
        st.success(f"💸 Highest spending on: {top_category}")

        # Budget
        st.subheader("🎯 Budget Tracker")
        budget = st.number_input("Set Monthly Budget", min_value=0.0)

        total = df["Amount"].sum()
        if budget > 0:
            if total > budget:
                st.error("⚠️ Budget Exceeded!")
            else:
                st.success("✅ Within Budget")
