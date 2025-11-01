# NextAstroTarget 🔭

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

**NextAstroTarget** is a comprehensive Python application designed to help astronomers and astrophotographers select optimal targets for their imaging sessions. The application intelligently processes astronomical databases and provides recommendations based on observing conditions, target visibility, and user preferences.

## 🌟 Features

- **🗄️ Database Management**: Automatically imports and processes Excel-based astronomical catalogs
- **🔍 Smart Target Search**: Advanced filtering by object type, magnitude, constellation, and coordinates  
- **📊 Target Optimization**: Calculates visibility, altitude, and optimal observing times
- **🎯 Random Discovery**: Discover new targets with the random selection feature
- **📈 Progress Tracking**: Real-time feedback during database initialization
- **🖥️ User-friendly GUI**: Clean, intuitive interface built with tkinter
- **📝 Comprehensive Logging**: Detailed application logs for troubleshooting
- **⚙️ Modular Architecture**: Easily extensible for future enhancements

## 🚀 Quick Start

### System Requirements

#### Operating System
- Windows 10 or Windows 11 (64-bit recommended)

#### Software Requirements
- Python 3.8 or higher
- Minimum 4GB RAM
- 1GB free disk space
- Internet connection for initial setup

### 📦 Installation

#### Method 1: Automated Installation (Recommended)

