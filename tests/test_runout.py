from datetime import date

from corejunkie_app.runout import cadence_to_uses_per_day, estimate_runout_date


def test_cadence_conversion_day():
    assert cadence_to_uses_per_day(2, "day") == 2


def test_cadence_conversion_week():
    assert cadence_to_uses_per_day(7, "week") == 1


def test_estimate_runout_date():
    runout = estimate_runout_date(
        package_size=16,
        opened_at=date(2026, 3, 31),
        cadence_value=2,
        cadence_unit="day",
        amount_per_use=0.5,
    )
    assert runout == date(2026, 4, 16)
