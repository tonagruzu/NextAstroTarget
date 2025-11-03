"""Test Python's rounding behavior."""

cycle = 0.4737
result = cycle * 29
print(f"cycle * 29 = {result}")
print(f"round({result}) = {round(result)}")
print(f"int({result} + 0.5) = {int(result + 0.5)}")

# Python uses "round half to even" (banker's rounding)
print()
print("Python rounding:")
print(f"round(13.5) = {round(13.5)}")  # rounds to 14 (even)
print(f"round(14.5) = {round(14.5)}")  # rounds to 14 (even)
print(f"round(13.74) = {round(13.74)}")  # rounds to 14
print(f"round(13.74) + 1 = {round(13.74) + 1}")  # = 15
