"""
Astronomical calculations utility for NextAstroTarget application.
Provides accurate calculations for sun/moon positions, phases, and timing.
"""

import math
from datetime import datetime, date, timedelta
from typing import Tuple, Dict, Any
import logging


class AstronomicalCalculator:
    """Handles astronomical calculations for target selection."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Astronomical constants
        self.J2000 = 2451545.0  # Julian day for J2000.0 epoch
        self.DEGREES_TO_RADIANS = math.pi / 180.0
        self.RADIANS_TO_DEGREES = 180.0 / math.pi
    
    def julian_day(self, dt: datetime) -> float:
        """Convert datetime to Julian day number."""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Add fractional part for time
        fraction = (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
        
        return jdn + fraction
    
    def local_sidereal_time(self, dt: datetime, longitude: float) -> float:
        """Calculate local sidereal time in hours."""
        jd = self.julian_day(dt)
        t = (jd - self.J2000) / 36525.0
        
        # Greenwich sidereal time at 0h UT
        gst0 = 6.697374558 + 2400.051336 * t + 0.000025862 * t * t
        
        # Local sidereal time
        ut_hours = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        lst = gst0 + 1.0027379093 * ut_hours + longitude / 15.0
        
        # Normalize to 0-24 hours
        while lst < 0:
            lst += 24
        while lst >= 24:
            lst -= 24
            
        return lst
    
    def calculate_sun_position(self, dt: datetime, latitude: float, longitude: float) -> Tuple[float, float]:
        """
        Calculate sun altitude and azimuth at given time and location.
        Returns: (altitude, azimuth) in degrees
        """
        try:
            jd = self.julian_day(dt)
            n = jd - self.J2000
            
            # Sun's mean longitude
            L = (280.460 + 0.9856474 * n) % 360
            
            # Sun's mean anomaly
            g = math.radians((357.528 + 0.9856003 * n) % 360)
            
            # Sun's ecliptic longitude
            lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
            
            # Sun's declination
            obliquity = math.radians(23.439 - 0.0000004 * n)
            alpha = math.atan2(math.cos(obliquity) * math.sin(lambda_sun), math.cos(lambda_sun))
            delta = math.asin(math.sin(obliquity) * math.sin(lambda_sun))
            
            # Hour angle
            lst = self.local_sidereal_time(dt, longitude)
            h = math.radians(15 * (lst - alpha * self.RADIANS_TO_DEGREES / 15.0))
            
            # Convert to horizontal coordinates
            lat_rad = math.radians(latitude)
            
            altitude = math.asin(
                math.sin(lat_rad) * math.sin(delta) +
                math.cos(lat_rad) * math.cos(delta) * math.cos(h)
            )
            
            azimuth = math.atan2(
                -math.sin(h),
                math.tan(delta) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(h)
            )
            
            # Convert to degrees and normalize azimuth
            altitude_deg = altitude * self.RADIANS_TO_DEGREES
            azimuth_deg = (azimuth * self.RADIANS_TO_DEGREES + 180) % 360
            
            return altitude_deg, azimuth_deg
            
        except Exception as e:
            self.logger.error(f"Error calculating sun position: {e}")
            return 0.0, 0.0
    
    def calculate_moon_position(self, dt: datetime, latitude: float, longitude: float) -> Tuple[float, float]:
        """
        Calculate moon altitude and azimuth at given time and location.
        Returns: (altitude, azimuth) in degrees
        """
        try:
            jd = self.julian_day(dt)
            t = (jd - self.J2000) / 36525.0
            
            # Moon's mean longitude
            L0 = (218.3164477 + 481267.88123421 * t) % 360
            
            # Moon's mean elongation
            D = (297.8501921 + 445267.1114034 * t) % 360
            
            # Sun's mean anomaly
            M = (357.5291092 + 35999.0502909 * t) % 360
            
            # Moon's mean anomaly
            M1 = (134.9633964 + 477198.8675055 * t) % 360
            
            # Argument of latitude
            F = (93.2720950 + 483202.0175233 * t) % 360
            
            # Convert to radians
            L0_rad = math.radians(L0)
            D_rad = math.radians(D)
            M_rad = math.radians(M)
            M1_rad = math.radians(M1)
            F_rad = math.radians(F)
            
            # Moon's longitude (simplified)
            lambda_moon = L0 + 6.289 * math.sin(M1_rad)
            lambda_moon += 1.274 * math.sin(2 * D_rad - M1_rad)
            lambda_moon += 0.658 * math.sin(2 * D_rad)
            lambda_moon_rad = math.radians(lambda_moon % 360)
            
            # Moon's latitude (simplified)
            beta_moon = 5.128 * math.sin(F_rad)
            beta_moon += 0.281 * math.sin(M1_rad + F_rad)
            beta_moon_rad = math.radians(beta_moon)
            
            # Convert to equatorial coordinates
            obliquity = math.radians(23.4393 - 0.0130042 * t)
            
            alpha = math.atan2(
                math.sin(lambda_moon_rad) * math.cos(obliquity) - 
                math.tan(beta_moon_rad) * math.sin(obliquity),
                math.cos(lambda_moon_rad)
            )
            
            delta = math.asin(
                math.sin(beta_moon_rad) * math.cos(obliquity) +
                math.cos(beta_moon_rad) * math.sin(obliquity) * math.sin(lambda_moon_rad)
            )
            
            # Hour angle
            lst = self.local_sidereal_time(dt, longitude)
            h = math.radians(15 * (lst - alpha * self.RADIANS_TO_DEGREES / 15.0))
            
            # Convert to horizontal coordinates
            lat_rad = math.radians(latitude)
            
            altitude = math.asin(
                math.sin(lat_rad) * math.sin(delta) +
                math.cos(lat_rad) * math.cos(delta) * math.cos(h)
            )
            
            azimuth = math.atan2(
                -math.sin(h),
                math.tan(delta) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(h)
            )
            
            # Convert to degrees and normalize
            altitude_deg = altitude * self.RADIANS_TO_DEGREES
            azimuth_deg = (azimuth * self.RADIANS_TO_DEGREES + 180) % 360
            
            return altitude_deg, azimuth_deg
            
        except Exception as e:
            self.logger.error(f"Error calculating moon position: {e}")
            return 0.0, 0.0
    
    def calculate_moon_phase(self, dt: datetime) -> float:
        """
        Calculate moon phase percentage (0-100).
        Returns: phase percentage (0 = new moon, 50 = first/last quarter, 100 = full moon)
        """
        try:
            jd = self.julian_day(dt)
            
            # Days since known new moon (Jan 6, 2000)
            days_since_new = jd - 2451549.5
            
            # Synodic period is approximately 29.53 days
            synodic_period = 29.530588853
            
            # Calculate phase
            phase = (days_since_new % synodic_period) / synodic_period
            
            # Convert to percentage (0-100)
            if phase < 0.5:
                # Waxing - 0 to 100%
                phase_percent = phase * 200
            else:
                # Waning - 100 to 0%
                phase_percent = (1 - phase) * 200
            
            return max(0, min(100, phase_percent))
            
        except Exception as e:
            self.logger.error(f"Error calculating moon phase: {e}")
            return 0.0
    
    def calculate_sun_times(self, latitude: float, longitude: float, target_date: date) -> Dict[str, datetime]:
        """
        Calculate sunrise, sunset, and twilight times for given location and date.
        Returns: dictionary with sunrise, sunset, nautical_dawn, nautical_dusk times
        """
        try:
            results = {}
            
            # Calculate for different sun altitudes
            # 0° = geometric horizon (sunrise/sunset)
            # -12° = nautical twilight
            sun_angles = {
                'sunrise': 0.0,
                'sunset': 0.0,
                'nautical_dawn': -12.0,
                'nautical_dusk': -12.0
            }
            
            for event_name, target_altitude in sun_angles.items():
                # Determine if we're looking for morning or evening event
                if 'sunrise' in event_name or 'dawn' in event_name:
                    # Morning events - start search at 4 AM
                    start_hour = 4
                    search_forward = True
                else:
                    # Evening events - start search at 6 PM  
                    start_hour = 18
                    search_forward = True
                
                dt = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour))
                
                # Binary search for the exact time
                best_time = dt
                best_diff = float('inf')
                
                # Coarse search - check every 15 minutes for 8 hours
                for minutes in range(0, 8*60, 15):
                    test_time = dt + timedelta(minutes=minutes)
                    altitude, _ = self.calculate_sun_position(test_time, latitude, longitude)
                    diff = abs(altitude - target_altitude)
                    
                    if diff < best_diff:
                        best_diff = diff
                        best_time = test_time
                
                # Fine search - check every minute around the best time
                for minutes in range(-30, 31):
                    test_time = best_time + timedelta(minutes=minutes)
                    altitude, _ = self.calculate_sun_position(test_time, latitude, longitude)
                    diff = abs(altitude - target_altitude)
                    
                    if diff < best_diff:
                        best_diff = diff
                        best_time = test_time
                
                results[event_name] = best_time
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating sun times: {e}")
            # Return default times
            base_time = datetime.combine(target_date, datetime.min.time())
            return {
                'sunrise': base_time.replace(hour=6),
                'sunset': base_time.replace(hour=18),
                'nautical_dawn': base_time.replace(hour=5),
                'nautical_dusk': base_time.replace(hour=19)
            }
    
    def calculate_sunset(self, latitude: float, longitude: float, target_date: date) -> datetime:
        """
        Calculate sunset time for given location and date.
        Returns: datetime object for sunset
        """
        try:
            sun_times = self.calculate_sun_times(latitude, longitude, target_date)
            return sun_times['sunset']
        except Exception as e:
            self.logger.error(f"Error calculating sunset: {e}")
            return datetime.combine(target_date, datetime.min.time().replace(hour=18))
    
    def calculate_moon_times(self, latitude: float, longitude: float, target_date: date) -> Dict[str, datetime]:
        """
        Calculate moonrise and moonset times for given location and date.
        Returns: dictionary with moonrise and moonset times
        """
        try:
            results = {}
            
            # Search for moonrise and moonset
            base_time = datetime.combine(target_date, datetime.min.time())
            
            for event_name in ['moonrise', 'moonset']:
                # Moonrise typically occurs during day, moonset during night
                if event_name == 'moonrise':
                    start_hour = 0  # Start at midnight
                else:
                    start_hour = 12  # Start at noon
                
                dt = base_time.replace(hour=start_hour)
                
                best_time = dt
                best_diff = float('inf')
                
                # Search over 24 hours with 30-minute intervals
                for minutes in range(0, 24*60, 30):
                    test_time = dt + timedelta(minutes=minutes)
                    altitude, _ = self.calculate_moon_position(test_time, latitude, longitude)
                    
                    # Look for when moon crosses horizon (0° altitude)
                    diff = abs(altitude - 0.0)
                    
                    # For moonrise, we want the time when altitude is increasing through 0°
                    # For moonset, we want the time when altitude is decreasing through 0°
                    if diff < best_diff:
                        # Check if this is the right crossing direction
                        prev_time = test_time - timedelta(minutes=15)
                        next_time = test_time + timedelta(minutes=15)
                        
                        prev_alt, _ = self.calculate_moon_position(prev_time, latitude, longitude)
                        next_alt, _ = self.calculate_moon_position(next_time, latitude, longitude)
                        
                        if event_name == 'moonrise' and next_alt > prev_alt:
                            # Rising through horizon
                            best_diff = diff
                            best_time = test_time
                        elif event_name == 'moonset' and next_alt < prev_alt:
                            # Setting through horizon
                            best_diff = diff
                            best_time = test_time
                
                # Fine-tune with 1-minute precision
                for minutes in range(-15, 16):
                    test_time = best_time + timedelta(minutes=minutes)
                    altitude, _ = self.calculate_moon_position(test_time, latitude, longitude)
                    diff = abs(altitude - 0.0)
                    
                    if diff < best_diff:
                        best_diff = diff
                        best_time = test_time
                
                results[event_name] = best_time
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating moon times: {e}")
            # Return default times
            base_time = datetime.combine(target_date, datetime.min.time())
            return {
                'moonrise': base_time.replace(hour=20),
                'moonset': base_time.replace(hour=8)
            }
    
    def calculate_altitude_azimuth(self, ra_hours: float, dec_degrees: float, 
                                 dt: datetime, latitude: float, longitude: float) -> Tuple[float, float]:
        """
        Calculate altitude and azimuth for given RA/Dec coordinates.
        
        Args:
            ra_hours: Right ascension in hours
            dec_degrees: Declination in degrees
            dt: Observation datetime
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees (negative for west)
            
        Returns:
            Tuple of (altitude, azimuth) in degrees
        """
        try:
            # Convert inputs to radians
            ra_rad = math.radians(ra_hours * 15)  # Convert hours to degrees then radians
            dec_rad = math.radians(dec_degrees)
            lat_rad = math.radians(latitude)
            
            # Calculate hour angle
            lst = self.local_sidereal_time(dt, longitude)
            h = math.radians(15 * (lst - ra_hours))  # Hour angle in radians
            
            # Calculate altitude
            altitude = math.asin(
                math.sin(lat_rad) * math.sin(dec_rad) +
                math.cos(lat_rad) * math.cos(dec_rad) * math.cos(h)
            )
            
            # Calculate azimuth
            azimuth = math.atan2(
                -math.sin(h),
                math.tan(dec_rad) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(h)
            )
            
            # Convert to degrees and normalize azimuth
            altitude_deg = altitude * self.RADIANS_TO_DEGREES
            azimuth_deg = (azimuth * self.RADIANS_TO_DEGREES + 180) % 360
            
            return altitude_deg, azimuth_deg
            
        except Exception as e:
            self.logger.error(f"Error calculating altitude/azimuth: {e}")
            return 0.0, 0.0
    
    def calculate_transit_time(self, ra_hours: float, longitude: float, 
                             target_date: date) -> datetime:
        """
        Calculate transit time (when object crosses meridian) for given RA and date.
        
        Args:
            ra_hours: Right ascension in hours
            longitude: Observer longitude in degrees (negative for west)
            target_date: Date for calculation
            
        Returns:
            datetime object for transit time
        """
        try:
            # Start with midnight
            dt = datetime.combine(target_date, datetime.min.time())
            
            # Calculate when LST equals RA
            for hour in range(24):
                test_time = dt + timedelta(hours=hour)
                lst = self.local_sidereal_time(test_time, longitude)
                
                # Check if LST is close to RA
                if abs(lst - ra_hours) < 0.5 or abs(lst - ra_hours + 24) < 0.5 or abs(lst - ra_hours - 24) < 0.5:
                    # Fine-tune with minutes
                    for minute in range(60):
                        test_time_min = test_time + timedelta(minutes=minute)
                        lst_min = self.local_sidereal_time(test_time_min, longitude)
                        
                        if abs(lst_min - ra_hours) < 0.02:  # Within about 1 minute
                            return test_time_min
                    
                    return test_time
            
            # Fallback - approximate transit
            return dt + timedelta(hours=ra_hours)
            
        except Exception as e:
            self.logger.error(f"Error calculating transit time: {e}")
            return datetime.combine(target_date, datetime.min.time().replace(hour=12))
    
    def calculate_moon_separation(self, ra_hours: float, dec_degrees: float, 
                                dt: datetime) -> float:
        """
        Calculate angular separation between object and moon.
        
        Args:
            ra_hours: Object right ascension in hours
            dec_degrees: Object declination in degrees
            dt: Observation datetime
            
        Returns:
            Angular separation in degrees
        """
        try:
            # This is a simplified calculation
            # In reality, would need moon's RA/Dec at the given time
            
            jd = self.julian_day(dt)
            t = (jd - self.J2000) / 36525.0
            
            # Approximate moon RA/Dec (simplified)
            moon_L = (218.3164477 + 481267.88123421 * t) % 360
            moon_ra_hours = moon_L / 15.0
            moon_dec = 0.0  # Simplified - moon dec varies
            
            # Calculate angular separation using spherical trigonometry
            ra1_rad = math.radians(ra_hours * 15)
            dec1_rad = math.radians(dec_degrees)
            ra2_rad = math.radians(moon_ra_hours * 15)
            dec2_rad = math.radians(moon_dec)
            
            # Haversine formula for great circle distance
            dra = ra2_rad - ra1_rad
            
            a = (math.sin((dec2_rad - dec1_rad) / 2) ** 2 +
                 math.cos(dec1_rad) * math.cos(dec2_rad) * 
                 math.sin(dra / 2) ** 2)
            
            separation = 2 * math.asin(math.sqrt(a))
            
            return separation * self.RADIANS_TO_DEGREES
            
        except Exception as e:
            self.logger.error(f"Error calculating moon separation: {e}")
            return 90.0  # Default to 90 degrees if calculation fails
    
    def is_object_observable(self, ra_hours: float, dec_degrees: float,
                           dt: datetime, latitude: float, longitude: float,
                           min_altitude: float = 30.0) -> Dict[str, Any]:
        """
        Check if an object is observable at given time and location.
        
        Args:
            ra_hours: Right ascension in hours
            dec_degrees: Declination in degrees
            dt: Observation datetime
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            min_altitude: Minimum altitude for observability in degrees
            
        Returns:
            Dictionary with observability information
        """
        try:
            altitude, azimuth = self.calculate_altitude_azimuth(
                ra_hours, dec_degrees, dt, latitude, longitude
            )
            
            observable = altitude >= min_altitude
            
            # Calculate when object will be at minimum altitude
            transit_time = self.calculate_transit_time(ra_hours, longitude, dt.date())
            
            # Calculate moon separation
            moon_separation = self.calculate_moon_separation(ra_hours, dec_degrees, dt)
            
            return {
                'observable': observable,
                'altitude': altitude,
                'azimuth': azimuth,
                'transit_time': transit_time,
                'moon_separation': moon_separation,
                'good_moon_separation': moon_separation > 20.0  # At least 20 degrees from moon
            }
            
        except Exception as e:
            self.logger.error(f"Error checking observability: {e}")
            return {
                'observable': False,
                'altitude': 0.0,
                'azimuth': 0.0,
                'transit_time': dt,
                'moon_separation': 0.0,
                'good_moon_separation': False
            }