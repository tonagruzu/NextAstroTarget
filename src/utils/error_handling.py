"""
Error handling and exception utilities for NextAstroTarget application.
Provides custom exceptions and error handling decorators.
"""

import functools
import traceback
import logging
from typing import Any, Callable, Optional, Type
import tkinter as tk
from tkinter import messagebox


class NextAstroTargetError(Exception):
    """Base exception class for NextAstroTarget application."""
    pass


class DatabaseError(NextAstroTargetError):
    """Exceptions related to database operations."""
    pass


class DataValidationError(NextAstroTargetError):
    """Exceptions related to data validation."""
    pass


class ConfigurationError(NextAstroTargetError):
    """Exceptions related to configuration issues."""
    pass


class GUIError(NextAstroTargetError):
    """Exceptions related to GUI operations."""
    pass


class CalculationError(NextAstroTargetError):
    """Exceptions related to astronomical calculations."""
    pass


def handle_exceptions(
    show_user_message: bool = True,
    user_message: str = None,
    return_value: Any = None,
    log_level: str = "error"
):
    """
    Decorator for handling exceptions in methods and functions.
    
    Args:
        show_user_message: Whether to show error message to user
        user_message: Custom message to show user (None for auto message)
        return_value: Value to return on exception
        log_level: Logging level for the exception
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(func.__module__)
                
                # Log the exception
                log_method = getattr(logger, log_level.lower(), logger.error)
                log_method(f"Exception in {func.__name__}: {e}")
                log_method(f"Traceback: {traceback.format_exc()}")
                
                # Show user message if requested
                if show_user_message:
                    message = user_message or f"An error occurred in {func.__name__}: {str(e)}"
                    try:
                        messagebox.showerror("Error", message)
                    except tk.TclError:
                        # GUI might not be available
                        print(f"Error: {message}")
                
                return return_value
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    default_return=None,
    error_message: str = None,
    show_error: bool = False
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        args: Arguments for the function
        kwargs: Keyword arguments for the function
        default_return: Value to return on error
        error_message: Custom error message
        show_error: Whether to show error dialog
        
    Returns:
        Function result or default_return on error
    """
    if kwargs is None:
        kwargs = {}
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Safe execution failed for {func.__name__}: {e}")
        
        if show_error:
            message = error_message or f"Error executing {func.__name__}: {str(e)}"
            try:
                messagebox.showerror("Execution Error", message)
            except tk.TclError:
                print(f"Error: {message}")
        
        return default_return


class ErrorReporter:
    """Centralized error reporting and handling."""
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
    
    def report_error(self, 
                    error: Exception,
                    context: str = "",
                    show_user: bool = True,
                    user_message: str = None) -> None:
        """
        Report an error with logging and optional user notification.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            show_user: Whether to show message to user
            user_message: Custom message for user
        """
        # Log the error
        error_msg = f"{context}: {error}" if context else str(error)
        self.logger.error(error_msg)
        self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Show user message if requested
        if show_user:
            message = user_message or f"An error occurred: {str(error)}"
            if context:
                message = f"{context}: {message}"
            
            try:
                messagebox.showerror("Error", message)
            except tk.TclError:
                print(f"Error: {message}")
    
    def report_warning(self, 
                      message: str,
                      context: str = "",
                      show_user: bool = False) -> None:
        """
        Report a warning.
        
        Args:
            message: Warning message
            context: Additional context
            show_user: Whether to show warning to user
        """
        warning_msg = f"{context}: {message}" if context else message
        self.logger.warning(warning_msg)
        
        if show_user:
            try:
                messagebox.showwarning("Warning", warning_msg)
            except tk.TclError:
                print(f"Warning: {warning_msg}")
    
    def report_info(self, 
                   message: str,
                   context: str = "",
                   show_user: bool = False) -> None:
        """
        Report an informational message.
        
        Args:
            message: Info message
            context: Additional context
            show_user: Whether to show info to user
        """
        info_msg = f"{context}: {message}" if context else message
        self.logger.info(info_msg)
        
        if show_user:
            try:
                messagebox.showinfo("Information", info_msg)
            except tk.TclError:
                print(f"Info: {info_msg}")


class ValidationError(Exception):
    """Exception for validation errors."""
    pass


