from datetime import date, timedelta


def cadence_to_uses_per_day(cadence_value: float, cadence_unit: str) -> float:
    normalized = cadence_unit.strip().lower()
    if normalized == "day":
        return cadence_value
    if normalized == "week":
        return cadence_value / 7.0
    raise ValueError("cadence_unit must be either 'day' or 'week'")


def estimate_runout_date(
    package_size: float,
    opened_at: date,
    cadence_value: float,
    cadence_unit: str,
    amount_per_use: float,
) -> date:
    uses_per_day = cadence_to_uses_per_day(cadence_value, cadence_unit)
    daily_consumption = uses_per_day * amount_per_use
    if daily_consumption <= 0:
        raise ValueError("daily consumption must be positive")

    days_to_empty = package_size / daily_consumption
    return opened_at + timedelta(days=round(days_to_empty))
