import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests

COMMON_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'NZD', 'INR', 'CNY']

# small fallback table (used only if network completely fails)
FALLBACK_RATES = {
    ('USD','EUR'): 0.92,
    ('EUR','USD'): 1.09,
    ('USD','GBP'): 0.80,
    ('GBP','USD'): 1.25,
}

API_TIMEOUT = 8  # seconds

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter (no API key)")
        self.root.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        ttk.Label(self.root, text="From:").grid(row=0, column=0, sticky="e", **pad)
        self.from_var = tk.StringVar(value="USD")
        self.from_combo = ttk.Combobox(self.root, textvariable=self.from_var, values=COMMON_CURRENCIES, state="readonly", width=12)
        self.from_combo.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(self.root, text="To:").grid(row=1, column=0, sticky="e", **pad)
        self.to_var = tk.StringVar(value="EUR")
        self.to_combo = ttk.Combobox(self.root, textvariable=self.to_var, values=COMMON_CURRENCIES, state="readonly", width=12)
        self.to_combo.grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(self.root, text="Amount:").grid(row=2, column=0, sticky="e", **pad)
        self.amount_entry = ttk.Entry(self.root, width=14)
        self.amount_entry.grid(row=2, column=1, sticky="w", **pad)
        self.amount_entry.insert(0, "1.00")

        self.convert_btn = ttk.Button(self.root, text="Convert", command=self._on_convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, **pad)

        self.status_label = ttk.Label(self.root, text="", wraplength=320, justify="center")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(4,10))

    def _on_convert(self):
        amount_text = self.amount_entry.get().strip()
        if not amount_text:
            messagebox.showwarning("Input required", "Please enter an amount to convert.")
            return
        try:
            amount = float(amount_text)
            if amount < 0:
                raise ValueError("Negative not allowed")
        except ValueError:
            messagebox.showerror("Invalid amount", "Please enter a valid non-negative number for amount.")
            return

        from_curr = self.from_var.get()
        to_curr = self.to_var.get()
        if not from_curr or not to_curr:
            messagebox.showwarning("Currency required", "Please choose both source and target currencies.")
            return

        # UI feedback
        self.convert_btn.config(state="disabled")
        self.status_label.config(text="Fetching rate...", foreground="blue")

        # background fetch
        thread = threading.Thread(target=self._fetch_and_display, args=(from_curr, to_curr, amount), daemon=True)
        thread.start()

    def _fetch_and_display(self, from_curr, to_curr, amount):
        """
        Use Frankfurter API:
        Example: https://api.frankfurter.app/latest?from=USD&to=EUR&amount=1
        Response:
        {
          "amount":1,
          "base":"USD",
          "date":"2025-12-16",
          "rates":{"EUR":0.92}
        }
        """
        try:
            url = "https://api.frankfurter.app/latest"
            params = {"from": from_curr, "to": to_curr, "amount": amount}
            resp = requests.get(url, params=params, timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            # defensive checks
            if not isinstance(data, dict) or "rates" not in data:
                raise RuntimeError("Unexpected API response format")

            rates = data.get("rates", {})
            if to_curr not in rates:
                raise RuntimeError("Target currency not found in response")

            converted = rates[to_curr]
            # frankfurter returns the converted amount directly (since we passed amount)
            rate = converted / amount if amount != 0 else 0.0

            text = f"{amount:.2f} {from_curr} = {converted:.2f} {to_curr}  (1 {from_curr} = {rate:.6f} {to_curr})"
            self.root.after(0, lambda: self._show_result(text))
        except Exception as e:
            # fallback attempt
            key = (from_curr, to_curr)
            if key in FALLBACK_RATES:
                rate = FALLBACK_RATES[key]
                converted = amount * rate
                text = f"[fallback] {amount:.2f} {from_curr} = {converted:.2f} {to_curr}  (1 {from_curr} = {rate:.6f} {to_curr})"
                self.root.after(0, lambda: self._show_result(text))
            else:
                err_text = f"Could not fetch rate (network/API). Error: {e}"
                self.root.after(0, lambda: self._show_error(err_text))
        finally:
            self.root.after(0, lambda: self.convert_btn.config(state="normal"))

    def _show_result(self, text):
        self.status_label.config(text=text, foreground="green")

    def _show_error(self, text):
        self.status_label.config(text=text, foreground="red")

if __name__ == "__main__":
    from tkinter import ttk
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
