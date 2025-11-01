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