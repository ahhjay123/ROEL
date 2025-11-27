import customtkinter as ctk
from tkinter import messagebox

def ask_payment_method(total_amount, callback):
    window = ctk.CTkToplevel()
    window.title("Select Payment Method")
    window.geometry("460x360")

    window.update_idletasks()
    w, h = 460, 360
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.lift()
    window.focus_force()
    window.grab_set()
    window.attributes("-topmost", True)
    window.after(10, lambda: window.attributes("-topmost", False))

    main = ctk.CTkFrame(window, corner_radius=16)
    main.pack(fill="both", expand=True, padx=14, pady=14)

    ctk.CTkLabel(
        main, text="Payment", font=("Arial Rounded MT Bold", 20)
    ).pack(pady=(6, 4))

    total_label = ctk.CTkLabel(
        main,
        text=f"Amount Due: ₱{total_amount:.2f}",
        font=("Arial Rounded MT Bold", 16),
    )
    total_label.pack(pady=(0, 10))

    ctk.CTkLabel(
        main,
        text="Choose a payment method:",
        font=("Arial", 13),
        text_color="#9ca3af",
    ).pack(pady=(0, 10))

    btn_row = ctk.CTkFrame(main, fg_color="transparent")
    btn_row.pack(pady=(0, 10), padx=10, fill="x")
    btn_row.grid_columnconfigure((0, 1, 2), weight=1)

    def pay(method):
        window.destroy()

        if method == "Cash":
            ask_cash_amount(total_amount, callback)
        else:
            callback(method, total_amount, 0.00, None, 0.0)


    ctk.CTkButton(btn_row, text="💵  Cash", height=40,
        corner_radius=10, command=lambda: pay("Cash")).grid(row=0, column=0, padx=4)

    ctk.CTkButton(btn_row, text="💳  Card", height=40,
        corner_radius=10, command=lambda: pay("Card")).grid(row=0, column=1, padx=4)

    ctk.CTkButton(btn_row, text="📱  GCash", height=40,
        corner_radius=10, command=lambda: pay("GCash")).grid(row=0, column=2, padx=4)


def ask_cash_amount(total_amount, callback):
    window = ctk.CTkToplevel()
    window.title("Cash Payment")
    window.geometry("400x240")

    window.update_idletasks()
    w, h = 400, 240
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.lift()
    window.focus_force()
    window.grab_set()

    main = ctk.CTkFrame(window, corner_radius=16)
    main.pack(fill="both", expand=True, padx=14, pady=14)

    ctk.CTkLabel(main, text="Cash Payment",
        font=("Arial Rounded MT Bold", 18)).pack(pady=(10, 6))

    ctk.CTkLabel(main, text=f"Total: ₱{total_amount:.2f}",
        font=("Arial Rounded MT Bold", 16)).pack(pady=(0, 10))

    ctk.CTkLabel(main, text="Enter cash received:",
        font=("Arial", 13)).pack(pady=(0, 6))

    cash_entry = ctk.CTkEntry(main, width=220, height=36)
    cash_entry.pack(pady=(0, 10))

    def process_cash():
        value = cash_entry.get().strip()
        if not value:
            messagebox.showerror("Error", "Enter a valid cash amount!")
            return

        try:
            cash = float(value)
        except ValueError:
            messagebox.showerror("Error", "Invalid cash amount!")
            return

        if cash < total_amount:
            messagebox.showerror("Error", "Insufficient cash!")
            return

        change = round(cash - total_amount, 2)

        window.destroy()
        callback("Cash", cash, change, None, 0.0)
        
    ctk.CTkButton(
        main,
        text="Confirm Payment",
        height=38,
        corner_radius=10,
        command=process_cash,
    ).pack(pady=(4, 6))

    cash_entry.bind("<Return>", lambda e: process_cash())
