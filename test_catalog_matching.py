#!/usr/bin/env python3

import re

def test_catalog_matching():
    """Test the improved catalog number matching logic."""
    
    # Sample data to test against
    test_objects = [
        "M 031 Andromeda Galaxy",
        "M031",
        "M31",
        "NGC 031",
        "NGC31", 
        "NGC 0031",
        "M 001 Crab Nebula",
        "M1",
        "M 01",
        "NGC 6960 Veil Nebula",
        "IC 434 Horsehead"
    ]
    
    # Test searches
    test_searches = [
        "M31", "M 31", "m31", "m 31",
        "NGC31", "NGC 31", "ngc31", "ngc 31",
        "31", "1", "6960", "434"
    ]
    
    print("Testing Catalog Number Matching")
    print("=" * 50)
    
    for search_term in test_searches:
        print(f"\nSearching for: '{search_term}'")
        search_lower = search_term.lower().strip()
        
        matches = []
        
        # Test catalog pattern matching
        catalog_pattern = re.match(r'^([a-z]+)\s*(\d+)$', search_lower)
        if catalog_pattern:
            prefix = catalog_pattern.group(1)
            number = catalog_pattern.group(2)
            number_int = int(number)
            number_padded = f"{number_int:03d}"
            
            patterns = [
                f"{prefix}\\s*0*{number_int}\\b",      
                f"{prefix}\\s+0*{number_int}\\b",      
                f"{prefix}\\s*{number_padded}\\b",     
                f"{prefix}\\s+{number_padded}\\b"      
            ]
            
            print(f"  Catalog detected: {prefix.upper()} {number_int}")
            print(f"  Patterns to test: {patterns}")
            
            for obj in test_objects:
                for pattern in patterns:
                    if re.search(pattern, obj, re.IGNORECASE):
                        if obj not in matches:
                            matches.append(obj)
                            break
        
        # Test pure number matching
        elif re.match(r'^\d+$', search_term.strip()):
            number = search_term.strip()
            number_int = int(number)
            number_padded = f"{number_int:03d}"
            
            number_patterns = [
                f"\\b0*{number_int}\\b",     
                f"\\b{number_padded}\\b",    
                f"\\s{number_int}\\b",       
                f"\\s{number_padded}\\b"     
            ]
            
            print(f"  Number detected: {number_int}")
            print(f"  Patterns to test: {number_patterns}")
            
            for obj in test_objects:
                for pattern in number_patterns:
                    if re.search(pattern, obj, re.IGNORECASE):
                        if obj not in matches:
                            matches.append(obj)
                            break
        
        if matches:
            print(f"  ✓ Found matches:")
            for match in matches:
                print(f"    - {match}")
        else:
            print(f"  ✗ No matches found")

if __name__ == "__main__":
    test_catalog_matching()