import os
import customtkinter as ctk

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def open_receipt_window(
        invoice_no,
        date_str,
        customer_name,
        items,
        total_price,
        payment_method,
        paid,
        change,
):


    window = ctk.CTkToplevel()
    window.title("Receipt / Invoice")
    window.geometry("520x640")
    window.resizable(False, False)

    window.update_idletasks()
    w, h = 520, 640
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
    main.grid_rowconfigure(2, weight=1)
    main.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        main,
        text=f"INVOICE: {invoice_no}",
        font=("Arial Rounded MT Bold", 20),
    ).grid(row=0, column=0, pady=(6, 2), sticky="n")

    ctk.CTkLabel(
        main,
        text=f"Date: {date_str}",
        font=("Arial", 11),
    ).grid(row=1, column=0, pady=(0, 10), sticky="n")

    ctk.CTkLabel(
        main,
        text=f"Customer: {customer_name}",
        font=("Arial Rounded MT Bold", 14)
    ).grid(row=2, column=0, pady=(0, 10), sticky="n")

    box = ctk.CTkTextbox(main, width=500, height=520, corner_radius=10)
    box.grid(row=3, column=0, pady=(4, 6), sticky="nsew")

    box.insert("end", "Items Purchased:\n")
    box.insert("end", f"Customer Name: {customer_name}\n")
    box.insert("end", "-" * 50 + "\n")


    original_total = 0
    for name, qty, total in items:
        original_total += total
        box.insert("end", f"{name} x{qty} - ₱{total:.2f}\n")

    box.insert("end", "-" * 50 + "\n")
    box.insert("end", f"Original Total: ₱{original_total:.2f}\n")
    box.insert("end", f"Final Total: ₱{total_price:.2f}\n")
    box.insert("end", "-" * 50 + "\n")
    box.insert("end", f"Payment Method: {payment_method}\n")

    if payment_method == "Cash":
        box.insert("end", f"Cash Given: ₱{paid:.2f}\n")
        box.insert("end", f"Change: ₱{change:.2f}\n")

    box.insert("end", "-" * 50 + "\n")
    box.insert("end", "Thank you for your purchase!\n")

    box.configure(state="disabled")
