import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class InvoicePDF:
    def __init__(
        self,
        invoice_number,
        date_str,
        customer_name,
        items,
        final_total,
        payment_method,
        paid_amount,
        change_amount
    ):
        self.customer_name = customer_name
        self.invoice_number = invoice_number
        self.date_str = date_str
        self.items = items
        self.final_total = float(final_total)
        self.original_total = sum(i["total"] for i in items)
        self.payment_method = payment_method
        self.paid_amount = float(paid_amount)
        self.change_amount = float(change_amount)
        self.folder = "invoices"
        os.makedirs(self.folder, exist_ok=True)

    @property
    def filename(self):
        return os.path.join(self.folder, f"invoice_{self.invoice_number}.pdf")

    def generate(self):
        c = canvas.Canvas(self.filename, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, y, "APPLIANCE SALES SYSTEM")
        y -= 35

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"INVOICE #{self.invoice_number}")
        y -= 20

        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Date: {self.date_str}")
        y -= 30

        c.drawString(50, y, f"Customer: {self.customer_name}")
        y -= 25

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Item")
        c.drawString(260, y, "Price")
        c.drawString(330, y, "Qty")
        c.drawString(390, y, "Total")
        y -= 18

        c.setFont("Helvetica", 11)

        for item in self.items:
            name = str(item["product"])
            qty = int(item["quantity"])
            total = float(item["total"])
            unit_price = total / qty if qty else 0.0

            c.drawString(50, y, name[:35])
            c.drawString(260, y, f"₱{unit_price:.2f}")
            c.drawString(330, y, str(qty))
            c.drawString(390, y, f"₱{total:.2f}")

            y -= 16
            if y < 100:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Item")
                c.drawString(260, y, "Price")
                c.drawString(330, y, "Qty")
                c.drawString(390, y, "Total")
                y -= 18
                c.setFont("Helvetica", 11)

        y -= 25
        c.setFont("Helvetica-Bold", 12)

        c.drawString(50, y, f"Original Total: ₱{self.original_total:.2f}")
        y -= 18

        c.drawString(50, y, f"FINAL TOTAL: ₱{self.final_total:.2f}")
        y -= 25

        c.drawString(50, y, f"Payment Method: {self.payment_method}")
        y -= 18

        if self.payment_method == "Cash":
            c.drawString(50, y, f"Cash Given: ₱{self.paid_amount:.2f}")
            y -= 18
            c.drawString(50, y, f"Change: ₱{self.change_amount:.2f}")
            y -= 18

        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(50, y, "Thank you for your purchase!")

        c.showPage()
        c.save()

        return self.filename


def generate_invoice_pdf(
    invoice_number,
    date_str,
    customer_name,
    items,
    final_total,
    payment_method,
    paid_amount,
    change_amount,
):

    pdf = InvoicePDF(
        invoice_number,
        date_str,
        customer_name,
        items,
        final_total,
        payment_method,
        paid_amount,
        change_amount,
    )

    return pdf.generate()
