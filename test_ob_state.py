from ob_state import (
    get_ob_id,
    can_alert_first_tap,
    confirm_first_tap,
    is_already_tapped
)


symbol = "EUR/USD"
timeframe = "H4"

ob = {
    "type": "BULLISH OB",
    "time": "2026-09-12T10:00:00+00:00",
    "high": 1.1650,
    "low": 1.1630
}


print("\n" + "=" * 60)
print("OB STATE TEST")
print("=" * 60)


# First check
ob_id = get_ob_id(
    symbol,
    timeframe,
    ob
)

print("\nOB ID:")
print(ob_id)


first_check = can_alert_first_tap(
    symbol,
    timeframe,
    ob
)

print("\nFirst tap check:")

if first_check:
    print("✅ First tap can alert")
else:
    print("❌ Already tapped")


# Mark as tapped
confirm_first_tap(ob_id)

print("\nOB marked as tapped.")


# Second check
second_check = can_alert_first_tap(
    symbol,
    timeframe,
    ob
)

print("\nSecond tap check:")

if second_check:
    print("❌ ERROR: Duplicate alert allowed")
else:
    print("✅ Duplicate alert blocked")


# Final state
print("\nFinal tapped status:")

if is_already_tapped(ob_id):
    print("✅ OB state = TAPPED")
else:
    print("❌ OB state = NOT TAPPED")
