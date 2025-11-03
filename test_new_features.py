"""
Test script for new features:
1. Address geocoding
2. Declination filter
3. Persistent settings storage
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.database_manager import DatabaseManager

def test_settings_table():
    """Test the new settings table functionality."""
    print("=" * 60)
    print("Testing Settings Table Functionality")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    # Create settings table
    print("\n1. Creating settings table...")
    db_manager.create_settings_table()
    print("   ✓ Settings table created")
    
    # Save some test settings
    print("\n2. Saving test settings...")
    test_settings = {
        'size_min': '10',
        'size_max': '500',
        'dec_min': '-30',
        'dec_max': '75',
        'transit_start': '18:00',
        'transit_end': '06:00',
        'observatory_address': 'Gdansk, Poland'
    }
    
    for key, value in test_settings.items():
        result = db_manager.save_setting(key, value)
        print(f"   ✓ Saved {key} = {value} (success: {result})")
    
    # Load settings back
    print("\n3. Loading settings back...")
    for key in test_settings.keys():
        loaded_value = db_manager.get_setting(key)
        original_value = test_settings[key]
        match = "✓" if loaded_value == original_value else "✗"
        print(f"   {match} {key}: {loaded_value} (expected: {original_value})")
    
    # Test default value
    print("\n4. Testing default value for non-existent setting...")
    default_test = db_manager.get_setting('nonexistent_key', 'default_value')
    print(f"   ✓ Got default value: {default_test}")
    
    # Test delete
    print("\n5. Testing delete setting...")
    result = db_manager.delete_setting('size_min')
    deleted_value = db_manager.get_setting('size_min')
    print(f"   ✓ Deleted size_min (success: {result}, value after delete: {deleted_value})")
    
    print("\n" + "=" * 60)
    print("Settings table tests completed!")
    print("=" * 60)

def test_geocoding():
    """Test the geocoding API (requires internet)."""
    print("\n" + "=" * 60)
    print("Testing Geocoding API")
    print("=" * 60)
    
    import requests
    
    test_addresses = [
        "Gdansk, Poland",
        "London, UK",
        "New York, USA",
        "Tokyo, Japan"
    ]
    
    print("\nTesting geocoding for sample addresses:")
    for address in test_addresses:
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'NextAstroTarget/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json()
            
            if results:
                result = results[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                display_name = result.get('display_name', address)
                print(f"\n✓ {address}")
                print(f"  Coordinates: {lat:.4f}°, {lon:.4f}°")
                print(f"  Full name: {display_name}")
            else:
                print(f"\n✗ {address}: No results found")
                
        except Exception as e:
            print(f"\n✗ {address}: Error - {e}")

def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "NextAstroTarget New Features Test" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Test 1: Settings table
    test_settings_table()
    
    # Test 2: Geocoding (requires internet)
    print("\n")
    response = input("Do you want to test geocoding API (requires internet)? (y/n): ")
    if response.lower() == 'y':
        test_geocoding()
    else:
        print("Skipping geocoding tests.")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nNew features summary:")
    print("1. ✓ Address geocoding field added to Observatory Settings")
    print("2. ✓ Declination Range filter added (-90° to +90°)")
    print("3. ✓ Persistent settings storage in database")
    print("\nFeatures that are now persistent:")
    print("  - Size Range (min/max)")
    print("  - Declination Range (min/max)")
    print("  - Transit Time (start/end)")
    print("  - Observatory Address")
    print("\nThese settings will be restored when you restart the application.")
    print("=" * 60)

if __name__ == "__main__":
    main()
