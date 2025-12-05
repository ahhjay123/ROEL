import customtkinter as ctk
from tkinter import messagebox
import datetime
from db import get_connection

def open_sales_window():
    window = ctk.CTkToplevel()
    window.title("Sales Dashboard")
    window.geometry("900x620")

    window.update_idletasks()
    w, h = 900, 620
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.lift()
    window.focus_force()
    window.grab_set()

    main = ctk.CTkFrame(window, corner_radius=16)
    main.pack(fill="both", expand=True, padx=16, pady=16)

    title = ctk.CTkLabel(main, text="📊 Sales Dashboard",
                         font=("Arial Rounded MT Bold", 26))
    title.pack(pady=(5, 10))

    tabs = ctk.CTkTabview(main, width=860, height=520)
    tabs.pack(fill="both", expand=True)
    tabs.add("Sales Log")
    tabs.add("Summary")
    tabs.add("Reports")

    log_box = ctk.CTkTextbox(tabs.tab("Sales Log"))
    log_box.pack(fill="both", expand=True, padx=10, pady=10)

    def render_sales_log():
        log_box.configure(state="normal")
        log_box.delete("1.0", "end")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id,
                s.product_name AS product,
                s.quantity,
                s.total,
                s.date,
                s.customer_name
            FROM sales s
            ORDER BY s.date DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            log_box.insert("end", "No sales recorded yet.")
        else:
            for r in rows:
                    log_box.insert(
                        "end",
                        f"{r['date']} | Customer: {r['customer_name']} | "
                        f"{r['product']} x{r['quantity']} = ₱{r['total']:.2f}\n"
                    )

        log_box.configure(state="disabled")

    render_sales_log()

    summary_box = ctk.CTkTextbox(tabs.tab("Summary"))
    summary_box.pack(fill="both", expand=True, padx=10, pady=10)

    def render_summary():
        summary_box.configure(state="normal")
        summary_box.delete("1.0", "end")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT product_name AS product,
                SUM(quantity) AS qty_sold,
                SUM(total) AS revenue
            FROM sales
            GROUP BY product_name
            ORDER BY revenue DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            summary_box.insert("end", "No sales data yet.")
        else:
            summary_box.insert("end", "Product Sales Summary\n")
            summary_box.insert("end", "-" * 50 + "\n")
            for r in rows:
                summary_box.insert(
                    "end",
                    f"{r['product']} — Sold: {r['qty_sold']} pcs, Revenue: ₱{r['revenue']:.2f}\n"
                )

        summary_box.configure(state="disabled")

    render_summary()

    report_frame = ctk.CTkFrame(tabs.tab("Reports"))
    report_frame.pack(fill="both", expand=True, padx=10, pady=10)

    report_box = ctk.CTkTextbox(report_frame)
    report_box.pack(fill="both", expand=True, pady=6)

    def generate_report(period):
        report_box.configure(state="normal")
        report_box.delete("1.0", "end")

        today = datetime.date.today()
        conn = get_connection()
        cursor = conn.cursor()

        if period == "Daily":
            start = today.strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT *
                FROM sales
                WHERE substr(date, 1, 10) = ?
            """, (start,))

        elif period == "Weekly":
            start = today - datetime.timedelta(days=today.weekday())
            end = start + datetime.timedelta(days=6)
            cursor.execute("""
                SELECT *
                FROM sales
                WHERE date(substr(date,1,10)) BETWEEN ? AND ?
            """, (start, end))

        else:
            month = today.strftime("%Y-%m")
            cursor.execute("""
                SELECT *
                FROM sales
                WHERE substr(date, 1, 7) = ?
            """, (month,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            report_box.insert("end", f"No {period.lower()} sales found.\n")
        else:
            total = sum(r["total"] for r in rows)
            report_box.insert("end", f"{period} Sales Report\n")
            report_box.insert("end", "-" * 50 + "\n")
            for r in rows:
                report_box.insert(
                    "end",
                    f"{r['date']} — {r['product_name']} x{r['quantity']} = ₱{r['total']:.2f}\n"
                )

            report_box.insert("end", "-" * 50 + "\n")
            report_box.insert("end", f"TOTAL {period.upper()} SALES: ₱{total:.2f}")

        report_box.configure(state="disabled")

   
    btn_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
    btn_frame.pack(pady=8)

    ctk.CTkButton(btn_frame, text="Daily", width=100,
                  command=lambda: generate_report("Daily")).grid(row=0, column=0, padx=5)

    ctk.CTkButton(btn_frame, text="Weekly", width=100,
                  command=lambda: generate_report("Weekly")).grid(row=0, column=1, padx=5)

    ctk.CTkButton(btn_frame, text="Monthly", width=100,
                  command=lambda: generate_report("Monthly")).grid(row=0, column=2, padx=5)
