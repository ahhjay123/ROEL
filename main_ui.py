import datetime
import os
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from db import (
    get_products,
    get_product_by_name,
    decrease_stock_by_name,
    increase_stock_by_name,
    delete_product,
    repair_image_paths,
)
from sale import save_invoice
from cart import Cart
from invoice import generate_invoice_pdf
from add_product_ui import open_add_product_window
from history_ui import open_history_window
from payment_ui import ask_payment_method

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOW_STOCK_THRESHOLD = 3
cart = Cart()


def start_main_ui():
    app = ctk.CTk()
    app.title("Appliance Sales System")
    app.geometry("1220x760")
    app.minsize(1100, 680)

    app.update_idletasks()
    w, h = 1220, 760
    x = (app.winfo_screenwidth() // 2) - (w // 2)
    y = (app.winfo_screenheight() // 2) - (h // 2)
    app.geometry(f"{w}x{h}+{x}+{y}")

    app.grid_rowconfigure(0, weight=0)
    app.grid_rowconfigure(1, weight=1)
    app.grid_columnconfigure(0, weight=0)
    app.grid_columnconfigure(1, weight=1)

    header = ctk.CTkFrame(app, height=80, corner_radius=0, fg_color="#111827")
    header.grid(row=0, column=0, columnspan=2, sticky="ew")
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        header,
        text="Appliance Sales System",
        font=("Arial Rounded MT Bold", 28),
    ).grid(row=0, column=0, padx=26, pady=(12, 0), sticky="w")

    ctk.CTkLabel(
        header,
        text=datetime.datetime.now().strftime("Today: %Y-%m-%d"),
        font=("Arial", 12),
        text_color="#9ca3af",
    ).grid(row=1, column=0, padx=26, pady=(0, 12), sticky="w")

    sidebar = ctk.CTkFrame(app, width=90, corner_radius=0, fg_color="#1f2937")
    sidebar.grid(row=1, column=0, sticky="ns")
    sidebar.grid_rowconfigure(8, weight=1)

    def _sidebar_button(icon, row, command=None):
        btn = ctk.CTkButton(
            sidebar,
            text=icon,
            width=70,
            height=70,
            font=("Segoe UI Emoji", 28),
            corner_radius=16,
            fg_color="#374151",
            hover_color="#1f6aa5",
            command=command,
        )
        btn.grid(row=row, column=0, padx=10, pady=10)
        return btn

    main = ctk.CTkFrame(app, fg_color="#0f172a")
    main.grid(row=1, column=1, padx=12, pady=12, sticky="nsew")
    main.grid_rowconfigure(0, weight=1)
    main.grid_columnconfigure(0, weight=2)
    main.grid_columnconfigure(1, weight=1)

    products_panel = ctk.CTkFrame(main, fg_color="#1e293b", corner_radius=12)
    products_panel.grid(row=0, column=0, padx=(10, 6), pady=10, sticky="nsew")
    products_panel.grid_rowconfigure(2, weight=1)
    products_panel.grid_columnconfigure(0, weight=1)

    header_frame = ctk.CTkFrame(products_panel, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
    header_frame.grid_columnconfigure(0, weight=1)
    header_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        header_frame,
        text="Products",
        font=("Arial Rounded MT Bold", 20),
    ).grid(row=0, column=0, sticky="w")

    search_entry = ctk.CTkEntry(
        header_frame,
        placeholder_text="Search product...",
        height=32,
    )
    search_entry.grid(row=0, column=1, sticky="e", padx=10)

    categories = [
        "Home Appliances",
        "Kitchen Appliances",
        "Living Room",
        "Other",
    ]
    current_category = {"value": categories[0]}

    cat_segment = ctk.CTkSegmentedButton(
        products_panel,
        values=categories,
        corner_radius=10
    )
    cat_segment.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="ew")
    cat_segment.set(categories[0])

    product_scroll = ctk.CTkScrollableFrame(
        products_panel,
        fg_color="transparent",
        corner_radius=12,
    )
    product_scroll.grid(row=2, column=0, padx=10, pady=(2, 12), sticky="nsew")
    product_scroll.grid_columnconfigure((0, 1, 2), weight=1)

    selected_product_name = {"name": None}
    product_card_widgets = {}

    right_panel = ctk.CTkFrame(main, fg_color="#1e293b", corner_radius=12)
    right_panel.grid(row=0, column=1, padx=(6, 10), pady=10, sticky="nsew")
    right_panel.grid_rowconfigure(2, weight=1)
    right_panel.grid_columnconfigure(0, weight=1)

    preview_frame = ctk.CTkFrame(
        right_panel, fg_color="#0f172a", corner_radius=12
    )
    preview_frame.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="ew")
    preview_frame.grid_columnconfigure(1, weight=1)

    preview_image_label = ctk.CTkLabel(
        preview_frame,
        text="",
        width=140,
        height=140,
        fg_color="#1f2937",
        corner_radius=10,
    )
    preview_image_label.grid(row=0, column=0, rowspan=3, padx=8, pady=8)

    selected_name_label = ctk.CTkLabel(
        preview_frame,
        text="No product selected",
        font=("Arial Rounded MT Bold", 16),
    )
    selected_name_label.grid(row=0, column=1, sticky="w", pady=(12, 4))

    selected_price_label = ctk.CTkLabel(
        preview_frame, text="Price: -", font=("Arial", 13)
    )
    selected_price_label.grid(row=1, column=1, sticky="w")

    selected_stock_label = ctk.CTkLabel(
        preview_frame, text="Stock: -", font=("Arial", 13)
    )
    selected_stock_label.grid(row=2, column=1, sticky="w", pady=(0, 8))

    qty_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    qty_frame.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="ew")
    qty_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(qty_frame, text="Quantity:", font=("Arial", 13)).grid(
        row=0, column=0, sticky="w", padx=(0, 6)
    )

    qty_entry = ctk.CTkEntry(qty_frame, height=35, corner_radius=8)
    qty_entry.insert(0, "1")
    qty_entry.grid(row=0, column=1, sticky="ew")

    cart_panel = ctk.CTkFrame(right_panel, fg_color="#0f172a", corner_radius=12)
    cart_panel.grid(row=2, column=0, padx=14, pady=(4, 12), sticky="nsew")
    cart_panel.grid_rowconfigure(1, weight=1)
    cart_panel.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(cart_panel, text="Cart", font=("Arial Rounded MT Bold", 18)).grid(
        row=0, column=0, sticky="w", padx=10, pady=(10, 2)
    )

    cart_scroll = ctk.CTkScrollableFrame(
        cart_panel, fg_color="transparent", corner_radius=12
    )
    cart_scroll.grid(row=1, column=0, padx=8, pady=(6, 6), sticky="nsew")
    cart_scroll.grid_columnconfigure(0, weight=1)

    total_label = ctk.CTkLabel(
        cart_panel,
        text="Total: ₱0.00",
        font=("Arial Rounded MT Bold", 16),
        text_color="#f8fafc",
    )
    total_label.grid(row=2, column=0, sticky="e", padx=12, pady=(0, 8))

    cart_btn_frame = ctk.CTkFrame(cart_panel, fg_color="transparent")
    cart_btn_frame.grid(row=3, column=0, padx=8, pady=(0, 10), sticky="ew")
    cart_btn_frame.grid_rowconfigure((0, 1), weight=0)
    cart_btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

    def _resolve_image_path(img_path):
        if not isinstance(img_path, str) or not img_path:
            return None
        if os.path.isabs(img_path):
            full_path = img_path
        else:
            full_path = os.path.join(BASE_DIR, img_path)
        return full_path if os.path.exists(full_path) else None

    def refresh_total():
        total_label.configure(text=f"Total: ₱{cart.get_total():.2f}")

    def render_cart_ui():
        for w in cart_scroll.winfo_children():
            w.destroy()

        if not cart.items:
            ctk.CTkLabel(
                cart_scroll, text="Cart is empty", font=("Arial", 12)
            ).grid(row=0, column=0, padx=6, pady=6, sticky="w")
            return

        for idx, (name, qty, total) in enumerate(cart.items):
            item_frame = ctk.CTkFrame(
                cart_scroll,
                corner_radius=10,
                fg_color="#1e293b",
                border_width=1
            )
            item_frame.grid(row=idx, column=0, padx=4, pady=4, sticky="ew")
            item_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                item_frame, text=name, font=("Arial Rounded MT Bold", 14)
            ).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))

            ctk.CTkLabel(
                item_frame,
                text=f"Qty: {qty}   •   Line: ₱{total:.2f}",
                font=("Arial", 12),
            ).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 6))

    def update_selected_preview():
        name = selected_product_name["name"]
        if not name:
            preview_image_label.configure(text="", image=None)
            preview_image_label.image = None
            selected_name_label.configure(text="No product selected")
            selected_price_label.configure(text="Price: -")
            selected_stock_label.configure(text="Stock: -")
            return

        product = get_product_by_name(name)
        if not product:
            selected_product_name["name"] = None
            update_selected_preview()
            return

        selected_name_label.configure(text=product["name"])
        selected_price_label.configure(text=f"Price: ₱{product['price']:.2f}")
        selected_stock_label.configure(text=f"Stock: {product['stock']}")

        img_path = _resolve_image_path(product.get("image_path"))
        if not img_path:
            preview_image_label.configure(text="No Image", image=None)
            preview_image_label.image = None
            return

        try:
            img = Image.open(img_path)
            img.thumbnail((150, 150))
            tk_img = ImageTk.PhotoImage(img)
            preview_image_label.configure(image=tk_img, text="")
            preview_image_label.image = tk_img
        except Exception:
            preview_image_label.configure(text="Image Error", image=None)
            preview_image_label.image = None

    def highlight_selected_card():
        for name, frame in product_card_widgets.items():
            if name == selected_product_name["name"]:
                frame.configure(border_width=2, border_color="#1f6aa5")
            else:
                frame.configure(border_width=1, border_color="#475569")

    def build_product_cards(cat):
        search = search_entry.get().lower().strip()

        for w in product_scroll.winfo_children():
            w.destroy()
        product_card_widgets.clear()

        rows = get_products(category=cat)
        if search:
            rows = [p for p in rows if search in p["name"].lower()]

        if not rows:
            ctk.CTkLabel(
                product_scroll,
                text="No products found.",
                font=("Arial", 12),
            ).grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        cols = 3
        for idx, p in enumerate(rows):
            r = idx // cols
            c = idx % cols

            card = ctk.CTkFrame(
                product_scroll,
                corner_radius=12,
                border_width=1,
                fg_color="#0f172a"
            )
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            img_label = ctk.CTkLabel(card, text="", width=100, height=90)
            img_label.grid(row=0, column=0, padx=6, pady=(8, 2))

            img_path = _resolve_image_path(p.get("image_path"))
            if img_path:
                try:
                    img = Image.open(img_path)
                    img.thumbnail((120, 100))
                    tk_img = ImageTk.PhotoImage(img)
                    img_label.configure(image=tk_img, text="")
                    img_label.image = tk_img
                except Exception:
                    img_label.configure(text="Image Error")
            else:
                img_label.configure(text="No Image")

            ctk.CTkLabel(
                card,
                text=p["name"],
                font=("Arial Rounded MT Bold", 14),
                wraplength=150,
                justify="center",
            ).grid(row=1, column=0, padx=6, pady=2)

            ctk.CTkLabel(
                card,
                text=f"₱{p['price']:.2f}",
                font=("Arial", 13),
            ).grid(row=2, column=0, padx=6, pady=0)

            stock_text = f"Stock: {p['stock']}"
            if p["stock"] <= LOW_STOCK_THRESHOLD:
                stock_text += "  ⚠"

            ctk.CTkLabel(card, text=stock_text, font=("Arial", 12)).grid(
                row=3, column=0, padx=6, pady=(0, 4)
            )

            def on_select(n=p["name"]):
                selected_product_name["name"] = n
                highlight_selected_card()
                update_selected_preview()

            card.bind("<Button-1>", lambda e, _n=p["name"]: on_select(_n))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, _n=p["name"]: on_select(_n))

            select_btn = ctk.CTkButton(
                card,
                text="Select",
                height=30,
                corner_radius=10,
                fg_color="#1f6aa5",
                hover_color="#155c8e",
                command=on_select,
            )
            select_btn.grid(row=4, column=0, padx=8, pady=(4, 8), sticky="ew")

            product_card_widgets[p["name"]] = card

        highlight_selected_card()

    def on_search(event):
        build_product_cards(current_category["value"])

    search_entry.bind("<KeyRelease>", on_search)

    def on_category_change(value):
        current_category["value"] = value
        build_product_cards(value)
        selected_product_name["name"] = None
        update_selected_preview()
        highlight_selected_card()

    cat_segment.configure(command=on_category_change)
    build_product_cards(categories[0])

    def add_to_cart():
        name = selected_product_name["name"]
        if not name:
            messagebox.showerror("Error", "Select a product first.")
            return

        try:
            qty = int(qty_entry.get())
            if qty <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Invalid quantity.")
            return

        product = get_product_by_name(name)
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return

        if qty > product["stock"]:
            messagebox.showerror("Error", f"Available stock: {product['stock']}")
            return

        line_total = round(product["price"] * qty, 2)
        cart.add(name, qty, line_total)
        render_cart_ui()
        refresh_total()

    def clear_cart():
        cart.clear()
        render_cart_ui()
        refresh_total()

    def checkout():
        if not cart.items:
            messagebox.showerror("Error", "Cart is empty.")
            return

        total = cart.get_total()
        items = cart.items.copy()

        def finished(method, paid, change, discount_type, discount_amount):
            from receipt_ui import open_receipt_window

            final_total = total - discount_amount

            invoice_no = save_invoice(
                items,
                final_total,
                method,
                paid,
                change,
                discount_type,
                discount_amount
            )

            for name, qty, _ in items:
                try:
                    decrease_stock_by_name(name, qty)
                except Exception:
                    pass

            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            items_dict = [
                {"product": i[0], "quantity": i[1], "total": i[2]} for i in items
            ]
            try:
                generate_invoice_pdf(
                    invoice_no, date, items_dict,
                    final_total, method, paid, change,
                    discount_type, discount_amount
                )
            except Exception:
                pass

            cart.clear()
            render_cart_ui()
            refresh_total()
            build_product_cards(current_category["value"])

            open_receipt_window(
                invoice_no, date, items,
                final_total, method, paid, change,
                discount_type, discount_amount
            )

        ask_payment_method(total, finished)

    def add_stock_popup():
        name = selected_product_name["name"]
        if not name:
            messagebox.showerror("Error", "Select a product first.")
            return

        popup = ctk.CTkToplevel(app)
        popup.title("Add Stock")
        popup.geometry("350x210")

        popup.update_idletasks()
        w, h = 350, 210
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")

        popup.lift()
        popup.focus_force()
        popup.grab_set()

        ctk.CTkLabel(
            popup, text=f"Add Stock for {name}", font=("Arial Rounded MT Bold", 14)
        ).pack(pady=12)

        qty_ent = ctk.CTkEntry(popup, height=34)
        qty_ent.insert(0, "1")
        qty_ent.pack(pady=10)

        def confirm():
            try:
                qty = int(qty_ent.get())
                if qty <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Error", "Invalid quantity.")
                return

            try:
                increase_stock_by_name(name, qty)
                messagebox.showinfo("Success", f"Added {qty} to {name}.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

            popup.destroy()
            build_product_cards(current_category["value"])
            update_selected_preview()

        ctk.CTkButton(
            popup, text="Add Stock", fg_color="orange", corner_radius=10, command=confirm
        ).pack(pady=10)

    def delete_selected_product():
        name = selected_product_name["name"]
        if not name:
            messagebox.showerror("Error", "Select a product to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
        )
        if not confirm:
            return

        product = get_product_by_name(name)
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return

        try:
            delete_product(product["id"])
            messagebox.showinfo("Success", f"Product '{name}' deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        selected_product_name["name"] = None
        update_selected_preview()
        build_product_cards(current_category["value"])

    def run_repair():
        repaired = repair_image_paths()
        messagebox.showinfo(
            "DB Repair Complete",
            f"Fixed {repaired} corrupted image entr{'y' if repaired == 1 else 'ies'}."
        )
        build_product_cards(current_category["value"])
        update_selected_preview()

    _sidebar_button("➕", 0, command=open_add_product_window)
    _sidebar_button("🧾", 1, command=open_history_window)
    _sidebar_button("🚪", 2, command=app.destroy)

    ctk.CTkButton(
        cart_btn_frame, text="Add to Cart", corner_radius=10,
        fg_color="#1f6aa5", hover_color="#155c8e", command=add_to_cart
    ).grid(row=0, column=0, padx=4, sticky="ew")

    ctk.CTkButton(
        cart_btn_frame, text="Checkout", corner_radius=10,
        fg_color="green", hover_color="#0f7f0f", command=checkout
    ).grid(row=0, column=1, padx=4, sticky="ew")

    ctk.CTkButton(
        cart_btn_frame, text="Clear Cart", corner_radius=10,
        fg_color="red", hover_color="#9b1c1c", command=clear_cart
    ).grid(row=0, column=2, padx=4, sticky="ew")

    ctk.CTkButton(
        cart_btn_frame,
        text="Delete Product",
        corner_radius=10,
        fg_color="#b91c1c",
        hover_color="#7f1111",
        command=delete_selected_product,
    ).grid(row=1, column=0, columnspan=3, padx=4, pady=(6, 2), sticky="ew")

    ctk.CTkButton(
        cart_btn_frame,
        text="Add Stock",
        corner_radius=10,
        fg_color="orange",
        hover_color="#cc8400",
        command=add_stock_popup,
    ).grid(row=2, column=0, columnspan=3, padx=4, pady=6, sticky="ew")

    render_cart_ui()
    refresh_total()

    app.mainloop()