1. **Download the application**
   - Extract all files to a directory (e.g., `C:\NextAstroTarget\`)

2. **Run the installer**
   - Double-click `install.bat` in the application directory
   - The installer will:
     - Check Python installation
     - Install required packages
     - Create desktop shortcut
     - Set up configuration files

3. **Launch the application**
   - Use the desktop shortcut "NextAstroTarget"
   - Or run `main.py` from the application directory

#### Method 2: Manual Installation

1. **Verify Python Installation**
   ```powershell
   python --version
   ```
   If Python is not installed, download from [python.org](https://www.python.org/downloads/)

2. **Install Required Packages**
   ```powershell
   cd C:\NextAstroTarget
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```powershell
   python main.py
   ```

### 🎯 First-Time Setup

### 1. Database Initialization
- On first launch, the application will show the "Database Initialization" screen
- Ensure the Excel file `Imm Deep Sky Compendium - 2023 - rev4g.xlsm` is in the application directory
- Click "Initialize Database" to process the astronomical data
- This process may take several minutes depending on data size

### 2. Application Configuration
- The application uses `config/config.ini` for configuration
- Default settings work for most users
- Advanced users can modify settings as needed

## Troubleshooting

### Common Issues

**Python Not Found**
- Install Python from python.org
- Ensure Python is added to system PATH during installation

**Permission Errors**
- Run installer as Administrator
- Ensure antivirus software isn't blocking the application

**Missing Excel File**
- Ensure `Imm Deep Sky Compendium - 2023 - rev4g.xlsm` is in the application directory
- Check file is not corrupted or password-protected

**Database Initialization Fails**
- Check Windows Event Viewer for detailed error messages
- Verify Excel file format and content
- Ensure sufficient disk space

### Getting Help

**Log Files**
- Check `logs/nextastrotarget.log` for detailed error information
- Enable debug mode in `config/config.ini` for verbose logging

**Support**
- Create an issue in the project repository
- Include log files and error messages
- Specify your operating system and Python version

## Uninstallation

### Remove Application
1. Delete the application directory
2. Remove desktop shortcut
3. Remove entries from Start Menu (if applicable)

### Clean Removal
- Application data is stored locally in the application directory
- No registry modifications are made
- No system files are modified

## Advanced Configuration

### Custom Data Sources
- Place additional Excel files in the application directory
- Modify `config/config.ini` to specify alternate data sources
- Restart application to reload configuration

### Network Configuration
- Application may access external APIs for additional data
- Configure firewall to allow outbound HTTPS connections
- Proxy settings can be configured in `config/config.ini`

### Performance Tuning
- Increase logging level to reduce I/O overhead
- Configure database cache size in configuration
- Use SSD storage for better database performance

## File Structure
```
NextAstroTarget/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── install.bat               # Windows installer
├── README.md                 # This file
├── config/
│   └── config.ini           # Configuration file
├── data/                    # Database storage
├── logs/                    # Application logs
├── src/                     # Source code
│   ├── database/           # Database modules
│   ├── gui/                # GUI components
│   ├── target_selection/   # Target selection logic
│   └── utils/              # Utility modules
└── Imm Deep Sky Compendium - 2023 - rev4g.xlsm  # Source data
```

## License and Attribution
This application uses open-source libraries and astronomical data:
- pandas: Data manipulation
- tkinter: GUI framework
- sqlite3: Database engine
- openpyxl: Excel file handling
- Astronomical data: Various catalogs and sources

## 📸 Screenshots

![Database Initialization](docs/images/db_init_screen.png)
*Database initialization with progress tracking*

![Target Selection](docs/images/target_selection_screen.png)
*Advanced target search and filtering interface*

![Target Details](docs/images/target_details_screen.png)
*Detailed target information and observability data*

## 🏗️ Architecture

NextAstroTarget follows a modular architecture design:

```
NextAstroTarget/
├── src/
│   ├── database/          # Database management and Excel processing
│   ├── gui/              # User interface components  
│   ├── target_selection/ # Target optimization algorithms
│   └── utils/            # Logging, error handling, utilities
├── config/               # Configuration files
├── data/                 # SQLite database storage
├── logs/                 # Application logs
└── assets/               # Icons and resources
```

## 🤝 Contributing

We welcome contributions to NextAstroTarget! Here's how you can help:

### Development Setup

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/NextAstroTarget.git
   cd NextAstroTarget
   ```

3. **Set up development environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Make your changes and test thoroughly**

6. **Submit a pull request**

### Coding Standards

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include unit tests for new features
- Update documentation as needed

## 🐛 Bug Reports & Feature Requests

Please use GitHub Issues to report bugs or request features:

- **🐛 Bug Report**: [Create Bug Report](https://github.com/yourusername/NextAstroTarget/issues/new?template=bug_report.md)
- **✨ Feature Request**: [Request Feature](https://github.com/yourusername/NextAstroTarget/issues/new?template=feature_request.md)

## 📚 Documentation

- **[Installation Guide](README.md#installation)**: Complete setup instructions
- **[User Manual](docs/user_manual.md)**: Detailed usage guide
- **[Developer Guide](docs/developer_guide.md)**: API documentation and development setup
- **[Configuration Reference](docs/configuration.md)**: Configuration options and customization

## 🔄 Changelog

### Version 1.0.0 (November 2025)
- Initial release
- Database initialization from Excel files
- Target search and filtering
- GUI interface with progress tracking
- Astronomical calculations for target optimization
- Windows desktop integration

## 🗺️ Roadmap

- [ ] **v1.1.0**: Observatory location management
- [ ] **v1.2.0**: Weather integration and cloud cover data
- [ ] **v1.3.0**: Imaging session planning and scheduling
- [ ] **v1.4.0**: Equipment compatibility checking
- [ ] **v2.0.0**: Web-based interface and mobile support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Astronomical Data**: Various astronomical catalogs and databases
- **Python Libraries**: pandas, tkinter, sqlite3, openpyxl
- **Community**: Thanks to the astronomy and astrophotography communities for inspiration

## 📞 Support

- **📧 Email**: support@nextastrotarget.com
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/NextAstroTarget/discussions)
- **📖 Wiki**: [Project Wiki](https://github.com/yourusername/NextAstroTarget/wiki)

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/NextAstroTarget&type=Date)](https://star-history.com/#yourusername/NextAstroTarget&Date)

---

**Made with ❤️ for the astronomy community**

## Version Information
- **Version**: 1.0.0
- **Release Date**: November 2025
- **Minimum Python**: 3.8+
- **Tested Platforms**: Windows 10, Windows 11