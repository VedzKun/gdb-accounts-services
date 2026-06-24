"""
Currency Conversion Utility
Module 1: Language Fundamentals with Python
"""
def convert_currency(amount: float, from_curr: str, to_curr: str) -> float:
    # Validating input types to prevent future errors
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise TypeError("Amount must be a number (int or float)")
    if not isinstance(from_curr, str) or not isinstance(to_curr, str):
        raise TypeError("Currency codes must be strings")

    from_curr_upper = from_curr.upper()
    to_curr_upper = to_curr.upper()

    supported_currencies = {"INR", "USD", "EUR"}
    if from_curr_upper not in supported_currencies:
        raise ValueError(f"Unsupported source currency: {from_curr}")
    if to_curr_upper not in supported_currencies:
        raise ValueError(f"Unsupported target currency: {to_curr}")

    if from_curr_upper == to_curr_upper:
        return round(float(amount), 2)

    # Convert from source currency to INR 
    amount_in_inr = 0.0
    if from_curr_upper == "INR":
        amount_in_inr = float(amount)
    elif from_curr_upper == "USD":
        amount_in_inr = float(amount) * 94.0
    elif from_curr_upper == "EUR":
        amount_in_inr = float(amount) * 90.0

    # Convert from INR to target currency
    converted_amount = 0.0
    if to_curr_upper == "INR":
        converted_amount = amount_in_inr
    elif to_curr_upper == "USD":
        converted_amount = amount_in_inr / 94.0
    elif to_curr_upper == "EUR":
        converted_amount = amount_in_inr / 90.0

    return round(converted_amount, 2)
