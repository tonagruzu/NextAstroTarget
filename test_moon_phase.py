#!/usr/bin/env python3

from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.astronomical_calculations import AstronomicalCalculator

def test_moon_phase():
    """Test the improved moon phase calculation."""
    
    calc = AstronomicalCalculator()
    
    # Test current moon phase
    now = datetime.now()
    phase_data = calc.calculate_moon_phase(now)
    
    print("CURRENT MOON PHASE CALCULATION")
    print("=" * 50)
    print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Phase name: {phase_data['phase_name']}")
    print(f"Illumination: {phase_data['illumination']:.1f}%")
    print(f"Cycle position: {phase_data['cycle_position']:.3f} (0=New, 0.5=Full)")
    print(f"Direction: {'Waxing' if phase_data['is_waxing'] else 'Waning'}")
    print(f"Days since new moon: {phase_data['days_since_new']:.1f}")
    
    # Test some known dates for verification
    test_dates = [
        # Known moon phases (approximate)
        ("2024-01-11", "New Moon"),      # New Moon
        ("2024-01-18", "First Quarter"), # First Quarter  
        ("2024-01-25", "Full Moon"),     # Full Moon
        ("2024-02-02", "Last Quarter"),  # Last Quarter
    ]
    
    print(f"\nTEST DATES VERIFICATION")
    print("=" * 50)
    
    for date_str, expected_phase in test_dates:
        test_date = datetime.strptime(date_str + " 12:00:00", "%Y-%m-%d %H:%M:%S")
        phase_data = calc.calculate_moon_phase(test_date)
        
        print(f"{date_str}: {phase_data['phase_name']} ({phase_data['illumination']:.0f}%) - Expected: {expected_phase}")
    
    # Show lunar cycle progression
    print(f"\nLUNAR CYCLE PROGRESSION (Next 30 days)")
    print("=" * 50)
    
    from datetime import timedelta
    
    for i in range(0, 30, 3):  # Every 3 days
        future_date = now + timedelta(days=i)
        phase_data = calc.calculate_moon_phase(future_date)
        
        print(f"{future_date.strftime('%m-%d')}: {phase_data['phase_name']:<15} ({phase_data['illumination']:3.0f}%)")

if __name__ == "__main__":
    test_moon_phase()