import tkinter as tk
from tkinter import ttk


# Simulated parsing function (replace this with your own)
def parse_items(invoice):
    splitted_1 = invoice.split("\n\n")

    arranged = [[splitted_1[0]]]
    for i in range(1, len(splitted_1) - 1):
        couple = splitted_1[i].split("\n")
        arranged[i - 1].append("\n".join(couple[:-1]))
        arranged.append([couple[-1]])
    arranged[-1].append(splitted_1[-1])

    extracted_price = []
    total_price = 0
    for couple in arranged:
        name = couple[0]
        details = couple[1].split("\n")
        quantity = int(details[0][1:])
        price = round(float(details[1].replace(",", ".")), 2)
        if len(details) > 3:
            price += round(float(details[-1][:-1].replace(",", ".")), 2)
        price = round(price, 2)

        extracted_price.append((name, quantity, price))
        total_price += price

    return extracted_price, total_price


person_names = ["Adrien", "Nicolas", "Matthieu", "Thibault"]


class ShoppingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopping List Splitter")

        self.discounts = []

        # Input text area
        self.input_text = tk.Text(root, height=6, width=100)
        self.input_text.pack(fill="x", padx=5, pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.parse_button = tk.Button(
            button_frame, text="Parse and Load Items", command=self.load_items
        )
        self.parse_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="Clear Input",
            command=lambda: self.input_text.delete("1.0", tk.END),
        )
        self.clear_button.pack(side="left", padx=5)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Left side: item table
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right side: discounts and totals
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side="right", fill="y", padx=10)

        # Discount entry area
        tk.Label(self.right_frame, text="Discount amount:").pack()
        self.discount_amount_entry = tk.Entry(self.right_frame, width=10)
        self.discount_amount_entry.pack(pady=2)
        self.discount_type = ttk.Combobox(
            self.right_frame,
            values=["Proportional", "Equal"],
            state="readonly",
            width=15,
        )
        self.discount_type.set("Proportional")
        self.discount_type.pack(pady=2)
        tk.Button(
            self.right_frame, text="Add Discount", command=self.add_discount
        ).pack(pady=2)

        # List of discounts
        self.discount_listbox = tk.Listbox(self.right_frame, height=6, width=30)
        self.discount_listbox.pack(pady=2)
        tk.Button(
            self.right_frame,
            text="Remove Selected Discount",
            command=self.remove_discount,
        ).pack(pady=2)

        # Total labels
        self.total_label = tk.Label(
            self.right_frame, text="Total Price: 0.00", fg="green"
        )
        self.total_label.pack(pady=5)

        self.discount_total_label = tk.Label(
            self.right_frame, text="Total Discounts: 0.00", fg="green"
        )
        self.discount_total_label.pack(pady=2)

        self.adjusted_total_label = tk.Label(
            self.right_frame, text="Total after Discounts: 0.00", fg="green"
        )
        self.adjusted_total_label.pack(pady=2)

        self.person_totals_label = tk.Label(self.right_frame, text="")
        self.person_totals_label.pack(pady=5)

        # Scrollable frame setup
        self.canvas = tk.Canvas(self.left_frame)
        self.scroll_y = tk.Scrollbar(
            self.left_frame, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.frame = tk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.frame, anchor="nw"
        )

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind("<Configure>", self.resize_canvas)

        # Header row
        self.headers = ["Article", "Qty", "Price"] + person_names + ["All"]
        for col, header in enumerate(self.headers):
            label = tk.Label(
                self.frame,
                text=header,
                font=("Arial", 10, "bold"),
                borderwidth=1,
                relief="solid",
                padx=5,
                pady=5,
            )
            label.grid(row=0, column=col, sticky="nsew")

        self.item_widgets = []
        self.item_data = []

        self.total_price = 0.0

    def resize_canvas(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def load_items(self):
        for widget_row in self.item_widgets:
            for widget in widget_row:
                widget.destroy()
        self.item_widgets.clear()
        self.item_data.clear()

        raw_text = self.input_text.get("1.0", tk.END).strip()
        items, self.total_price = parse_items(raw_text)

        for row_index, (article, qty, price) in enumerate(items, start=1):
            row_widgets = []
            tk.Label(
                self.frame, text=article, borderwidth=1, relief="solid", padx=5
            ).grid(row=row_index, column=0, sticky="nsew")
            tk.Label(self.frame, text=qty, borderwidth=1, relief="solid", padx=5).grid(
                row=row_index, column=1, sticky="nsew"
            )
            tk.Label(
                self.frame, text=price, borderwidth=1, relief="solid", padx=5
            ).grid(row=row_index, column=2, sticky="nsew")

            row_widgets.extend(
                [
                    self.frame.grid_slaves(row=row_index, column=0)[0],
                    self.frame.grid_slaves(row=row_index, column=1)[0],
                    self.frame.grid_slaves(row=row_index, column=2)[0],
                ]
            )

            person_vars = [tk.BooleanVar(value=False) for _ in person_names]
            all_var = tk.BooleanVar(value=True)
            in_all_update = {"flag": False}

            def make_person_trace(pvars, allvar):
                def on_person_check(*_):
                    if in_all_update["flag"]:
                        return
                    if any(var.get() for var in pvars):
                        allvar.set(False)
                    elif not allvar.get():
                        allvar.set(True)
                    self.update_totals()

                return on_person_check

            def make_all_trace(pvars, allvar):
                def on_all_check(*_):
                    if allvar.get():
                        in_all_update["flag"] = True
                        for var in pvars:
                            var.set(False)
                        self.frame.after_idle(lambda: in_all_update.update(flag=False))
                    elif not any(var.get() for var in pvars):
                        self.frame.after_idle(lambda: allvar.set(True))
                    self.update_totals()

                return on_all_check

            person_trace = make_person_trace(person_vars, all_var)
            all_trace = make_all_trace(person_vars, all_var)

            for i, var in enumerate(person_vars):
                var.trace_add("write", person_trace)
                cb = tk.Checkbutton(self.frame, variable=var)
                cb.grid(row=row_index, column=3 + i)
                row_widgets.append(cb)

            all_var.trace_add("write", all_trace)
            all_cb = tk.Checkbutton(self.frame, variable=all_var)
            all_cb.grid(row=row_index, column=3 + len(person_names))
            row_widgets.append(all_cb)

            self.item_widgets.append(row_widgets)
            self.item_data.append((price, person_vars, all_var))

        self.update_totals()

    def update_totals(self):
        totals = {name: 0.0 for name in person_names}
        for price, person_vars, all_var in self.item_data:
            if all_var.get():
                share = price / len(person_names)
                for name in person_names:
                    totals[name] += share
            else:
                selected = [
                    name for var, name in zip(person_vars, person_names) if var.get()
                ]
                if selected:
                    share = price / len(selected)
                    for name in selected:
                        totals[name] += share

        discount_contributions = {name: 0.0 for name in person_names}
        total_discount = sum(float(d["amount"]) for d in self.discounts)

        for discount in self.discounts:
            if discount["type"] == "Proportional":
                total_sum = sum(totals.values())
                for name in person_names:
                    if total_sum > 0:
                        share = discount["amount"] * (totals[name] / total_sum)
                        totals[name] -= share
                        discount_contributions[name] += share
            else:
                share = discount["amount"] / len(person_names)
                for name in person_names:
                    totals[name] -= share
                    discount_contributions[name] += share

        adjusted_total = self.total_price - total_discount

        self.discount_total_label.config(text=f"Total Discounts: {total_discount:.2f}")
        self.total_label.config(text=f"Total Price: {self.total_price:.2f}")
        self.adjusted_total_label.config(
            text=f"Total after Discounts: {adjusted_total:.2f}"
        )

        self.person_totals_label.config(
            text="\n".join(
                f"{name}: {totals[name]:.2f} (\u2193{discount_contributions[name]:.2f})"
                for name in person_names
            )
        )

    def add_discount(self):
        try:
            value = float(self.discount_amount_entry.get())
            if 0 <= value <= self.total_price:
                discount = {"amount": value, "type": self.discount_type.get()}
                self.discounts.append(discount)
                self.discount_listbox.insert(
                    tk.END, f"{discount['type']} - {value:.2f}"
                )
                self.update_totals()
        except ValueError:
            pass

    def remove_discount(self):
        selection = self.discount_listbox.curselection()
        if selection:
            index = selection[0]
            self.discount_listbox.delete(index)
            del self.discounts[index]
            self.update_totals()


# Run app
root = tk.Tk()
app = ShoppingApp(root)
root.mainloop()
