import customtkinter as ctk
from tkinter import messagebox

from main_ui import start_main_ui

USERS = {
    "admin": "admin123",
    "user": "user123",
}


def start_login_ui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Appliance Sales System - Login")
    app.geometry("760x420")

    app.update_idletasks()
    w, h = 760, 420
    x = (app.winfo_screenwidth() // 2) - (w // 2)
    y = (app.winfo_screenheight() // 2) - (h // 2)
    app.geometry(f"{w}x{h}+{x}+{y}")

    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    root = ctk.CTkFrame(app, corner_radius=0)
    root.grid(row=0, column=0, sticky="nsew")
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    left_panel = ctk.CTkFrame(root, fg_color="#111827", corner_radius=0)
    left_panel.grid(row=0, column=0, sticky="nsw")
    left_panel.configure(width=240)
    left_panel.grid_propagate(False)

    left_panel.grid_columnconfigure(0, weight=1)
    left_panel.grid_rowconfigure(0, weight=1)

    ctk.CTkLabel(
        left_panel, text="⚙️", font=("Segoe UI Emoji", 48)
    ).grid(row=0, column=0, pady=(40, 0), sticky="n")

    ctk.CTkLabel(
        left_panel,
        text="Appliance\nSales System",
        font=("Arial Rounded MT Bold", 22),
        justify="center",
    ).grid(row=0, column=0, pady=(140, 0), sticky="n")

    ctk.CTkLabel(
        left_panel,
        text="Fast • Simple • Reliable",
        font=("Arial", 12),
        text_color="#9ca3af",
    ).grid(row=0, column=0, pady=(260, 0), sticky="n")

    right = ctk.CTkFrame(root, fg_color="transparent")
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(0, weight=1)

    card = ctk.CTkFrame(right, corner_radius=16)
    card.grid(row=0, column=0, padx=50, pady=40, sticky="n")
    card.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        card, text="Welcome back", font=("Arial Rounded MT Bold", 26)
    ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 0))

    ctk.CTkLabel(
        card,
        text="Sign in to manage appliance sales",
        font=("Arial", 13),
        text_color="#9ca3af",
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(4, 20))

    form = ctk.CTkFrame(card, fg_color="transparent")
    form.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    form.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(form, text="Username", anchor="w", font=("Arial", 12, "bold")).grid(
        row=0, column=0, sticky="w"
    )
    username_entry = ctk.CTkEntry(form, placeholder_text="Enter username", height=38)
    username_entry.grid(row=1, column=0, sticky="ew", pady=(2, 10))

    ctk.CTkLabel(form, text="Password", anchor="w", font=("Arial", 12, "bold")).grid(
        row=2, column=0, sticky="w"
    )
    password_entry = ctk.CTkEntry(
        form, placeholder_text="Enter password", height=38, show="*"
    )
    password_entry.grid(row=3, column=0, sticky="ew", pady=(2, 10))

    ctk.CTkLabel(
        form,
        text="Default accounts: admin/admin123 • user/user123",
        font=("Arial", 10),
        text_color="#9ca3af",
    ).grid(row=4, column=0, sticky="w", pady=(0, 10))

    def login():
        u = username_entry.get().strip()
        p = password_entry.get().strip()

        if USERS.get(u) == p:
            messagebox.showinfo("Success", f"Welcome {u}!")
            app.after(150, lambda: [app.destroy(), start_main_ui()])
        else:
            messagebox.showerror("Error", "Invalid username or password")

    login_btn = ctk.CTkButton(
        card,
        text="Login",
        height=42,
        fg_color="#1f6aa5",
        hover_color="#155c8e",
        command=login,
    )
    login_btn.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")

    username_entry.bind("<Return>", lambda e: login())
    password_entry.bind("<Return>", lambda e: login())
    login_btn.bind("<Return>", lambda e: login())

    app.mainloop()