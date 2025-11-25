import customtkinter as ctk
import datetime
from sale import get_sales_history


def open_history_window():
    window = ctk.CTkToplevel()
    window.title("Sales History")
    window.geometry("780x560")

    window.update_idletasks()
    w, h = 780, 560
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.lift()
    window.focus_force()
    window.grab_set()
    window.attributes("-topmost", True)
    window.after(10, lambda: window.attributes("-topmost", False))

    main = ctk.CTkFrame(window, corner_radius=16)
    main.pack(fill="both", expand=True, padx=16, pady=16)
    main.grid_rowconfigure(3, weight=1)
    main.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        main, text="Sales History", font=("Arial Rounded MT Bold", 22)
    ).grid(row=0, column=0, padx=10, pady=(6, 2), sticky="w")

    ctk.CTkLabel(
        main,
        text="Filter invoices by date.",
        font=("Arial", 11),
        text_color="#9ca3af",
    ).grid(row=1, column=0, padx=10, pady=(0, 12), sticky="w")

    filter_frame = ctk.CTkFrame(main, fg_color="transparent")
    filter_frame.grid(row=2, column=0, padx=10, pady=(0, 12), sticky="ew")
    filter_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        filter_frame, text="Select Date:", font=("Arial", 12)
    ).grid(row=0, column=0, sticky="w")

    date_entry = ctk.CTkEntry(
        filter_frame, placeholder_text="YYYY-MM-DD", width=160, height=32
    )
    date_entry.grid(row=0, column=1, padx=(6, 10))

    def set_today():
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        date_entry.delete(0, "end")
        date_entry.insert(0, today)
        render_history()

    today_btn = ctk.CTkButton(
        filter_frame,
        text="Today",
        width=80,
        height=32,
        fg_color="#1f6aa5",
        hover_color="#155c8e",
        command=set_today,
    )
    today_btn.grid(row=0, column=2, padx=6)

    def clear_date():
        date_entry.delete(0, "end")
        render_history()

    clear_btn = ctk.CTkButton(
        filter_frame,
        text="Clear",
        width=80,
        height=32,
        fg_color="#4b5563",
        hover_color="#374151",
        command=clear_date,
    )
    clear_btn.grid(row=0, column=3, padx=6)

    history_box = ctk.CTkTextbox(main, width=740, height=420)
    history_box.grid(row=3, column=0, padx=10, pady=6, sticky="nsew")

    def render_history():
        history_box.configure(state="normal")
        history_box.delete("1.0", "end")

        sales = get_sales_history()
        selected_date = date_entry.get().strip()

        filtered = []

        if selected_date:
            try:
                datetime.datetime.strptime(selected_date, "%Y-%m-%d")
            except ValueError:
                history_box.insert("end", "Invalid date format. Use YYYY-MM-DD.")
                history_box.configure(state="disabled")
                return

            for inv in sales:
                if inv.get("date", "").startswith(selected_date):
                    filtered.append(inv)
        else:
            filtered = sales

        if not filtered:
            history_box.insert("end", "No invoices found for this date.")
            history_box.configure(state="disabled")
            return

        for inv in filtered:
            history_box.insert(
                "end",
                f"Invoice: {inv.get('invoice_no')} | "
                f"Date: {inv.get('date')} | "
                f"Total: ₱{inv.get('total'):.2f} | "
                f"Method: {inv.get('payment_method')}\n"
            )
            for it in inv.get("items", []):
                history_box.insert(
                    "end",
                    f"   - {it['product']} x{it['quantity']} = ₱{it['total']:.2f}\n"
                )
            history_box.insert("end", "-" * 80 + "\n")

        history_box.configure(state="disabled")

    date_entry.bind("<KeyRelease>", lambda e: render_history())

    render_history()