def validate_coordinates(ra: Any, dec: Any) -> tuple[float, float]:
    """
    Validate and convert coordinates to decimal degrees.
    
    Args:
        ra: Right ascension (various formats)
        dec: Declination (various formats)
        
    Returns:
        Tuple of (ra_degrees, dec_degrees)
        
    Raises:
        ValidationError: If coordinates are invalid
    """
    try:
        # Handle string coordinates
        if isinstance(ra, str) and ':' in ra:
            parts = ra.split(':')
            ra_hours = float(parts[0]) + float(parts[1])/60.0
            if len(parts) > 2:
                ra_hours += float(parts[2])/3600.0
            ra_deg = ra_hours * 15.0
        else:
            ra_val = float(ra)
            ra_deg = ra_val * 15.0 if ra_val <= 24 else ra_val
        
        if isinstance(dec, str) and ':' in dec:
            parts = dec.split(':')
            sign = -1 if parts[0].startswith('-') else 1
            dec_deg = abs(float(parts[0])) + float(parts[1])/60.0
            if len(parts) > 2:
                dec_deg += float(parts[2])/3600.0
            dec_deg *= sign
        else:
            dec_deg = float(dec)
        
        # Validate ranges
        if not (0 <= ra_deg < 360):
            raise ValidationError(f"RA out of range: {ra_deg}")
        
        if not (-90 <= dec_deg <= 90):
            raise ValidationError(f"Dec out of range: {dec_deg}")
        
        return ra_deg, dec_deg
        
    except (ValueError, IndexError) as e:
        raise ValidationError(f"Invalid coordinates: {ra}, {dec} - {e}")


def validate_magnitude(magnitude: Any) -> float:
    """
    Validate magnitude value.
    
    Args:
        magnitude: Magnitude value to validate
        
    Returns:
        Valid magnitude as float
        
    Raises:
        ValidationError: If magnitude is invalid
    """
    try:
        mag = float(magnitude)
        if not (-30 <= mag <= 50):  # Reasonable range
            raise ValidationError(f"Magnitude out of reasonable range: {mag}")
        return mag
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid magnitude: {magnitude} - {e}")


def validate_location(latitude: Any, longitude: Any) -> tuple[float, float]:
    """
    Validate observer location coordinates.
    
    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        
    Returns:
        Tuple of (latitude, longitude)
        
    Raises:
        ValidationError: If coordinates are invalid
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if not (-90 <= lat <= 90):
            raise ValidationError(f"Latitude out of range: {lat}")
        
        if not (-180 <= lon <= 180):
            raise ValidationError(f"Longitude out of range: {lon}")
        
        return lat, lon
        
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid location: {latitude}, {longitude} - {e}")


class RobustDataLoader:
    """Robust data loading with error handling and fallbacks."""
    
    def __init__(self, error_reporter: Optional[ErrorReporter] = None):
        self.error_reporter = error_reporter or ErrorReporter()
    
    def load_excel_safely(self, filename: str) -> Optional[dict]:
        """
        Safely load Excel file with error handling.
        
        Args:
            filename: Path to Excel file
            
        Returns:
            Dictionary of sheet data or None on error
        """
        try:
            import pandas as pd
            
            # Try to read the file
            data = pd.read_excel(filename, sheet_name=None, engine='openpyxl')
            self.error_reporter.report_info(f"Successfully loaded Excel file: {filename}")
            return data
            
        except FileNotFoundError:
            self.error_reporter.report_error(
                FileNotFoundError(f"Excel file not found: {filename}"),
                "Excel Load Error",
                show_user=True,
                user_message="The Excel file could not be found. Please check the file path."
            )
            return None
        
        except PermissionError:
            self.error_reporter.report_error(
                PermissionError(f"No permission to read file: {filename}"),
                "Excel Load Error",
                show_user=True,
                user_message="Permission denied. Please check file permissions and close Excel if it's open."
            )
            return None
        
        except Exception as e:
            self.error_reporter.report_error(
                e,
                "Excel Load Error",
                show_user=True,
                user_message="Failed to load Excel file. Please check the file format."
            )
            return None
    
    def clean_dataframe(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """
        Clean DataFrame with robust error handling.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            # Remove empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Clean column names
            df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
            
            # Remove duplicate columns
            df = df.loc[:, ~df.columns.duplicated()]
            
            return df
            
        except Exception as e:
            self.error_reporter.report_warning(
                f"Error cleaning DataFrame: {e}",
                "Data Cleaning"
            )
            return df  # Return original if cleaning fails


# Global error reporter instance
global_error_reporter = ErrorReporter()


if __name__ == "__main__":
    # Test error handling
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.utils.logger import setup_logging
    
    setup_logging()
    
    # Test validation functions
    try:
        ra, dec = validate_coordinates("12:34:56", "+45:30:00")
        print(f"Coordinates: RA={ra:.2f}°, Dec={dec:.2f}°")
    except ValidationError as e:
        print(f"Validation error: {e}")
    
    # Test error reporter
    reporter = ErrorReporter()
    reporter.report_info("Test info message")
    reporter.report_warning("Test warning message")
    
    print("Error handling test completed.")