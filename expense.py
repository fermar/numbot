import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


_EXPENSE_PATTERN = re.compile(
    r"^\s*(?:[$€£]\s*)?(\d+(?:[.,]\d{1,2})?)\s+(.+?)\s*$"
)


@dataclass(frozen=True)
class Expense:
    amount: Decimal
    description: str


def parse_expense(message: str) -> Expense:
    match = _EXPENSE_PATTERN.fullmatch(message)
    if match is None:
        raise ValueError("Usa el formato: monto descripción (por ejemplo: 12,50 café).")

    try:
        amount = Decimal(match.group(1).replace(",", "."))
    except InvalidOperation as error:
        raise ValueError("El monto no es válido.") from error

    if not amount.is_finite() or amount <= 0:
        raise ValueError("El monto debe ser mayor que cero.")

    description = match.group(2).strip()
    if not description:
        raise ValueError("Incluye una descripción del gasto.")

    return Expense(amount=amount, description=description)
