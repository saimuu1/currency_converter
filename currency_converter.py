import tkinter as tk
import requests

# -----------------------------
# Available currency options
# -----------------------------
common_currencies = [
    'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 'NZD',
    'SEK', 'NOK', 'DKK', 'SGD', 'INR', 'KRW', 'MXN', 'BRL', 'ZAR', 'RUB'
]

class CurrencyConverter:

    def __init__(self):
        # -----------------------------
        # Window setup
        # -----------------------------
        self.root = tk.Tk()
        self.root.title("Currency Converter")
        self.root.geometry("250x230")

        # -----------------------------
        # Currency selection inputs
        # -----------------------------
        self.initial_var = tk.StringVar(self.root, value="USD")
        self.initial_menu = tk.OptionMenu(self.root, self.initial_var, *common_currencies)
        self.initial_menu.pack(pady=2)

        self.target_var = tk.StringVar(self.root, value="EUR")
        self.target_menu = tk.OptionMenu(self.root, self.target_var, *common_currencies)
        self.target_menu.pack(pady=2)

        # -----------------------------
        # Amount input
        # -----------------------------
        self.amount_label = tk.Label(self.root, text="Amount:")
        self.amount_label.pack(pady=2)

        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack(pady=2)

        # -----------------------------
        # Convert action
        # -----------------------------
        self.convert_button = tk.Button(self.root, text="Convert", command=self.convert_money)
        self.convert_button.pack(pady=2)

        # -----------------------------
        # Result display
        # -----------------------------
        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack(pady=2)

        self.root.mainloop()

    def convert_money(self):
        try:
            # -----------------------------
            # Read user input
            # -----------------------------
            amount = float(self.amount_entry.get())
            from_currency = self.initial_var.get()
            to_currency = self.target_var.get()

            # -----------------------------
            # API request
            # -----------------------------
            url = "https://api.frankfurter.app/latest"
            params = {
                "amount": amount,
                "from": from_currency,
                "to": to_currency
            }

            response = requests.get(url, params=params)
            data = response.json()

            # -----------------------------
            # Extract and display result
            # -----------------------------
            result = data["rates"][to_currency]

            self.result_label.config(text=f"Converted Amount: {result}")

        except ValueError:
            self.result_label.config(text="Please enter a valid amount!")
        except Exception:
            self.result_label.config(text="Error in conversion!")

if __name__ == "__main__":
    CurrencyConverter()
