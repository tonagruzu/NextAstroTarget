# Changelog

All notable changes to NextAstroTarget will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Observatory location management
- Weather integration and cloud cover data
- Imaging session planning and scheduling
- Equipment compatibility checking
- Web-based interface

## [1.1.0] - 2025-11-01

### Added - Enhanced User Interface Implementation
- **Comprehensive UI Overhaul** per UserInterface.md specifications
  - 10 specialized interface sections matching professional astronomy software
  - Enhanced main window with timing/location, sun/moon data, and filtering controls
  - Professional spreadsheet-like object data display

- **Real-time Astronomical Calculations**
  - Accurate sun/moon position calculations with proper astronomical algorithms
  - Moon phase calculations with graphical display
  - Real-time altitude tracking over 6-hour periods
  - Transit time calculations for all objects
  - Moon separation calculations for imaging planning

- **Advanced Filtering System**
  - Declination range filtering with min/max controls
  - Size range filtering for object dimensions
  - Rating-based filtering (5-star to 3-star targets)
  - Catalog filtering (Messier, NGC, IC, etc.)
  - Object type filtering (Galaxies, Nebulae, Clusters, Planetary Nebulae)
  - Color-coded filter buttons matching UI specifications

- **Interactive Time Controls**
  - Date/time spinboxes with month, day, year, hour, minute controls
  - "Now" button for current time selection
  - "Sunset" button for automatic sunset time calculation
  - GMT offset and DST handling
  - Observatory location input (latitude, longitude, elevation)

- **Enhanced Object Data Display**
  - 20+ columns of comprehensive object information
  - Real-time calculated columns (altitude, transit, moon data)
  - Context menus with object details, coordinate copying
  - Sortable columns by name, altitude, magnitude, rating
  - Object detail popups with full astronomical information

- **Database Integration Improvements**
  - Successfully processed 3,134 objects from Imm Deep Sky Compendium
  - Intelligent Excel structure mapping to database columns
  - Header row filtering and data validation
  - Cross-referenced catalog support (Messier, NGC, IC designations)

### Technical Enhancements
- **New Core Components**
  - `astronomical_calculations.py`: Professional-grade astronomical algorithms
  - `enhanced_main_window.py`: Comprehensive UI matching specifications
  - `enhanced_target_selection_gui.py`: Advanced object browser with real-time data
  
- **Performance Optimizations**
  - Background thread for real-time calculations
  - Efficient data filtering and display updates
  - Proper pandas DataFrame handling for large datasets
  - Memory-efficient coordinate conversion algorithms

### User Experience Improvements
- **Professional Interface Design**
  - Multiple tabbed sections with labeled frames
  - Color-coded controls (blue filters, green size, red ratings)
  - Responsive scrollable interface handling thousands of objects
  - Consistent styling matching astronomy software standards

- **Interactive Features**
  - Double-click for object details
  - Right-click context menus
  - Coordinate copying to clipboard
  - Alphabetical and transit time sorting options
  - Real-time status updates and progress indicators

## [1.0.0] - 2025-11-01

### Added
- Initial release of NextAstroTarget astrophotography target selection application
- **Database Management**
  - Excel file import with automatic SQLite conversion
  - Progress tracking during database initialization
  - Robust error handling for malformed data
  - Column name sanitization for SQL compatibility
  - Automatic index creation for better performance

- **Target Selection Interface**
  - Advanced search and filtering by name, type, constellation, magnitude
  - Random target discovery feature
  - Tabbed interface for search, browse, and database info
  - Real-time target details display
  - Search results with sortable columns

- **Astronomical Calculations**
  - Coordinate conversion (RA/Dec string formats to decimal degrees)
  - Local sidereal time calculations
  - Altitude and azimuth calculations
  - Airmass calculations
  - Target visibility scoring algorithms

- **User Interface**
  - Clean, modern tkinter-based GUI
  - Smart application flow (database check → init or target selection)
  - Progress bars with real-time status updates
  - Error dialogs with user-friendly messages
  - Navigation menu between different screens

- **Installation & Setup**
  - Windows batch installer (`install.bat`)
  - PowerShell installer (`install.ps1`) with enhanced features
  - Automated desktop shortcut creation
  - Start Menu integration
  - Uninstaller script
  - Dependency management via requirements.txt

- **Architecture & Quality**
  - Modular package structure for easy maintenance
  - Comprehensive logging system with rotation
  - Custom exception classes for different error types
  - Configuration management via INI files
  - Thread-safe database operations
  - Graceful error recovery

- **Documentation**
  - Complete README with installation and usage guides
  - Contributing guidelines for developers
  - GitHub issue templates for bugs and features
  - MIT license
  - Code documentation with docstrings

- **Development Support**
  - Git repository with proper .gitignore
  - GitHub integration ready
  - Version tagging system
  - Release preparation scripts

### Technical Details
- **Platform**: Windows 10/11 (64-bit recommended)
- **Python**: 3.8+ required
- **Dependencies**: pandas, openpyxl, Pillow, requests, astropy (optional)
- **Database**: SQLite for local storage
- **GUI Framework**: tkinter (built-in)
- **Architecture**: Modular MVC-style design

### Known Issues
- None reported in initial release

### Migration Notes
- This is the initial release, no migration required

---

## Version History Summary

- **v1.0.0**: Initial release with full astrophotography target selection functionality
- **Future**: Enhanced features and web interface planned

## Support

For issues, feature requests, or contributions:
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/NextAstroTarget/issues)
- **Discussions**: [Ask questions or discuss ideas](https://github.com/yourusername/NextAstroTarget/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines