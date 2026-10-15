import unittest
from decimal import Decimal

from expense import parse_expense


class ParseExpenseTests(unittest.TestCase):
    def test_parses_decimal_comma_and_preserves_description(self) -> None:
        expense = parse_expense(" 12,50 café con leche ")

        self.assertEqual(expense.amount, Decimal("12.50"))
        self.assertEqual(expense.description, "café con leche")

    def test_parses_currency_symbol(self) -> None:
        expense = parse_expense("€8.75 transporte")

        self.assertEqual(expense.amount, Decimal("8.75"))
        self.assertEqual(expense.description, "transporte")

    def test_rejects_missing_description(self) -> None:
        with self.assertRaises(ValueError):
            parse_expense("15")

    def test_rejects_zero_or_negative_amount(self) -> None:
        for message in ("0 café", "-2 café"):
            with self.subTest(message=message), self.assertRaises(ValueError):
                parse_expense(message)

    def test_rejects_more_than_two_decimal_places(self) -> None:
        with self.assertRaises(ValueError):
            parse_expense("1.234 café")


if __name__ == "__main__":
    unittest.main()
