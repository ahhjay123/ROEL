import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from db import add_product

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


def open_add_product_window():
    window = ctk.CTkToplevel()
    window.title("Add New Product")
    window.geometry("480x560")
    window.resizable(False, False)

    window.update_idletasks()
    w, h = 480, 560
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.lift()
    window.focus_force()
    window.grab_set()
    window.attributes("-topmost", True)
    window.after(10, lambda: window.attributes("-topmost", False))

    main_frame = ctk.CTkFrame(window, corner_radius=16)
    main_frame.pack(fill="both", expand=True, padx=18, pady=18)

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=2)

    title = ctk.CTkLabel(
        main_frame, text="Add New Product", font=("Arial Rounded MT Bold", 20)
    )
    title.grid(row=0, column=0, columnspan=2, pady=(8, 16))

    ctk.CTkLabel(main_frame, text="Product Name:", anchor="e").grid(
        row=1, column=0, sticky="e", padx=(10, 8), pady=(4, 4)
    )
    name_entry = ctk.CTkEntry(main_frame, placeholder_text="e.g. Washing Machine", height=32)
    name_entry.grid(row=1, column=1, sticky="ew", pady=(4, 4))

    categories = [
        "Home Appliances",
        "Kitchen Appliances",
        "Living Room",
        "Other",
    ]
    ctk.CTkLabel(main_frame, text="Category:", anchor="e").grid(
        row=2, column=0, sticky="e", padx=(10, 8), pady=(4, 4)
    )
    category_combo = ctk.CTkComboBox(main_frame, values=categories, height=32)
    category_combo.grid(row=2, column=1, sticky="ew", pady=(4, 4))
    category_combo.set(categories[0])

    ctk.CTkLabel(main_frame, text="Price:", anchor="e").grid(
        row=3, column=0, sticky="e", padx=(10, 8), pady=(4, 4)
    )
    price_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00", height=32)
    price_entry.grid(row=3, column=1, sticky="ew", pady=(4, 4))

    ctk.CTkLabel(main_frame, text="Product Image:", anchor="e").grid(
        row=4, column=0, sticky="e", padx=(10, 8), pady=(8, 4)
    )

    img_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#0f172a")
    img_frame.grid(row=4, column=1, sticky="ew", pady=(4, 4))
    img_frame.grid_columnconfigure(0, weight=1)

    img_preview_label = ctk.CTkLabel(
        img_frame, text="No Image", width=180, height=180, corner_radius=10, fg_color="#1f2937"
    )
    img_preview_label.grid(row=0, column=0, pady=(6, 6), padx=6)

    image_state = {"file": None}

    def choose_image():
        file = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")],
        )
        if not file:
            return

        image_state["file"] = file

        try:
            img = Image.open(file)
            img.thumbnail((180, 180))
            preview = ImageTk.PhotoImage(img)
            img_preview_label.configure(image=preview, text="")
            img_preview_label.image = preview
        except Exception:
            img_preview_label.configure(text="Preview Error", image=None)
            img_preview_label.image = None

    ctk.CTkButton(
        img_frame,
        text="Upload Image",
        fg_color="#1f6aa5",
        hover_color="#155c8e",
        corner_radius=10,
        command=choose_image,
    ).grid(row=1, column=0, pady=(4, 8), padx=6, sticky="ew")

    def save_product():
        name = name_entry.get().strip()
        category = category_combo.get()
        raw_image = image_state["file"]

        try:
            price = float(price_entry.get())
            if not name:
                raise ValueError("Name cannot be empty.")
            if price < 0:
                raise ValueError("Price must be non-negative.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        stock = 0
        stored_path = None

        if raw_image:
            try:
                ext = os.path.splitext(raw_image)[1]
                safe_name = name.replace(" ", "_")
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{safe_name}_{ts}{ext}"
                final_image_path = os.path.join(IMAGES_DIR, filename)
                shutil.copy2(raw_image, final_image_path)

                stored_path = os.path.join("images", filename)
            except Exception as e:
                messagebox.showwarning("Image Error", f"Image not saved: {e}")
                stored_path = None

        add_product(name, category, price, stock, stored_path)
        messagebox.showinfo("Success", f"Product '{name}' added.")
        window.destroy()

    ctk.CTkButton(
        main_frame,
        text="Save Product",
        fg_color="green",
        hover_color="#0f7f0f",
        height=38,
        corner_radius=10,
        command=save_product,
    ).grid(row=10, column=0, columnspan=2, pady=20, padx=16, sticky="ew")