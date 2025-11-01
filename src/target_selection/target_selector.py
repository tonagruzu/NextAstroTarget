"""
Target selection module for NextAstroTarget application.
Contains logic for selecting optimal astrophotography targets.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import math

from src.database.database_manager import DatabaseManager


@dataclass
class ObservingLocation:
    """Represents an observing location."""
    latitude: float  # degrees
    longitude: float  # degrees
    elevation: float = 0.0  # meters
    timezone_offset: float = 0.0  # hours from UTC
    name: str = "Unknown Location"


@dataclass
class ObservingConditions:
    """Represents observing conditions and constraints."""
    start_time: datetime
    end_time: datetime
    min_altitude: float = 30.0  # degrees
    max_magnitude: float = 15.0
    moon_separation_min: float = 20.0  # degrees
    atmospheric_extinction: float = 0.2  # magnitudes per airmass
    seeing_limit: float = 3.0  # arcseconds


@dataclass
class TargetInfo:
    """Information about a celestial target."""
    name: str
    ra: float  # right ascension in degrees
    dec: float  # declination in degrees
    magnitude: float
    object_type: str
    constellation: str
    size_major: float = 0.0  # arcminutes
    size_minor: float = 0.0  # arcminutes
    distance: float = 0.0  # light years or Mpc
    notes: str = ""


class AstronomicalCalculations:
    """Astronomical calculations for target selection."""
    
    @staticmethod
    def ra_dec_to_degrees(ra_str: str, dec_str: str) -> Tuple[float, float]:
        """Convert RA/Dec strings to decimal degrees."""
        try:
            # Handle various RA formats (HH:MM:SS or decimal hours)
            if ':' in str(ra_str):
                parts = str(ra_str).split(':')
                ra_hours = float(parts[0]) + float(parts[1])/60.0
                if len(parts) > 2:
                    ra_hours += float(parts[2])/3600.0
                ra_deg = ra_hours * 15.0  # Convert hours to degrees
            else:
                ra_deg = float(ra_str) * 15.0 if float(ra_str) <= 24 else float(ra_str)
            
            # Handle various Dec formats (DD:MM:SS or decimal degrees)
            if ':' in str(dec_str):
                parts = str(dec_str).split(':')
                sign = -1 if parts[0].startswith('-') else 1
                dec_deg = abs(float(parts[0])) + float(parts[1])/60.0
                if len(parts) > 2:
                    dec_deg += float(parts[2])/3600.0
                dec_deg *= sign
            else:
                dec_deg = float(dec_str)
            
            return ra_deg, dec_deg
            
        except (ValueError, IndexError, AttributeError):
            return 0.0, 0.0
    
    @staticmethod
    def calculate_local_sidereal_time(longitude: float, utc_datetime: datetime) -> float:
        """Calculate local sidereal time in degrees."""
        # Simplified calculation - for production use a proper astronomy library
        j2000_epoch = datetime(2000, 1, 1, 12, 0, 0)
        days_since_j2000 = (utc_datetime - j2000_epoch).total_seconds() / 86400.0
        
        # Greenwich Mean Sidereal Time at 0h UT
        gmst = 280.46061837 + 360.98564736629 * days_since_j2000
        
        # Local sidereal time
        lst = gmst + longitude
        
        # Normalize to 0-360 degrees
        return lst % 360.0
    
    @staticmethod
    def calculate_altitude_azimuth(ra: float, dec: float, lst: float, latitude: float) -> Tuple[float, float]:
        """Calculate altitude and azimuth for given coordinates."""
        # Convert to radians
        ra_rad = math.radians(ra)
        dec_rad = math.radians(dec)
        lst_rad = math.radians(lst)
        lat_rad = math.radians(latitude)
        
        # Hour angle
        ha = lst_rad - ra_rad
        
        # Altitude calculation
        sin_alt = (math.sin(dec_rad) * math.sin(lat_rad) + 
                  math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha))
        altitude = math.degrees(math.asin(max(-1, min(1, sin_alt))))
        
        # Azimuth calculation
        cos_az = ((math.sin(dec_rad) - math.sin(lat_rad) * math.sin(math.radians(altitude))) /
                 (math.cos(lat_rad) * math.cos(math.radians(altitude))))
        cos_az = max(-1, min(1, cos_az))  # Clamp to valid range
        
        azimuth = math.degrees(math.acos(cos_az))
        if math.sin(ha) > 0:
            azimuth = 360 - azimuth
        
        return altitude, azimuth
    
    @staticmethod
    def calculate_airmass(altitude: float) -> float:
        """Calculate airmass from altitude."""
        if altitude <= 0:
            return 999.0
        
        # Simple secant formula (good enough for altitudes > 20 degrees)
        alt_rad = math.radians(altitude)
        return 1.0 / math.sin(alt_rad)


class TargetSelector:
    """Main target selection class."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.calc = AstronomicalCalculations()
    
    def get_all_targets(self) -> pd.DataFrame:
        """Get all targets from the database."""
        try:
            # Get table information
            table_info = self.db_manager.get_table_info()
            
            if not table_info:
                self.logger.warning("No tables found in database")
                return pd.DataFrame()
            
            # Find the main targets table
            main_table = self._find_main_table(table_info.keys())
            
            if not main_table:
                self.logger.warning("No suitable targets table found")
                return pd.DataFrame()
            
            # Load all targets
            query = f"SELECT * FROM {main_table}"
            targets = self.db_manager.execute_query(query)
            
            return targets
            
        except Exception as e:
            self.logger.error(f"Error loading targets: {e}")
            return pd.DataFrame()
    
    def _find_main_table(self, table_names: List[str]) -> Optional[str]:
        """Find the main targets table from available tables."""
        # Look for tables with target-related keywords
        keywords = ['target', 'object', 'deep', 'sky', 'catalog', 'messier', 'ngc']
        
        for table in table_names:
            table_lower = table.lower()
            if any(keyword in table_lower for keyword in keywords):
                return table
        
        # If no specific table found, return the first one
        return table_names[0] if table_names else None
    
    def select_targets_for_session(self, 
                                 location: ObservingLocation,
                                 conditions: ObservingConditions,
                                 target_count: int = 10) -> List[Dict]:
        """
        Select optimal targets for an observing session.
        
        Args:
            location: Observer location
            conditions: Observing conditions and constraints
            target_count: Number of targets to return
            
        Returns:
            List of target dictionaries with scores and observability info
        """
        try:
            # Load all targets
            all_targets = self.get_all_targets()
            
            if all_targets.empty:
                self.logger.warning("No targets available")
                return []
            
            # Calculate observability for each target
            scored_targets = []
            
            for idx, target_row in all_targets.iterrows():
                target_info = self._row_to_target_info(target_row)
                if target_info:
                    score_info = self._calculate_target_score(
                        target_info, location, conditions
                    )
                    if score_info and score_info['observable']:
                        scored_targets.append({
                            'target': target_info,
                            'score_info': score_info,
                            'original_data': target_row.to_dict()
                        })
            
            # Sort by score (descending)
            scored_targets.sort(key=lambda x: x['score_info']['total_score'], reverse=True)
            
            # Return top targets
            return scored_targets[:target_count]
            
        except Exception as e:
            self.logger.error(f"Error selecting targets: {e}")
            return []
    
    def _row_to_target_info(self, row: pd.Series) -> Optional[TargetInfo]:
        """Convert database row to TargetInfo object."""
        try:
            # Map common column names
            name = self._get_column_value(row, ['name', 'object', 'designation', 'id'])
            ra_str = self._get_column_value(row, ['ra', 'right_ascension', 'alpha'])
            dec_str = self._get_column_value(row, ['dec', 'declination', 'delta'])
            magnitude = self._get_column_value(row, ['magnitude', 'mag', 'v_mag', 'visual_magnitude'])
            obj_type = self._get_column_value(row, ['type', 'object_type', 'class'])
            constellation = self._get_column_value(row, ['constellation', 'const', 'con'])
            
            if not all([name, ra_str, dec_str]):
                return None
            
            # Convert coordinates
            ra_deg, dec_deg = self.calc.ra_dec_to_degrees(ra_str, dec_str)
            
            # Handle magnitude
            try:
                mag = float(magnitude) if magnitude and str(magnitude).strip() else 99.0
            except (ValueError, TypeError):
                mag = 99.0
            
            return TargetInfo(
                name=str(name),
                ra=ra_deg,
                dec=dec_deg,
                magnitude=mag,
                object_type=str(obj_type) if obj_type else "Unknown",
                constellation=str(constellation) if constellation else "Unknown"
            )
            
        except Exception as e:
            self.logger.debug(f"Error converting row to target info: {e}")
            return None
    
    def _get_column_value(self, row: pd.Series, possible_columns: List[str]):
        """Get value from row using possible column names."""
        for col in possible_columns:
            # Try exact match
            if col in row.index and pd.notna(row[col]):
                return row[col]
            
            # Try case-insensitive match
            for actual_col in row.index:
                if col.lower() == actual_col.lower() and pd.notna(row[actual_col]):
                    return row[actual_col]
            
            # Try partial match
            for actual_col in row.index:
                if col.lower() in actual_col.lower() and pd.notna(row[actual_col]):
                    return row[actual_col]
        
        return None
    
    def _calculate_target_score(self, target: TargetInfo, location: ObservingLocation, 
                              conditions: ObservingConditions) -> Optional[Dict]:
        """Calculate observability score for a target."""
        try:
            # Calculate position at middle of observing window
            mid_time = conditions.start_time + (conditions.end_time - conditions.start_time) / 2
            
            # Local sidereal time
            lst = self.calc.calculate_local_sidereal_time(location.longitude, mid_time)
            
            # Altitude and azimuth
            altitude, azimuth = self.calc.calculate_altitude_azimuth(
                target.ra, target.dec, lst, location.latitude
            )
            
            # Check if observable
            observable = (
                altitude >= conditions.min_altitude and
                target.magnitude <= conditions.max_magnitude
            )
            
            if not observable:
                return None
            
            # Calculate airmass
            airmass = self.calc.calculate_airmass(altitude)
            
            # Scoring components
            altitude_score = min(90, altitude) / 90.0  # 0-1, higher is better
            magnitude_score = max(0, (conditions.max_magnitude - target.magnitude) / conditions.max_magnitude)
            airmass_score = max(0, (3.0 - airmass) / 2.0)  # Best at airmass 1, poor above 3
            
            # Object type bonus (customize as needed)
            type_bonus = self._get_type_bonus(target.object_type)
            
            # Total score
            total_score = (
                altitude_score * 0.3 +
                magnitude_score * 0.3 +
                airmass_score * 0.3 +
                type_bonus * 0.1
            )
            
            return {
                'observable': True,
                'altitude': altitude,
                'azimuth': azimuth,
                'airmass': airmass,
                'altitude_score': altitude_score,
                'magnitude_score': magnitude_score,
                'airmass_score': airmass_score,
                'type_bonus': type_bonus,
                'total_score': total_score
            }
            
        except Exception as e:
            self.logger.debug(f"Error calculating score for {target.name}: {e}")
            return None
    
    def _get_type_bonus(self, object_type: str) -> float:
        """Get scoring bonus based on object type."""
        type_str = str(object_type).lower()
        
        # Scoring preferences (customize as needed)
        if any(keyword in type_str for keyword in ['galaxy', 'gxy']):
            return 0.8
        elif any(keyword in type_str for keyword in ['nebula', 'neb']):
            return 0.9
        elif any(keyword in type_str for keyword in ['cluster', 'cl']):
            return 0.7
        elif any(keyword in type_str for keyword in ['planetary', 'pn']):
            return 0.6
        else:
            return 0.5
    
    def get_targets_by_constellation(self, constellation: str) -> pd.DataFrame:
        """Get all targets in a specific constellation."""
        try:
            all_targets = self.get_all_targets()
            
            if all_targets.empty:
                return pd.DataFrame()
            
            # Find constellation column
            const_columns = [col for col in all_targets.columns if 'const' in col.lower()]
            
            if not const_columns:
                return pd.DataFrame()
            
            # Filter by constellation
            const_col = const_columns[0]
            filtered = all_targets[
                all_targets[const_col].str.lower() == constellation.lower()
            ]
            
            return filtered
            
        except Exception as e:
            self.logger.error(f"Error filtering by constellation: {e}")
            return pd.DataFrame()
    
    def search_targets(self, 
                      name_pattern: str = None,
                      object_type: str = None,
                      max_magnitude: float = None,
                      constellation: str = None) -> pd.DataFrame:
        """Search targets with various criteria."""
        try:
            all_targets = self.get_all_targets()
            
            if all_targets.empty:
                return pd.DataFrame()
            
            result = all_targets.copy()
            
            # Name search
            if name_pattern:
                name_columns = [col for col in result.columns if 'name' in col.lower() or 'object' in col.lower()]
                if name_columns:
                    name_col = name_columns[0]
                    result = result[
                        result[name_col].str.contains(name_pattern, case=False, na=False)
                    ]
            
            # Type filter
            if object_type:
                type_columns = [col for col in result.columns if 'type' in col.lower()]
                if type_columns:
                    type_col = type_columns[0]
                    result = result[
                        result[type_col].str.contains(object_type, case=False, na=False)
                    ]
            
            # Magnitude filter
            if max_magnitude:
                mag_columns = [col for col in result.columns if 'mag' in col.lower()]
                if mag_columns:
                    mag_col = mag_columns[0]
                    result = result[
                        pd.to_numeric(result[mag_col], errors='coerce') <= max_magnitude
                    ]
            
            # Constellation filter
            if constellation:
                const_columns = [col for col in result.columns if 'const' in col.lower()]
                if const_columns:
                    const_col = const_columns[0]
                    result = result[
                        result[const_col].str.lower() == constellation.lower()
                    ]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error searching targets: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    # Test the target selector
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.utils.logger import setup_logging
    
    setup_logging()
    
    # Create test instances
    db_manager = DatabaseManager()
    selector = TargetSelector(db_manager)
    
    if not db_manager.database_exists():
        print("Database not found. Please initialize it first.")
        sys.exit(1)
    
    # Test basic functionality
    targets = selector.get_all_targets()
    print(f"Found {len(targets)} targets in database")
    
    if not targets.empty:
        print("\nFirst few targets:")
        print(targets.head())
        
        # Test search
        search_results = selector.search_targets(max_magnitude=10.0)
        print(f"\nTargets with magnitude <= 10.0: {len(search_results)}")
    
    print("\nTarget selector test completed.")