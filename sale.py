import datetime
import json
import os

from db import get_product_by_name, record_sale

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SALES_FILE = os.path.join(BASE_DIR, "sales_history.json")

class Invoice:
    def __init__(
        self,
        items,
        final_total,
        payment_method,
        paid_amount,
        change_amount,
        discount_type=None,
        discount_amount=0.0,
    ):
        self.items = items
        self.original_total = sum(i[2] for i in items)
        self.discount_type = discount_type or "NONE"
        self.discount_amount = float(discount_amount)
        self.discount_applied = self.discount_amount > 0
        self.total_amount = float(final_total)
        self.payment_method = payment_method
        self.paid_amount = float(paid_amount)
        self.change_amount = float(change_amount)
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.invoice_no = None

    def to_dict(self):
        return {
            "invoice_no": self.invoice_no,
            "date": self.date,
            "items": [
                {"product": n, "quantity": q, "total": t}
                for (n, q, t) in self.items
            ],
            "original_total": self.original_total,
            "discount_type": self.discount_type,
            "discount_amount": self.discount_amount,
            "discount_applied": self.discount_applied,
            "total": self.total_amount,
            "payment_method": self.payment_method,
            "paid": self.paid_amount,
            "change": self.change_amount,
        }

class SaleManager:
    def __init__(self, json_path):
        self.json_path = json_path
        self.sales = self._load()

    def _load(self):
        if not os.path.exists(self.json_path):
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.sales, f, indent=4, ensure_ascii=False)

    def _next_invoice(self):
        if not self.sales:
            return "INV-0001"
        nums = []
        for inv in self.sales:
            try:
                nums.append(int(inv["invoice_no"].split("-")[1]))
            except:
                pass
        nxt = max(nums) + 1 if nums else 1
        return f"INV-{nxt:04d}"

    def save_invoice(
        self,
        items,
        final_total,
        payment_method,
        paid,
        change,
        discount_type,
        discount_amount
    ):
        invoice = Invoice(
            items,
            final_total,
            payment_method,
            paid,
            change,
            discount_type,
            discount_amount
        )

        invoice.invoice_no = self._next_invoice()

        self.sales.append(invoice.to_dict())
        self._save()

        for name, qty, line_total in items:
            product = get_product_by_name(name)
            if product:
                record_sale(
                    product["id"],
                    qty,
                    line_total,
                    invoice.date
                )

        return invoice.invoice_no

_SALE_MANAGER = SaleManager(SALES_FILE)

def save_invoice(
    items,
    final_total,
    payment_method,
    paid,
    change,
    discount_type,
    discount_amount
):
    return _SALE_MANAGER.save_invoice(
        items,
        final_total,
        payment_method,
        paid,
        change,
        discount_type,
        discount_amount
    )

def get_sales_history():
    return _SALE_MANAGER.sales