import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "appliance_store.db")

class Product:
    def __init__(self, name, category, price, stock, image_path=None):
        self.name = name
        self.category = category
        self.price = float(price)
        self.stock = int(stock)
        self.image_path = image_path

class DatabaseManager:
    def __init__(self, db_path, base_dir):
        self.db_path = db_path
        self.base_dir = base_dir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_database(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                image_path TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """
        )

        conn.commit()
        conn.close()

    def add_product(self, product: Product):
        conn = self.connect()
        cursor = conn.cursor()

        if self.product_exists(product.name):
            conn.close()
            raise ValueError(f"Product '{product.name}' already exists.")

        cursor.execute(
            """
            INSERT INTO products (name, category, price, stock, image_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (product.name, product.category, product.price, product.stock, product.image_path),
        )

        conn.commit()
        conn.close()

    def get_products(self, category=None):
        conn = self.connect()
        cursor = conn.cursor()

        if category:
            cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM products")

        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_product_by_name(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE name = ? LIMIT 1", (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def change_stock(self, product_id, delta):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError("Product not found")

        new_stock = row["stock"] + delta
        if new_stock < 0:
            conn.close()
            raise ValueError("Stock cannot go below zero")

        cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))

        conn.commit()
        conn.close()

    def delete_product(self, product_id):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT image_path FROM products WHERE id=?", (product_id,))
        row = cursor.fetchone()

        if row:
            img_path = row["image_path"]

            if isinstance(img_path, str) and img_path:
                if os.path.isabs(img_path):
                    full = img_path
                else:
                    full = os.path.join(self.base_dir, img_path)

                if os.path.exists(full):
                    try:
                        os.remove(full)
                    except:
                        pass

        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()

    def repair_image_paths(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id, image_path FROM products")
        rows = cursor.fetchall()

        fixed = 0
        for r in rows:
            if isinstance(r["image_path"], (bytes, bytearray)):
                cursor.execute("UPDATE products SET image_path=NULL WHERE id=?", (r["id"],))
                fixed += 1

        conn.commit()
        conn.close()
        return fixed

    def record_sale(self, product_id, quantity, total, date_str):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sales (product_id, quantity, total, date)
            VALUES (?, ?, ?, ?)
            """,
            (product_id, quantity, total, date_str),
        )
    
        conn.commit()
        conn.close()

    def product_exists(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM products WHERE name = ? LIMIT 1", (name,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

_db = DatabaseManager(DB_PATH, BASE_DIR)

def get_connection():
    return _db.connect()

def initialize_database():
    _db.initialize_database()

def print_db_location():
    print("Using DB:", DB_PATH)

def add_product(name, category, price, stock, image_path=None):
    try:
        _db.add_product(Product(name, category, price, stock, image_path))
    except ValueError as e:
        raise e

def get_products(category=None):
    return _db.get_products(category)

def get_product_by_name(name):
    return _db.get_product_by_name(name)

def change_stock(product_id, delta):
    _db.change_stock(product_id, delta)

def increase_stock_by_name(name, qty):
    p = get_product_by_name(name)
    if not p: raise ValueError("Product not found")
    _db.change_stock(p["id"], qty)

def decrease_stock_by_name(name, qty):
    p = get_product_by_name(name)
    if not p: raise ValueError("Product not found")
    _db.change_stock(p["id"], -qty)

def record_sale(product_id, quantity, total, date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _db.record_sale(product_id, quantity, total, date)

def delete_product(product_id):
    _db.delete_product(product_id)

def repair_image_paths():
    return _db.repair_image_paths()
