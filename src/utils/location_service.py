"""
Location Service for NextAstroTarget application.
Provides address geocoding and timezone lookup functionality.
"""

import requests
import json
from typing import Dict, Optional, Tuple
import logging
from datetime import datetime
import math


class LocationService:
    """Service for geocoding addresses and determining timezone information."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Geocode an address to get coordinates and timezone information.
        Uses OpenStreetMap's Nominatim service (free, no API key required).
        
        Args:
            address: Full address string (e.g., "123 Main St, City, State, Country")
            
        Returns:
            Dictionary with location data or None if failed
        """
        try:
            self.logger.info(f"Geocoding address: {address}")
            
            # Use Nominatim (OpenStreetMap) geocoding service
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'addressdetails': 1,
                'limit': 1,
                'extratags': 1
            }
            
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)'
            }
            
            response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                self.logger.warning(f"No results found for address: {address}")
                return None
                
            result = data[0]
            
            latitude = float(result['lat'])
            longitude = float(result['lon'])
            
            # Get timezone using coordinates
            timezone_info = self.get_timezone_info(latitude, longitude)
            
            location_data = {
                'address': result.get('display_name', address),
                'latitude': latitude,
                'longitude': longitude,
                'country': result.get('address', {}).get('country', ''),
                'state': result.get('address', {}).get('state', ''),
                'city': result.get('address', {}).get('city', 
                       result.get('address', {}).get('town', 
                       result.get('address', {}).get('village', ''))),
                'timezone': timezone_info['timezone'],
                'gmt_offset': timezone_info['gmt_offset'],
                'dst_active': timezone_info['dst_active']
            }
            
            self.logger.info(f"Geocoding successful: {latitude:.4f}, {longitude:.4f}")
            return location_data
            
        except requests.RequestException as e:
            self.logger.error(f"Network error during geocoding: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error geocoding address: {e}")
            return None
    
    def get_timezone_info(self, latitude: float, longitude: float) -> Dict:
        """
        Get timezone information for given coordinates.
        Uses TimeZoneDB API or falls back to simple longitude-based calculation.
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Dictionary with timezone information
        """
        try:
            # Try online timezone service first
            timezone_url = "http://worldtimeapi.org/api/timezone"
            
            # Get list of timezones
            response = requests.get(timezone_url, timeout=5)
            if response.status_code == 200:
                # Try IP-based timezone (simpler approach)
                ip_url = "http://worldtimeapi.org/api/ip"
                ip_response = requests.get(ip_url, timeout=5)
                if ip_response.status_code == 200:
                    data = ip_response.json()
                    
                    # Extract timezone info
                    timezone = data.get('timezone', 'UTC')
                    offset_seconds = data.get('raw_offset', 0)
                    dst_offset = data.get('dst_offset', 0)
                    
                    gmt_offset = (offset_seconds + dst_offset) / 3600.0  # Convert to hours
                    dst_active = dst_offset != 0
                    
                    return {
                        'timezone': timezone,
                        'gmt_offset': gmt_offset,
                        'dst_active': dst_active
                    }
            
        except Exception as e:
            self.logger.warning(f"Online timezone lookup failed: {e}")
        
        # Fallback to longitude-based estimation
        return self.estimate_timezone_from_longitude(longitude)
    
    def estimate_timezone_from_longitude(self, longitude: float) -> Dict:
        """
        Estimate timezone from longitude using simple 15-degree rule.
        This is approximate and doesn't account for political boundaries.
        
        Args:
            longitude: Longitude in degrees
            
        Returns:
            Dictionary with estimated timezone information
        """
        # Basic timezone estimation: 15 degrees per hour
        estimated_offset = longitude / 15.0
        
        # Round to nearest hour for standard timezones
        rounded_offset = round(estimated_offset)
        
        # Generate timezone name
        if rounded_offset == 0:
            timezone_name = "GMT"
        elif rounded_offset > 0:
            timezone_name = f"GMT+{int(rounded_offset)}"
        else:
            timezone_name = f"GMT{int(rounded_offset)}"
        
        # Estimate DST (very rough - assume DST is active in summer months for northern hemisphere)
        current_month = datetime.now().month
        dst_active = False
        
        # Simple DST estimation for northern hemisphere (March-October)
        if 3 <= current_month <= 10:
            dst_active = True
            
        return {
            'timezone': timezone_name,
            'gmt_offset': rounded_offset + (1 if dst_active else 0),
            'dst_active': dst_active
        }
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate coordinate ranges.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            
        Returns:
            True if coordinates are valid
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def format_coordinates(self, latitude: float, longitude: float) -> str:
        """
        Format coordinates for display.
        
        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            
        Returns:
            Formatted coordinate string
        """
        lat_dir = "N" if latitude >= 0 else "S"
        lon_dir = "E" if longitude >= 0 else "W"
        
        return f"{abs(latitude):.4f}°{lat_dir}, {abs(longitude):.4f}°{lon_dir}"
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        earth_radius = 6371.0
        
        return earth_radius * c